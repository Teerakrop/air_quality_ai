"""
Sensor Interface Module for Air Quality Data Collection
Handles communication with ESP32 via USB-UART
Supports SDS011 (PM2.5, PM10), MQ135 (Gas), DHT22 (Temp, Humidity)
"""

import serial
import json
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class SensorInterface:
    def __init__(self, port: str = config.SERIAL_PORT, baud_rate: int = config.BAUD_RATE):
        """
        Initialize sensor interface
        
        Args:
            port: Serial port for ESP32 connection
            baud_rate: Communication baud rate
        """
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to ESP32
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=config.TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Wait for connection to stabilize
            time.sleep(2)
            
            # Test connection with a ping
            if self._test_connection():
                self.is_connected = True
                logger.info(f"Successfully connected to sensor on {self.port}")
                return True
            else:
                logger.error("Connection test failed")
                return False
                
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def _test_connection(self) -> bool:
        """
        Test if ESP32 is responding
        
        Returns:
            bool: True if ESP32 responds, False otherwise
        """
        try:
            # Send ping command
            self.serial_connection.write(b'PING\n')
            self.serial_connection.flush()
            
            # Wait for response
            response = self.serial_connection.readline().decode('utf-8').strip()
            return response == 'PONG'
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def read_sensor_data(self) -> Optional[Dict]:
        """
        Read sensor data from ESP32
        
        Expected JSON format from ESP32:
        {
            "pm25": 12.5,
            "pm10": 18.3,
            "temperature": 25.4,
            "humidity": 65.2,
            "gas_level": 150
        }
        
        Returns:
            Dict: Sensor data with timestamp, None if error
        """
        if not self.is_connected:
            logger.error("Not connected to sensor")
            return None
            
        try:
            # Request data from ESP32
            self.serial_connection.write(b'READ\n')
            self.serial_connection.flush()
            
            # Read response
            raw_data = self.serial_connection.readline().decode('utf-8').strip()
            
            if not raw_data:
                logger.warning("No data received from sensor")
                return None
            
            # Parse JSON data
            sensor_data = json.loads(raw_data)
            
            # Add timestamp
            sensor_data['timestamp'] = datetime.now().isoformat()
            
            # Validate data
            if self._validate_sensor_data(sensor_data):
                logger.debug(f"Sensor data received: {sensor_data}")
                return sensor_data
            else:
                logger.warning(f"Invalid sensor data: {sensor_data}")
                return None
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON data: {raw_data}, Error: {e}")
            return None
        except serial.SerialException as e:
            logger.error(f"Serial communication error: {e}")
            self.is_connected = False
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading sensor data: {e}")
            return None
    
    def _validate_sensor_data(self, data: Dict) -> bool:
        """
        Validate sensor data ranges
        
        Args:
            data: Sensor data dictionary
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ['pm25', 'pm10', 'temperature', 'humidity', 'gas_level']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate ranges
            pm25 = float(data['pm25'])
            pm10 = float(data['pm10'])
            temp = float(data['temperature'])
            humidity = float(data['humidity'])
            gas = float(data['gas_level'])
            
            # PM2.5 and PM10 should be positive and reasonable
            if pm25 < 0 or pm25 > 1000:
                logger.error(f"PM2.5 out of range: {pm25}")
                return False
                
            if pm10 < 0 or pm10 > 1000:
                logger.error(f"PM10 out of range: {pm10}")
                return False
            
            # Temperature range check
            if temp < config.TEMP_MIN or temp > config.TEMP_MAX:
                logger.error(f"Temperature out of range: {temp}")
                return False
            
            # Humidity range check
            if humidity < config.HUMIDITY_MIN or humidity > config.HUMIDITY_MAX:
                logger.error(f"Humidity out of range: {humidity}")
                return False
            
            # Gas level should be positive
            if gas < 0 or gas > 10000:
                logger.error(f"Gas level out of range: {gas}")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Data validation error: {e}")
            return False
    
    def disconnect(self):
        """
        Close serial connection
        """
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            logger.info("Disconnected from sensor")

class MockSensorInterface(SensorInterface):
    """
    Mock sensor interface for testing without hardware
    """
    def __init__(self):
        super().__init__()
        self.is_connected = False
        
    def connect(self) -> bool:
        """Mock connection always succeeds"""
        self.is_connected = True
        logger.info("Mock sensor connected")
        return True
    
    def read_sensor_data(self) -> Optional[Dict]:
        """Generate mock sensor data"""
        import random
        
        if not self.is_connected:
            return None
        
        # Generate realistic mock data
        mock_data = {
            'timestamp': datetime.now().isoformat(),
            'pm25': round(random.uniform(5, 50), 1),
            'pm10': round(random.uniform(10, 80), 1),
            'temperature': round(random.uniform(20, 35), 1),
            'humidity': round(random.uniform(40, 80), 1),
            'gas_level': random.randint(100, 500)
        }
        
        logger.debug(f"Mock sensor data: {mock_data}")
        return mock_data
    
    def disconnect(self):
        """Mock disconnect"""
        self.is_connected = False
        logger.info("Mock sensor disconnected")

def get_sensor_interface(mock: bool = False) -> SensorInterface:
    """
    Factory function to get sensor interface
    
    Args:
        mock: If True, return mock interface for testing
        
    Returns:
        SensorInterface: Configured sensor interface
    """
    if mock:
        return MockSensorInterface()
    else:
        return SensorInterface()

if __name__ == "__main__":
    # Test the sensor interface
    print("Testing Sensor Interface...")
    
    # Test with mock sensor
    sensor = get_sensor_interface(mock=True)
    
    if sensor.connect():
        print("Connected successfully!")
        
        # Read some test data
        for i in range(5):
            data = sensor.read_sensor_data()
            if data:
                print(f"Reading {i+1}: {data}")
            time.sleep(1)
        
        sensor.disconnect()
    else:
        print("Failed to connect to sensor")
