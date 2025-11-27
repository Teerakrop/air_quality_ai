"""
Prediction System for Air Quality Forecasting
Handles 1-3 hour predictions and accuracy tracking
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import schedule
import time
import threading

from data_logger import DataLogger, PredictionLogger
from ml_models import ModelManager
import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class PredictionSystem:
    """
    Main prediction system that handles forecasting and accuracy tracking
    """
    def __init__(self):
        self.data_logger = DataLogger()
        self.prediction_logger = PredictionLogger()
        self.model_manager = ModelManager()
        self.is_running = False
        self.prediction_thread = None
        
        # Prediction horizons in minutes (converted from config hours)
        self.horizons_minutes = [h * 5 for h in config.PREDICTION_HORIZONS]  # Convert to 5-minute intervals
        self.horizons_hours = [h * 5 / 60 for h in config.PREDICTION_HORIZONS]  # Convert to hours
        
        # Load existing model if available
        self.model_manager.load_model()
    
    def start_prediction_service(self):
        """
        Start the prediction service in a separate thread
        """
        if self.is_running:
            logger.warning("Prediction service is already running")
            return
        
        self.is_running = True
        
        # Schedule predictions every 5 minutes
        schedule.every(5).minutes.do(self._make_predictions)
        
        # Schedule model retraining
        schedule.every(config.RETRAIN_INTERVAL_HOURS).hours.do(self._retrain_model)
        
        # Schedule accuracy evaluation
        schedule.every(1).hours.do(self._evaluate_accuracy)
        
        # Start scheduler thread
        self.prediction_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.prediction_thread.start()
        
        logger.info("Prediction service started")
    
    def stop_prediction_service(self):
        """
        Stop the prediction service
        """
        self.is_running = False
        schedule.clear()
        
        if self.prediction_thread:
            self.prediction_thread.join(timeout=5)
        
        logger.info("Prediction service stopped")
    
    def _run_scheduler(self):
        """
        Run the scheduler in a loop
        """
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _make_predictions(self):
        """
        Make predictions for all horizons
        """
        try:
            logger.info("Making predictions...")
            
            # Get recent data for prediction
            recent_data = self.data_logger.get_latest_data(n_rows=config.SEQUENCE_LENGTH + 50)
            
            if recent_data is None or len(recent_data) < config.SEQUENCE_LENGTH:
                logger.warning("Not enough data for predictions")
                return
            
            current_time = datetime.now()
            
            # Make predictions for each horizon
            for i, (horizon_minutes, horizon_hours) in enumerate(zip(self.horizons_minutes, self.horizons_hours)):
                prediction = self.model_manager.predict(recent_data, horizon_steps=horizon_minutes)
                
                if prediction is not None:
                    # Create prediction record
                    prediction_data = {
                        'timestamp': current_time.isoformat(),
                        'prediction_time': (current_time + timedelta(hours=horizon_hours)).isoformat(),
                        'horizon_hours': horizon_hours,
                        'model_type': self.model_manager.current_model_type,
                        'predicted_pm25': float(prediction[0]),
                        'predicted_pm10': float(prediction[1]),
                        'predicted_temp': float(prediction[2]),
                        'predicted_humidity': float(prediction[3]),
                        'actual_pm25': None,  # Will be filled later
                        'actual_pm10': None,
                        'actual_temp': None,
                        'actual_humidity': None
                    }
                    
                    # Log prediction
                    self.prediction_logger.log_prediction(prediction_data)
                    logger.debug(f"Prediction logged for {horizon_hours}h horizon")
                
                else:
                    logger.warning(f"Failed to make prediction for {horizon_hours}h horizon")
        
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
    
    def _retrain_model(self):
        """
        Retrain the model with latest data
        """
        try:
            logger.info("Retraining model...")
            
            # Get all available data
            all_data = self.data_logger.get_latest_data(n_rows=50000)  # Get large amount of recent data
            
            if all_data is None or len(all_data) < 100:
                logger.warning("Not enough data for retraining")
                return
            
            # Train model
            results = self.model_manager.train_model(all_data)
            logger.info(f"Model retrained: {results}")
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
    
    def _evaluate_accuracy(self):
        """
        Evaluate prediction accuracy by comparing with actual values
        """
        try:
            logger.info("Evaluating prediction accuracy...")
            
            # Get predictions that should have actual values by now
            predictions_df = pd.read_csv(config.PREDICTIONS_FILE)
            
            if predictions_df.empty:
                logger.info("No predictions to evaluate")
                return
            
            # Convert timestamps
            predictions_df['timestamp'] = pd.to_datetime(predictions_df['timestamp'])
            predictions_df['prediction_time'] = pd.to_datetime(predictions_df['prediction_time'])
            
            # Find predictions that need actual values
            current_time = datetime.now()
            ready_predictions = predictions_df[
                (predictions_df['prediction_time'] <= current_time) & 
                (predictions_df['actual_pm25'].isna())
            ]
            
            if ready_predictions.empty:
                logger.debug("No predictions ready for evaluation")
                return
            
            # Get actual data for comparison
            actual_data = self.data_logger.get_latest_data(n_rows=10000)
            
            if actual_data is None:
                logger.warning("No actual data available for comparison")
                return
            
            actual_data['timestamp'] = pd.to_datetime(actual_data['timestamp'])
            
            updated_predictions = []
            accuracy_metrics = {}
            
            for _, pred_row in ready_predictions.iterrows():
                # Find closest actual measurement to prediction time
                time_diff = abs(actual_data['timestamp'] - pred_row['prediction_time'])
                closest_idx = time_diff.idxmin()
                
                # Only use if within 10 minutes of prediction time
                if time_diff.loc[closest_idx] <= timedelta(minutes=10):
                    actual_row = actual_data.loc[closest_idx]
                    
                    # Update prediction with actual values
                    updated_pred = pred_row.copy()
                    updated_pred['actual_pm25'] = actual_row['pm25']
                    updated_pred['actual_pm10'] = actual_row['pm10']
                    updated_pred['actual_temp'] = actual_row['temperature']
                    updated_pred['actual_humidity'] = actual_row['humidity']
                    
                    updated_predictions.append(updated_pred)
                    
                    # Calculate accuracy metrics
                    horizon = pred_row['horizon_hours']
                    model_type = pred_row['model_type']
                    
                    key = f"{model_type}_{horizon}h"
                    if key not in accuracy_metrics:
                        accuracy_metrics[key] = {
                            'model_type': model_type,
                            'horizon_hours': horizon,
                            'mae_pm25': [],
                            'mae_pm10': [],
                            'mae_temp': [],
                            'mae_humidity': [],
                            'rmse_pm25': [],
                            'rmse_pm10': [],
                            'rmse_temp': [],
                            'rmse_humidity': []
                        }
                    
                    # Calculate errors
                    mae_pm25 = abs(pred_row['predicted_pm25'] - actual_row['pm25'])
                    mae_pm10 = abs(pred_row['predicted_pm10'] - actual_row['pm10'])
                    mae_temp = abs(pred_row['predicted_temp'] - actual_row['temperature'])
                    mae_humidity = abs(pred_row['predicted_humidity'] - actual_row['humidity'])
                    
                    accuracy_metrics[key]['mae_pm25'].append(mae_pm25)
                    accuracy_metrics[key]['mae_pm10'].append(mae_pm10)
                    accuracy_metrics[key]['mae_temp'].append(mae_temp)
                    accuracy_metrics[key]['mae_humidity'].append(mae_humidity)
                    
                    # RMSE (squared errors)
                    accuracy_metrics[key]['rmse_pm25'].append(mae_pm25 ** 2)
                    accuracy_metrics[key]['rmse_pm10'].append(mae_pm10 ** 2)
                    accuracy_metrics[key]['rmse_temp'].append(mae_temp ** 2)
                    accuracy_metrics[key]['rmse_humidity'].append(mae_humidity ** 2)
            
            # Update predictions file with actual values
            if updated_predictions:
                updated_df = pd.DataFrame(updated_predictions)
                
                # Update original dataframe
                for _, updated_row in updated_df.iterrows():
                    mask = (
                        (predictions_df['timestamp'] == updated_row['timestamp']) &
                        (predictions_df['horizon_hours'] == updated_row['horizon_hours'])
                    )
                    predictions_df.loc[mask, 'actual_pm25'] = updated_row['actual_pm25']
                    predictions_df.loc[mask, 'actual_pm10'] = updated_row['actual_pm10']
                    predictions_df.loc[mask, 'actual_temp'] = updated_row['actual_temp']
                    predictions_df.loc[mask, 'actual_humidity'] = updated_row['actual_humidity']
                
                # Save updated predictions
                predictions_df.to_csv(config.PREDICTIONS_FILE, index=False)
                logger.info(f"Updated {len(updated_predictions)} predictions with actual values")
            
            # Log accuracy metrics
            for key, metrics in accuracy_metrics.items():
                if metrics['mae_pm25']:  # Only log if we have data
                    accuracy_data = {
                        'timestamp': current_time.isoformat(),
                        'model_type': metrics['model_type'],
                        'horizon_hours': metrics['horizon_hours'],
                        'mae_pm25': np.mean(metrics['mae_pm25']),
                        'mae_pm10': np.mean(metrics['mae_pm10']),
                        'mae_temp': np.mean(metrics['mae_temp']),
                        'mae_humidity': np.mean(metrics['mae_humidity']),
                        'rmse_pm25': np.sqrt(np.mean(metrics['rmse_pm25'])),
                        'rmse_pm10': np.sqrt(np.mean(metrics['rmse_pm10'])),
                        'rmse_temp': np.sqrt(np.mean(metrics['rmse_temp'])),
                        'rmse_humidity': np.sqrt(np.mean(metrics['rmse_humidity']))
                    }
                    
                    self.prediction_logger.log_accuracy(accuracy_data)
                    logger.info(f"Accuracy logged for {key}: MAE PM2.5={accuracy_data['mae_pm25']:.2f}")
        
        except Exception as e:
            logger.error(f"Error evaluating accuracy: {e}")
    
    def get_latest_predictions(self, hours: int = 24) -> Optional[pd.DataFrame]:
        """
        Get latest predictions within specified hours
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            DataFrame with latest predictions or None
        """
        try:
            predictions_df = pd.read_csv(config.PREDICTIONS_FILE)
            
            if predictions_df.empty:
                return None
            
            # Filter by time
            predictions_df['timestamp'] = pd.to_datetime(predictions_df['timestamp'])
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_predictions = predictions_df[predictions_df['timestamp'] >= cutoff_time]
            
            return recent_predictions.sort_values('timestamp', ascending=False)
        
        except Exception as e:
            logger.error(f"Error getting latest predictions: {e}")
            return None
    
    def get_accuracy_summary(self, days: int = 7) -> Optional[Dict]:
        """
        Get accuracy summary for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with accuracy summary or None
        """
        try:
            accuracy_df = pd.read_csv(config.ACCURACY_LOG_FILE)
            
            if accuracy_df.empty:
                return None
            
            # Filter by time
            accuracy_df['timestamp'] = pd.to_datetime(accuracy_df['timestamp'])
            cutoff_time = datetime.now() - timedelta(days=days)
            
            recent_accuracy = accuracy_df[accuracy_df['timestamp'] >= cutoff_time]
            
            if recent_accuracy.empty:
                return None
            
            # Calculate summary statistics
            summary = {}
            
            for model_type in recent_accuracy['model_type'].unique():
                model_data = recent_accuracy[recent_accuracy['model_type'] == model_type]
                
                summary[model_type] = {}
                
                for horizon in model_data['horizon_hours'].unique():
                    horizon_data = model_data[model_data['horizon_hours'] == horizon]
                    
                    summary[model_type][f"{horizon}h"] = {
                        'mae_pm25': horizon_data['mae_pm25'].mean(),
                        'mae_pm10': horizon_data['mae_pm10'].mean(),
                        'mae_temp': horizon_data['mae_temp'].mean(),
                        'mae_humidity': horizon_data['mae_humidity'].mean(),
                        'rmse_pm25': horizon_data['rmse_pm25'].mean(),
                        'rmse_pm10': horizon_data['rmse_pm10'].mean(),
                        'rmse_temp': horizon_data['rmse_temp'].mean(),
                        'rmse_humidity': horizon_data['rmse_humidity'].mean(),
                        'count': len(horizon_data)
                    }
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting accuracy summary: {e}")
            return None
    
    def force_prediction(self) -> Dict:
        """
        Force a prediction run (for testing/manual trigger)
        
        Returns:
            Dictionary with prediction results
        """
        try:
            recent_data = self.data_logger.get_latest_data(n_rows=config.SEQUENCE_LENGTH + 10)
            
            if recent_data is None or len(recent_data) < config.SEQUENCE_LENGTH:
                return {'error': 'Not enough data for prediction'}
            
            predictions = {}
            
            for horizon_hours in self.horizons_hours:
                prediction = self.model_manager.predict(recent_data)
                
                if prediction is not None:
                    predictions[f"{horizon_hours}h"] = {
                        'pm25': float(prediction[0]),
                        'pm10': float(prediction[1]),
                        'temperature': float(prediction[2]),
                        'humidity': float(prediction[3]),
                        'prediction_time': (datetime.now() + timedelta(hours=horizon_hours)).isoformat(),
                        'model_type': self.model_manager.current_model_type
                    }
                else:
                    predictions[f"{horizon_hours}h"] = {'error': 'Prediction failed'}
            
            return predictions
        
        except Exception as e:
            logger.error(f"Error in force prediction: {e}")
            return {'error': str(e)}

if __name__ == "__main__":
    # Test the prediction system
    print("Testing Prediction System...")
    
    prediction_system = PredictionSystem()
    
    # Test force prediction
    print("Testing force prediction...")
    result = prediction_system.force_prediction()
    print(f"Prediction result: {result}")
    
    # Test accuracy summary
    print("Testing accuracy summary...")
    summary = prediction_system.get_accuracy_summary()
    if summary:
        print(f"Accuracy summary: {summary}")
    else:
        print("No accuracy data available")
    
    print("Prediction system test completed")
