"""
Configuration file for Air Quality AI System
"""
import os
import platform
from datetime import datetime

# Data Collection Settings
# Auto-detect serial port based on OS and hardware
def detect_serial_port():
    """Auto-detect ESP32 serial port"""
    import glob
    import os
    
    # Check for Jetson Nano specific ports first
    jetson_ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyUSB1']
    for port in jetson_ports:
        if os.path.exists(port):
            return port
    
    # Fallback to system detection
    if platform.system() == 'Windows':
        ports = glob.glob('COM*')
        return ports[0] if ports else 'COM3'
    else:
        # Linux/Unix - try common ESP32 ports
        possible_ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        return possible_ports[0] if possible_ports else '/dev/ttyUSB0'

# Try to auto-detect, fallback to default
try:
    SERIAL_PORT = detect_serial_port()
except:
    SERIAL_PORT = '/dev/ttyUSB0' if platform.system() != 'Windows' else 'COM3'
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

# ML Parameters - Optimized for Jetson Nano
SEQUENCE_LENGTH = 60  # Use 60 data points (5 minutes at 5-second intervals)
PREDICTION_HORIZONS = [12, 36, 72]  # 1, 3, 6 hours in 5-minute intervals

# Jetson Nano Memory Optimization
def get_min_data_for_lstm():
    """Determine minimum data based on available memory"""
    try:
        import psutil
        total_memory = psutil.virtual_memory().total / (1024**3)  # GB
        if total_memory < 6:  # Jetson Nano has 4GB
            return 50000  # Use more data before switching to LSTM
        else:
            return 10000
    except:
        return 50000  # Conservative default for Jetson Nano

MIN_DATA_FOR_LSTM = get_min_data_for_lstm()
TRAIN_TEST_SPLIT = 0.8
RETRAIN_INTERVAL_HOURS = 24  # Retrain model every 24 hours

# Jetson Nano specific optimizations
JETSON_OPTIMIZATION = True
MAX_BATCH_SIZE = 16  # Smaller batch size for Jetson Nano
MAX_EPOCHS = 30  # Fewer epochs to prevent overheating
MAX_CPU_CORES = 2   # Limit CPU usage on Jetson Nano
ENABLE_GPU_MEMORY_GROWTH = True  # Prevent TensorFlow from allocating all GPU memory

# VS Code 1.68.1 Compatibility Settings
VSCODE_COMPATIBILITY = True
DISABLE_HEAVY_LOGGING = True  # Reduce log output for better VS Code performance
OPTIMIZE_FOR_DEVELOPMENT = True  # Enable development-friendly settings

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
