"""
Machine Learning Models for Air Quality Prediction
Implements LSTM and RandomForest models for time-series forecasting
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import joblib
import os

# ML Libraries
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

# Deep Learning Libraries - Jetson Nano Compatible
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    
    # Jetson Nano specific TensorFlow configuration
    if hasattr(tf.config, 'experimental'):
        # Limit GPU memory growth to prevent OOM
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logger.info("GPU memory growth enabled for Jetson Nano")
            except RuntimeError as e:
                logger.warning(f"GPU configuration warning: {e}")
    
    TENSORFLOW_AVAILABLE = True
    logger.info(f"TensorFlow {tf.__version__} loaded successfully")
except ImportError as e:
    TENSORFLOW_AVAILABLE = False
    logger.warning(f"TensorFlow not available: {e}. LSTM models will not work.")

import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Data preprocessing for time-series models
    """
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_columns = ['pm25', 'pm10', 'temperature', 'humidity', 'gas_level']
        self.target_columns = ['pm25', 'pm10', 'temperature', 'humidity']
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training/prediction
        
        Args:
            df: DataFrame with sensor data
            
        Returns:
            Tuple of (features, targets) arrays
        """
        # Sort by timestamp
        df = df.sort_values('timestamp').copy()
        
        # Extract features and targets
        features = df[self.feature_columns].values
        targets = df[self.target_columns].values
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        return features_scaled, targets
    
    def create_sequences(self, features: np.ndarray, targets: np.ndarray, 
                        sequence_length: int = config.SEQUENCE_LENGTH) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time-series prediction
        
        Args:
            features: Feature array
            targets: Target array
            sequence_length: Length of input sequences
            
        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []
        
        for i in range(sequence_length, len(features)):
            X.append(features[i-sequence_length:i])
            y.append(targets[i])
        
        return np.array(X), np.array(y)
    
    def create_multi_horizon_targets(self, targets: np.ndarray, 
                                   horizons: List[int] = config.PREDICTION_HORIZONS) -> Dict[int, np.ndarray]:
        """
        Create targets for multiple prediction horizons
        
        Args:
            targets: Target array
            horizons: List of prediction horizons (in time steps)
            
        Returns:
            Dictionary mapping horizon to target arrays
        """
        horizon_targets = {}
        
        for horizon in horizons:
            y_horizon = []
            for i in range(len(targets) - horizon):
                y_horizon.append(targets[i + horizon])
            horizon_targets[horizon] = np.array(y_horizon)
        
        return horizon_targets

class LSTMModel:
    """
    LSTM model for time-series forecasting
    """
    def __init__(self, sequence_length: int = config.SEQUENCE_LENGTH, 
                 n_features: int = 5, n_targets: int = 4):
        """
        Initialize LSTM model
        
        Args:
            sequence_length: Length of input sequences
            n_features: Number of input features
            n_targets: Number of target variables
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM models")
            
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_targets = n_targets
        self.model = None
        self.is_trained = False
        
    def build_model(self):
        """
        Build LSTM model architecture
        
        Returns:
            Compiled Keras model
        """
        model = keras.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=(self.sequence_length, self.n_features)),
            layers.Dropout(0.2),
            layers.LSTM(32, return_sequences=False),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(self.n_targets)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: np.ndarray, y_val: np.ndarray, 
              epochs: int = None, batch_size: int = None) -> Dict:
        """
        Train LSTM model
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            epochs: Number of training epochs
            batch_size: Training batch size
            
        Returns:
            Training history
        """
        self.model = self.build_model()
        
        # Callbacks
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.2, patience=5, min_lr=0.001
        )
        
        # Jetson Nano optimized parameters
        if epochs is None:
            epochs = getattr(config, 'MAX_EPOCHS', 30)  # Fewer epochs for Jetson Nano
        if batch_size is None:
            batch_size = getattr(config, 'MAX_BATCH_SIZE', 16)  # Smaller batch size
        
        logger.info(f"Training with epochs={epochs}, batch_size={batch_size}")
        
        # Train model with Jetson Nano optimizations
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=1,
            use_multiprocessing=False,  # Disable multiprocessing for stability
            workers=1  # Single worker for Jetson Nano
        )
        
        self.is_trained = True
        logger.info("LSTM model training completed")
        
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with LSTM model
        
        Args:
            X: Input sequences
            
        Returns:
            Predictions array
        """
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        return self.model.predict(X)
    
    def save_model(self, filepath: str = config.LSTM_MODEL_PATH):
        """
        Save trained model
        
        Args:
            filepath: Path to save model
        """
        if self.model is not None:
            self.model.save(filepath)
            logger.info(f"LSTM model saved to {filepath}")
    
    def load_model(self, filepath: str = config.LSTM_MODEL_PATH) -> bool:
        """
        Load trained model
        
        Args:
            filepath: Path to model file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(filepath):
                self.model = keras.models.load_model(filepath)
                self.is_trained = True
                logger.info(f"LSTM model loaded from {filepath}")
                return True
            else:
                logger.warning(f"Model file not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Failed to load LSTM model: {e}")
            return False

class RandomForestModel:
    """
    Random Forest model for time-series forecasting
    """
    def __init__(self, n_estimators: int = None, max_depth: int = None):
        """
        Initialize Random Forest model
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum tree depth
        """
        # Jetson Nano optimized parameters
        self.n_estimators = n_estimators or (50 if getattr(config, 'JETSON_OPTIMIZATION', False) else 100)
        self.max_depth = max_depth or (15 if getattr(config, 'JETSON_OPTIMIZATION', False) else 20)
        self.models = {}  # One model per target variable
        self.target_columns = ['pm25', 'pm10', 'temperature', 'humidity']
        self.is_trained = False
        
    def _prepare_features(self, X: np.ndarray) -> np.ndarray:
        """
        Flatten sequences for Random Forest
        
        Args:
            X: Input sequences (3D array)
            
        Returns:
            Flattened features (2D array)
        """
        if len(X.shape) == 3:
            # Flatten sequences: (samples, timesteps, features) -> (samples, timesteps * features)
            return X.reshape(X.shape[0], -1)
        return X
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict:
        """
        Train Random Forest models
        
        Args:
            X_train: Training features
            y_train: Training targets
            
        Returns:
            Training metrics
        """
        X_train_flat = self._prepare_features(X_train)
        
        metrics = {}
        
        # Train separate model for each target variable
        for i, target in enumerate(self.target_columns):
            logger.info(f"Training Random Forest for {target}")
            
            # Jetson Nano optimization: limit CPU cores
            n_jobs = 2 if getattr(config, 'JETSON_OPTIMIZATION', False) else -1
            
            model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                random_state=42,
                n_jobs=n_jobs
            )
            
            model.fit(X_train_flat, y_train[:, i])
            self.models[target] = model
            
            # Calculate training score
            train_pred = model.predict(X_train_flat)
            mae = mean_absolute_error(y_train[:, i], train_pred)
            rmse = np.sqrt(mean_squared_error(y_train[:, i], train_pred))
            
            metrics[target] = {'mae': mae, 'rmse': rmse}
            logger.info(f"{target} - MAE: {mae:.3f}, RMSE: {rmse:.3f}")
        
        self.is_trained = True
        logger.info("Random Forest models training completed")
        
        return metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with Random Forest models
        
        Args:
            X: Input features
            
        Returns:
            Predictions array
        """
        if not self.is_trained:
            raise ValueError("Models must be trained before making predictions")
        
        X_flat = self._prepare_features(X)
        predictions = []
        
        for target in self.target_columns:
            pred = self.models[target].predict(X_flat)
            predictions.append(pred)
        
        return np.column_stack(predictions)
    
    def save_models(self, filepath: str = config.RF_MODEL_PATH):
        """
        Save trained models
        
        Args:
            filepath: Path to save models
        """
        if self.models:
            joblib.dump(self.models, filepath)
            logger.info(f"Random Forest models saved to {filepath}")
    
    def load_models(self, filepath: str = config.RF_MODEL_PATH) -> bool:
        """
        Load trained models
        
        Args:
            filepath: Path to model file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(filepath):
                self.models = joblib.load(filepath)
                self.is_trained = True
                logger.info(f"Random Forest models loaded from {filepath}")
                return True
            else:
                logger.warning(f"Model file not found: {filepath}")
                return False
        except Exception as e:
            logger.error(f"Failed to load Random Forest models: {e}")
            return False

class ModelManager:
    """
    Manager for handling model selection and training
    """
    def __init__(self):
        self.preprocessor = DataPreprocessor()
        self.lstm_model = None
        self.rf_model = None
        self.current_model_type = None
        
    def should_use_lstm(self, data_size: int) -> bool:
        """
        Determine whether to use LSTM or Random Forest based on data size
        
        Args:
            data_size: Number of data points
            
        Returns:
            True if LSTM should be used, False for Random Forest
        """
        return data_size >= config.MIN_DATA_FOR_LSTM and TENSORFLOW_AVAILABLE
    
    def train_model(self, df: pd.DataFrame) -> Dict:
        """
        Train appropriate model based on data size
        
        Args:
            df: Training data DataFrame
            
        Returns:
            Training results
        """
        logger.info(f"Training model with {len(df)} data points")
        
        # Prepare data
        features, targets = self.preprocessor.prepare_data(df)
        X, y = self.preprocessor.create_sequences(features, targets)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=1-config.TRAIN_TEST_SPLIT, random_state=42
        )
        
        # Choose model type
        use_lstm = self.should_use_lstm(len(df))
        
        if use_lstm:
            logger.info("Using LSTM model")
            self.current_model_type = 'LSTM'
            self.lstm_model = LSTMModel()
            
            # Train LSTM
            history = self.lstm_model.train(X_train, y_train, X_val, y_val)
            
            # Save model and scaler
            self.lstm_model.save_model()
            joblib.dump(self.preprocessor.scaler, config.SCALER_PATH)
            
            return {'model_type': 'LSTM', 'history': history}
        
        else:
            logger.info("Using Random Forest model")
            self.current_model_type = 'RandomForest'
            self.rf_model = RandomForestModel()
            
            # Train Random Forest
            metrics = self.rf_model.train(X_train, y_train)
            
            # Save model and scaler
            self.rf_model.save_models()
            joblib.dump(self.preprocessor.scaler, config.SCALER_PATH)
            
            return {'model_type': 'RandomForest', 'metrics': metrics}
    
    def load_model(self) -> bool:
        """
        Load the most recent trained model
        
        Returns:
            True if successful, False otherwise
        """
        # Try to load scaler first
        if os.path.exists(config.SCALER_PATH):
            self.preprocessor.scaler = joblib.load(config.SCALER_PATH)
        else:
            logger.warning("Scaler not found, using new scaler")
            return False
        
        # Try LSTM first
        if TENSORFLOW_AVAILABLE and os.path.exists(config.LSTM_MODEL_PATH):
            self.lstm_model = LSTMModel()
            if self.lstm_model.load_model():
                self.current_model_type = 'LSTM'
                logger.info("Loaded LSTM model")
                return True
        
        # Try Random Forest
        if os.path.exists(config.RF_MODEL_PATH):
            self.rf_model = RandomForestModel()
            if self.rf_model.load_models():
                self.current_model_type = 'RandomForest'
                logger.info("Loaded Random Forest model")
                return True
        
        logger.warning("No trained model found")
        return False
    
    def predict(self, recent_data: pd.DataFrame, horizon_steps: int = 12) -> Optional[np.ndarray]:
        """
        Make prediction using loaded model
        
        Args:
            recent_data: Recent sensor data for prediction
            horizon_steps: Number of steps to predict ahead
            
        Returns:
            Prediction array or None if error
        """
        try:
            if self.current_model_type is None:
                logger.error("No model loaded for prediction")
                return None
            
            # Prepare data
            features, _ = self.preprocessor.prepare_data(recent_data)
            
            # Get last sequence
            if len(features) < config.SEQUENCE_LENGTH:
                logger.error(f"Not enough data for prediction. Need {config.SEQUENCE_LENGTH}, got {len(features)}")
                return None
            
            last_sequence = features[-config.SEQUENCE_LENGTH:].reshape(1, config.SEQUENCE_LENGTH, -1)
            
            # Make prediction
            if self.current_model_type == 'LSTM' and self.lstm_model:
                prediction = self.lstm_model.predict(last_sequence)
            elif self.current_model_type == 'RandomForest' and self.rf_model:
                prediction = self.rf_model.predict(last_sequence)
            else:
                logger.error(f"Model {self.current_model_type} not available")
                return None
            
            return prediction[0]  # Return single prediction
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None

if __name__ == "__main__":
    # Test the models with sample data
    print("Testing ML Models...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='5min')
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'pm25': np.random.normal(25, 10, 1000),
        'pm10': np.random.normal(35, 15, 1000),
        'temperature': np.random.normal(25, 5, 1000),
        'humidity': np.random.normal(60, 20, 1000),
        'gas_level': np.random.normal(200, 50, 1000)
    })
    
    # Test model manager
    manager = ModelManager()
    
    print("Training model...")
    results = manager.train_model(sample_data)
    print(f"Training results: {results}")
    
    print("Testing prediction...")
    prediction = manager.predict(sample_data.tail(100))
    if prediction is not None:
        print(f"Prediction successful: {prediction}")
    else:
        print("Prediction failed")
