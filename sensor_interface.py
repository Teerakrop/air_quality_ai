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
        # Try multiple ports if the configured one fails
        ports_to_try = [self.port]
        
        # Add common Jetson Nano ports
        import glob
        jetson_ports = glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*')
        for port in jetson_ports:
            if port not in ports_to_try:
                ports_to_try.append(port)
        
        for port_attempt in ports_to_try:
            try:
                logger.info(f"Trying to connect to {port_attempt}...")
                self.serial_connection = serial.Serial(
                    port=port_attempt,
                    baudrate=self.baud_rate,
                    timeout=config.TIMEOUT,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                
                # Update the port if successful
                self.port = port_attempt
            
                # Wait for connection to stabilize
                time.sleep(2)
                
                # Test connection with a ping
                if self._test_connection():
                    self.is_connected = True
                    logger.info(f"Successfully connected to sensor on {port_attempt}")
                    return True
                else:
                    logger.warning(f"Connection test failed for {port_attempt}")
                    self.serial_connection.close()
                    continue
                    
            except serial.SerialException as e:
                logger.warning(f"Failed to connect to {port_attempt}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error connecting to {port_attempt}: {e}")
                continue
        
        logger.error(f"Failed to connect to any serial port. Tried: {ports_to_try}")
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
        """Generate mock sensor data - Thailand specific"""
        import random
        from datetime import datetime
        
        if not self.is_connected:
            return None
        
        # ข้อมูลจำลองแบบประเทศไทย
        current_hour = datetime.now().hour
        
        # รูปแบบมลพิษตามเวลาแบบไทย
        if 7 <= current_hour <= 9 or 17 <= current_hour <= 19:  # ช่วงเร่งด่วน
            pm25_base = random.uniform(35, 65)  # กรุงเทพฯ ช่วงรถติด
            pm10_base = random.uniform(45, 85)
        elif 22 <= current_hour or current_hour <= 6:  # กลางคืน
            pm25_base = random.uniform(15, 35)  # ยังมีมลพิษตกค้าง
            pm10_base = random.uniform(25, 45)
        else:  # เวลาปกติ
            pm25_base = random.uniform(25, 45)  # ระดับปานกลางของไทย
            pm10_base = random.uniform(35, 60)
        
        # อุณหภูมิแบบไทย (20-38°C)
        temp_base = 28 + 6 * (current_hour - 12) / 12  # รอบวัน
        temperature = temp_base + random.uniform(-3, 3)
        temperature = max(20, min(38, temperature))
        
        # ความชื้นสูงแบบไทย (50-95%)
        humidity_base = 75 - (temperature - 28) * 1.5
        humidity = humidity_base + random.uniform(-10, 10)
        humidity = max(50, min(95, humidity))
        
        # ระดับแก๊สตามมลพิษ
        gas_level = int(200 + pm25_base * 5 + random.uniform(-50, 50))
        gas_level = max(100, min(800, gas_level))
        
        mock_data = {
            'timestamp': datetime.now().isoformat(),
            'pm25': round(pm25_base, 1),
            'pm10': round(pm10_base, 1),
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'gas_level': gas_level
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
