"""
Data Logger Module for Air Quality System
Handles CSV data storage with timestamps every 5-10 seconds
"""

import pandas as pd
import os
import logging
from datetime import datetime
from typing import Dict, Optional
import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class DataLogger:
    def __init__(self, csv_file: str = config.RAW_DATA_FILE):
        """
        Initialize data logger
        
        Args:
            csv_file: Path to CSV file for data storage
        """
        self.csv_file = csv_file
        self.columns = config.SENSOR_COLUMNS
        
        # Create CSV file with headers if it doesn't exist
        self._initialize_csv()
    
    def _initialize_csv(self):
        """
        Create CSV file with headers if it doesn't exist
        """
        if not os.path.exists(self.csv_file):
            # Create empty DataFrame with correct columns
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(self.csv_file, index=False)
            logger.info(f"Created new CSV file: {self.csv_file}")
        else:
            # Verify existing CSV has correct columns
            try:
                existing_df = pd.read_csv(self.csv_file, nrows=0)  # Read only headers
                if list(existing_df.columns) != self.columns:
                    logger.warning(f"CSV columns mismatch. Expected: {self.columns}, Found: {list(existing_df.columns)}")
            except Exception as e:
                logger.error(f"Error reading existing CSV: {e}")
    
    def log_data(self, sensor_data: Dict) -> bool:
        """
        Log sensor data to CSV file
        
        Args:
            sensor_data: Dictionary containing sensor readings
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate data structure
            if not self._validate_data_structure(sensor_data):
                logger.error("Invalid data structure for logging")
                return False
            
            # Create DataFrame from sensor data
            df_row = pd.DataFrame([sensor_data])
            
            # Ensure columns are in correct order
            df_row = df_row.reindex(columns=self.columns)
            
            # Append to CSV file
            df_row.to_csv(self.csv_file, mode='a', header=False, index=False)
            
            logger.debug(f"Data logged successfully: {sensor_data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log data: {e}")
            return False
    
    def _validate_data_structure(self, data: Dict) -> bool:
        """
        Validate that data contains all required columns
        
        Args:
            data: Sensor data dictionary
            
        Returns:
            bool: True if valid, False otherwise
        """
        for column in self.columns:
            if column not in data:
                logger.error(f"Missing required column: {column}")
                return False
        return True
    
    def get_latest_data(self, n_rows: int = 100) -> Optional[pd.DataFrame]:
        """
        Get the latest n rows of data
        
        Args:
            n_rows: Number of latest rows to retrieve
            
        Returns:
            DataFrame: Latest data or None if error
        """
        try:
            if not os.path.exists(self.csv_file):
                logger.warning(f"CSV file does not exist: {self.csv_file}")
                return None
            
            # Read the CSV file
            df = pd.read_csv(self.csv_file)
            
            if df.empty:
                logger.warning("CSV file is empty")
                return None
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp and get latest n rows
            df_sorted = df.sort_values('timestamp').tail(n_rows)
            
            logger.debug(f"Retrieved {len(df_sorted)} latest rows")
            return df_sorted
            
        except Exception as e:
            logger.error(f"Failed to read latest data: {e}")
            return None
    
    def get_data_count(self) -> int:
        """
        Get total number of data points in CSV
        
        Returns:
            int: Number of rows in CSV file
        """
        try:
            if not os.path.exists(self.csv_file):
                return 0
            
            df = pd.read_csv(self.csv_file)
            return len(df)
            
        except Exception as e:
            logger.error(f"Failed to count data rows: {e}")
            return 0
    
    def get_data_range(self, start_time: str, end_time: str) -> Optional[pd.DataFrame]:
        """
        Get data within a specific time range
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            
        Returns:
            DataFrame: Data within time range or None if error
        """
        try:
            if not os.path.exists(self.csv_file):
                logger.warning(f"CSV file does not exist: {self.csv_file}")
                return None
            
            df = pd.read_csv(self.csv_file)
            
            if df.empty:
                return None
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            start_dt = pd.to_datetime(start_time)
            end_dt = pd.to_datetime(end_time)
            
            # Filter by time range
            mask = (df['timestamp'] >= start_dt) & (df['timestamp'] <= end_dt)
            filtered_df = df.loc[mask]
            
            logger.debug(f"Retrieved {len(filtered_df)} rows for time range {start_time} to {end_time}")
            return filtered_df
            
        except Exception as e:
            logger.error(f"Failed to get data range: {e}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Remove data older than specified days
        
        Args:
            days_to_keep: Number of days of data to retain
        """
        try:
            if not os.path.exists(self.csv_file):
                return
            
            df = pd.read_csv(self.csv_file)
            
            if df.empty:
                return
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - pd.Timedelta(days=days_to_keep)
            
            # Filter to keep only recent data
            df_filtered = df[df['timestamp'] >= cutoff_date]
            
            # Save back to CSV
            df_filtered.to_csv(self.csv_file, index=False)
            
            removed_rows = len(df) - len(df_filtered)
            logger.info(f"Cleaned up {removed_rows} old data rows, kept {len(df_filtered)} rows")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def get_statistics(self) -> Optional[Dict]:
        """
        Get basic statistics about the logged data
        
        Returns:
            Dict: Statistics summary or None if error
        """
        try:
            df = self.get_latest_data(n_rows=10000)  # Get recent data for stats
            
            if df is None or df.empty:
                return None
            
            # Calculate statistics
            stats = {
                'total_records': len(df),
                'date_range': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat()
                },
                'pm25': {
                    'mean': df['pm25'].mean(),
                    'min': df['pm25'].min(),
                    'max': df['pm25'].max(),
                    'std': df['pm25'].std()
                },
                'pm10': {
                    'mean': df['pm10'].mean(),
                    'min': df['pm10'].min(),
                    'max': df['pm10'].max(),
                    'std': df['pm10'].std()
                },
                'temperature': {
                    'mean': df['temperature'].mean(),
                    'min': df['temperature'].min(),
                    'max': df['temperature'].max(),
                    'std': df['temperature'].std()
                },
                'humidity': {
                    'mean': df['humidity'].mean(),
                    'min': df['humidity'].min(),
                    'max': df['humidity'].max(),
                    'std': df['humidity'].std()
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            return None

class PredictionLogger:
    """
    Logger for prediction results and accuracy tracking
    """
    def __init__(self, predictions_file: str = config.PREDICTIONS_FILE, 
                 accuracy_file: str = config.ACCURACY_LOG_FILE):
        """
        Initialize prediction logger
        
        Args:
            predictions_file: Path to predictions CSV file
            accuracy_file: Path to accuracy log CSV file
        """
        self.predictions_file = predictions_file
        self.accuracy_file = accuracy_file
        
        # Initialize prediction CSV
        if not os.path.exists(self.predictions_file):
            pred_columns = ['timestamp', 'prediction_time', 'horizon_hours', 'model_type', 
                           'predicted_pm25', 'predicted_pm10', 'predicted_temp', 
                           'predicted_humidity', 'actual_pm25', 'actual_pm10', 
                           'actual_temp', 'actual_humidity']
            pd.DataFrame(columns=pred_columns).to_csv(self.predictions_file, index=False)
        
        # Initialize accuracy CSV
        if not os.path.exists(self.accuracy_file):
            acc_columns = ['timestamp', 'model_type', 'horizon_hours', 'mae_pm25', 
                          'mae_pm10', 'mae_temp', 'mae_humidity', 'rmse_pm25', 
                          'rmse_pm10', 'rmse_temp', 'rmse_humidity']
            pd.DataFrame(columns=acc_columns).to_csv(self.accuracy_file, index=False)
    
    def log_prediction(self, prediction_data: Dict) -> bool:
        """
        Log prediction results
        
        Args:
            prediction_data: Dictionary containing prediction information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            df_row = pd.DataFrame([prediction_data])
            df_row.to_csv(self.predictions_file, mode='a', header=False, index=False)
            logger.debug("Prediction logged successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
            return False
    
    def log_accuracy(self, accuracy_data: Dict) -> bool:
        """
        Log accuracy metrics
        
        Args:
            accuracy_data: Dictionary containing accuracy metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            df_row = pd.DataFrame([accuracy_data])
            df_row.to_csv(self.accuracy_file, mode='a', header=False, index=False)
            logger.debug("Accuracy metrics logged successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to log accuracy: {e}")
            return False

if __name__ == "__main__":
    # Test the data logger
    print("Testing Data Logger...")
    
    # Create test data
    test_data = {
        'timestamp': datetime.now().isoformat(),
        'pm25': 25.5,
        'pm10': 35.2,
        'temperature': 28.3,
        'humidity': 65.8,
        'gas_level': 250
    }
    
    # Initialize logger
    logger_instance = DataLogger()
    
    # Log test data
    if logger_instance.log_data(test_data):
        print("✓ Data logged successfully")
    else:
        print("✗ Failed to log data")
    
    # Get statistics
    stats = logger_instance.get_statistics()
    if stats:
        print(f"✓ Statistics: {stats}")
    else:
        print("✗ No statistics available")
    
    # Get data count
    count = logger_instance.get_data_count()
    print(f"✓ Total data points: {count}")
