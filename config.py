"""
Configuration file for Air Quality AI System
"""
import os
import platform
from datetime import datetime

# Data Collection Settings
# Auto-detect serial port based on OS
if platform.system() == 'Windows':
    SERIAL_PORT = 'COM3'  # Default Windows COM port
else:
    SERIAL_PORT = '/dev/ttyUSB0'  # Linux/Unix port
BAUD_RATE = 115200
DATA_COLLECTION_INTERVAL = 5  # seconds
TIMEOUT = 10  # seconds

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Data Files
RAW_DATA_FILE = os.path.join(DATA_DIR, 'air_quality_data.csv')
PREDICTIONS_FILE = os.path.join(DATA_DIR, 'predictions.csv')
ACCURACY_LOG_FILE = os.path.join(DATA_DIR, 'accuracy_log.csv')

# Model Settings
LSTM_MODEL_PATH = os.path.join(MODELS_DIR, 'lstm_model.h5')
RF_MODEL_PATH = os.path.join(MODELS_DIR, 'random_forest_model.joblib')
SCALER_PATH = os.path.join(MODELS_DIR, 'scaler.joblib')

# ML Parameters
SEQUENCE_LENGTH = 60  # Use 60 data points (5 minutes at 5-second intervals)
PREDICTION_HORIZONS = [12, 36, 72]  # 1, 3, 6 hours in 5-minute intervals
MIN_DATA_FOR_LSTM = 10000  # Minimum rows to use LSTM instead of RandomForest
TRAIN_TEST_SPLIT = 0.8
RETRAIN_INTERVAL_HOURS = 24  # Retrain model every 24 hours

# Dashboard Settings
DASHBOARD_HOST = '0.0.0.0'
DASHBOARD_PORT = 8050
DASHBOARD_DEBUG = False

# Sensor Thresholds (for alerts)
PM25_THRESHOLD = 35.0  # μg/m³
PM10_THRESHOLD = 50.0  # μg/m³
TEMP_MIN = -10.0  # °C
TEMP_MAX = 60.0   # °C
HUMIDITY_MIN = 0.0   # %
HUMIDITY_MAX = 100.0 # %

# Data Validation
SENSOR_COLUMNS = ['timestamp', 'pm25', 'pm10', 'temperature', 'humidity', 'gas_level']
REQUIRED_COLUMNS = SENSOR_COLUMNS

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
