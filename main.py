"""
Main Application for Air Quality AI System
Orchestrates data collection, model training, and predictions
"""

import time
import logging
import signal
import sys
import threading
from datetime import datetime
import argparse

from sensor_interface import get_sensor_interface
from data_logger import DataLogger
from prediction_system import PredictionSystem
from ml_models import ModelManager
import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

class AirQualityAISystem:
    """
    Main system orchestrator
    """
    def __init__(self, mock_sensor=False):
        """
        Initialize the Air Quality AI System
        
        Args:
            mock_sensor: If True, use mock sensor for testing
        """
        self.mock_sensor = mock_sensor
        self.running = False
        
        # Initialize components
        self.sensor = get_sensor_interface(mock=mock_sensor)
        self.data_logger = DataLogger()
        self.prediction_system = PredictionSystem()
        self.model_manager = ModelManager()
        
        # Threads
        self.data_collection_thread = None
        self.dashboard_thread = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Air Quality AI System initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """
        Start the complete system
        """
        logger.info("Starting Air Quality AI System...")
        
        # Connect to sensor
        if not self.sensor.connect():
            logger.error("Failed to connect to sensor. Exiting.")
            return False
        
        # Load or train initial model
        if not self._initialize_model():
            logger.warning("No model available. Will train when enough data is collected.")
        
        # Start prediction system
        self.prediction_system.start_prediction_service()
        
        # Start data collection
        self.running = True
        self.data_collection_thread = threading.Thread(target=self._data_collection_loop, daemon=True)
        self.data_collection_thread.start()
        
        # Start dashboard in a separate thread
        self.dashboard_thread = threading.Thread(target=self._start_dashboard, daemon=True)
        self.dashboard_thread.start()
        
        logger.info("✅ Air Quality AI System started successfully!")
        logger.info(f"📊 Data collection interval: {config.DATA_COLLECTION_INTERVAL} seconds")
        logger.info(f"🤖 Model type: {self.model_manager.current_model_type or 'None (will train later)'}")
        logger.info(f"🌐 Dashboard available at: http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
        logger.info(f"🌐 Local access: http://localhost:{config.DASHBOARD_PORT}")
        
        return True
    
    def stop(self):
        """
        Stop the system gracefully
        """
        logger.info("Stopping Air Quality AI System...")
        
        self.running = False
        
        # Stop prediction system
        self.prediction_system.stop_prediction_service()
        
        # Disconnect sensor
        if self.sensor:
            self.sensor.disconnect()
        
        # Wait for threads to finish
        if self.data_collection_thread and self.data_collection_thread.is_alive():
            self.data_collection_thread.join(timeout=5)
        
        if self.dashboard_thread and self.dashboard_thread.is_alive():
            self.dashboard_thread.join(timeout=2)
        
        logger.info("✅ Air Quality AI System stopped")
    
    def _start_dashboard(self):
        """
        Start the web dashboard in a separate thread
        """
        try:
            logger.info("🌐 Starting web dashboard...")
            
            # Import dashboard here to avoid circular imports
            from dashboard import app
            
            # Start the dashboard server
            app.run_server(
                host=config.DASHBOARD_HOST,
                port=config.DASHBOARD_PORT,
                debug=config.DASHBOARD_DEBUG,
                use_reloader=False,  # Disable reloader in threaded mode
                dev_tools_hot_reload=False  # Disable hot reload
            )
            
        except ImportError as e:
            logger.error(f"❌ Dashboard import failed: {e}")
            logger.info("🔄 Trying simple dashboard fallback...")
            self._start_simple_dashboard()
            
        except Exception as e:
            logger.error(f"❌ Failed to start dashboard: {e}")
            logger.info("🔄 Trying simple dashboard fallback...")
            self._start_simple_dashboard()
    
    def _start_simple_dashboard(self):
        """
        Start simple fallback dashboard
        """
        try:
            from simple_dashboard import create_dash_app
            
            app = create_dash_app()
            if app:
                logger.info("🌐 Starting simple dashboard...")
                app.run_server(
                    host=config.DASHBOARD_HOST,
                    port=config.DASHBOARD_PORT,
                    debug=False,
                    use_reloader=False,
                    dev_tools_hot_reload=False
                )
            else:
                raise ImportError("Simple dashboard not available")
                
        except Exception as e:
            logger.error(f"❌ Simple dashboard also failed: {e}")
            logger.info("💡 Dashboard unavailable. You can:")
            logger.info(f"   - Check data files in: {config.DATA_DIR}")
            logger.info(f"   - Run: python3 simple_dashboard.py")
            logger.info(f"   - Run: python3 start_website.py")
    
    def _initialize_model(self) -> bool:
        """
        Initialize or load existing model
        
        Returns:
            True if model is ready, False otherwise
        """
        # Try to load existing model
        if self.model_manager.load_model():
            logger.info(f"✅ Loaded existing {self.model_manager.current_model_type} model")
            return True
        
        # Check if we have enough data to train a new model
        data_count = self.data_logger.get_data_count()
        
        if data_count >= 100:  # Minimum data for training
            logger.info(f"Training new model with {data_count} data points...")
            
            # Get training data
            training_data = self.data_logger.get_latest_data(n_rows=data_count)
            
            if training_data is not None and len(training_data) >= 100:
                try:
                    # Train model
                    results = self.model_manager.train_model(training_data)
                    logger.info(f"✅ Model trained successfully: {results}")
                    return True
                except Exception as e:
                    logger.error(f"Failed to train model: {e}")
                    return False
            else:
                logger.warning("Training data is insufficient")
                return False
        else:
            logger.info(f"Not enough data for training ({data_count}/100 minimum)")
            return False
    
    def _data_collection_loop(self):
        """
        Main data collection loop
        """
        logger.info("🔄 Data collection started")
        
        consecutive_failures = 0
        max_failures = 10
        
        while self.running:
            try:
                # Read sensor data
                sensor_data = self.sensor.read_sensor_data()
                
                if sensor_data:
                    # Log data to CSV
                    if self.data_logger.log_data(sensor_data):
                        logger.debug(f"Data logged: PM2.5={sensor_data['pm25']:.1f}, PM10={sensor_data['pm10']:.1f}")
                        consecutive_failures = 0
                        
                        # Check if we need to train initial model
                        if self.model_manager.current_model_type is None:
                            data_count = self.data_logger.get_data_count()
                            if data_count >= 100 and data_count % 50 == 0:  # Check every 50 new records
                                logger.info(f"Attempting to train initial model with {data_count} records...")
                                self._initialize_model()
                    else:
                        logger.error("Failed to log sensor data")
                        consecutive_failures += 1
                else:
                    logger.warning("No sensor data received")
                    consecutive_failures += 1
                
                # Check for too many consecutive failures
                if consecutive_failures >= max_failures:
                    logger.error(f"Too many consecutive failures ({consecutive_failures}). Attempting to reconnect...")
                    
                    # Try to reconnect
                    self.sensor.disconnect()
                    time.sleep(5)
                    
                    if self.sensor.connect():
                        logger.info("Sensor reconnected successfully")
                        consecutive_failures = 0
                    else:
                        logger.error("Failed to reconnect sensor")
                        time.sleep(30)  # Wait longer before next attempt
                
                # Wait for next collection
                time.sleep(config.DATA_COLLECTION_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                consecutive_failures += 1
                time.sleep(config.DATA_COLLECTION_INTERVAL)
        
        logger.info("🔄 Data collection stopped")
    
    def get_system_status(self) -> dict:
        """
        Get current system status
        
        Returns:
            Dictionary with system status information
        """
        try:
            data_count = self.data_logger.get_data_count()
            latest_data = self.data_logger.get_latest_data(n_rows=1)
            
            status = {
                'running': self.running,
                'sensor_connected': self.sensor.is_connected if hasattr(self.sensor, 'is_connected') else False,
                'data_count': data_count,
                'model_type': self.model_manager.current_model_type,
                'last_data_time': None,
                'prediction_service_running': self.prediction_system.is_running
            }
            
            if latest_data is not None and not latest_data.empty:
                status['last_data_time'] = latest_data.iloc[0]['timestamp']
                status['latest_readings'] = {
                    'pm25': latest_data.iloc[0]['pm25'],
                    'pm10': latest_data.iloc[0]['pm10'],
                    'temperature': latest_data.iloc[0]['temperature'],
                    'humidity': latest_data.iloc[0]['humidity']
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def run_maintenance(self):
        """
        Run system maintenance tasks
        """
        logger.info("🔧 Running system maintenance...")
        
        try:
            # Clean up old data (keep last 30 days)
            self.data_logger.cleanup_old_data(days_to_keep=30)
            
            # Get system statistics
            stats = self.data_logger.get_statistics()
            if stats:
                logger.info(f"📊 System statistics: {stats['total_records']} records, "
                          f"PM2.5 avg: {stats['pm25']['mean']:.1f}")
            
            # Check model performance
            accuracy_summary = self.prediction_system.get_accuracy_summary(days=7)
            if accuracy_summary:
                logger.info("🎯 Model accuracy summary available")
            
            logger.info("✅ Maintenance completed")
            
        except Exception as e:
            logger.error(f"Error during maintenance: {e}")

def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(description='Air Quality AI System')
    parser.add_argument('--mock', action='store_true', 
                       help='Use mock sensor for testing')
    parser.add_argument('--dashboard-only', action='store_true',
                       help='Run only the dashboard')
    parser.add_argument('--maintenance', action='store_true',
                       help='Run maintenance tasks and exit')
    
    args = parser.parse_args()
    
    if args.dashboard_only:
        # Run only dashboard
        logger.info("Starting dashboard only...")
        from dashboard import app
        app.run_server(
            host=config.DASHBOARD_HOST,
            port=config.DASHBOARD_PORT,
            debug=config.DASHBOARD_DEBUG
        )
        return
    
    # Initialize system
    system = AirQualityAISystem(mock_sensor=args.mock)
    
    if args.maintenance:
        # Run maintenance and exit
        system.run_maintenance()
        return
    
    # Start the system
    if system.start():
        try:
            # Keep the main thread alive
            while system.running:
                time.sleep(1)
                
                # Run periodic maintenance (every hour)
                current_time = datetime.now()
                if current_time.minute == 0 and current_time.second < 5:
                    system.run_maintenance()
                    
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            system.stop()
    else:
        logger.error("Failed to start system")
        sys.exit(1)

if __name__ == "__main__":
    main()
