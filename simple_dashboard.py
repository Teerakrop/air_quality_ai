#!/usr/bin/env python3
"""
Simple fallback dashboard for Air Quality AI System
This is a lightweight dashboard that works even if the main dashboard fails
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import dash
    from dash import html, dcc, Input, Output
    import plotly.graph_objs as go
    import plotly.express as px
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    logger.warning("Dash not available, creating HTML-only dashboard")

import config

class SimpleDashboard:
    """Simple dashboard that works with minimal dependencies"""
    
    def __init__(self):
        self.data_file = config.RAW_DATA_FILE
        self.predictions_file = config.PREDICTIONS_FILE
        
    def get_latest_data(self, hours=24):
        """Get latest data from CSV files"""
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    # Get last 24 hours
                    cutoff = datetime.now() - timedelta(hours=hours)
                    recent_data = df[df['timestamp'] >= cutoff]
                    return recent_data.tail(100)  # Last 100 readings
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return pd.DataFrame()
    
    def get_predictions(self):
        """Get latest predictions"""
        try:
            if os.path.exists(self.predictions_file):
                df = pd.read_csv(self.predictions_file)
                if not df.empty:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    return df.tail(10)  # Last 10 predictions
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error reading predictions: {e}")
            return pd.DataFrame()

def create_dash_app():
    """Create Dash application"""
    if not DASH_AVAILABLE:
        return None
    
    app = dash.Dash(__name__)
    dashboard = SimpleDashboard()
    
    app.layout = html.Div([
        html.H1("🌬️ Air Quality AI - Simple Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB', 'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                html.H3("📊 System Status", style={'color': '#28a745'}),
                html.P(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
                html.P("✅ System is running"),
                html.P(f"📁 Data file: {os.path.basename(config.RAW_DATA_FILE)}"),
            ], className="status-panel", style={
                'backgroundColor': '#f8f9fa', 'padding': '20px', 
                'borderRadius': '10px', 'margin': '10px'
            }),
        ]),
        
        # Auto-refresh every 30 seconds
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # 30 seconds
            n_intervals=0
        ),
        
        # Data display
        html.Div(id='data-display'),
        
        # Charts
        html.Div([
            dcc.Graph(id='pm25-chart'),
            dcc.Graph(id='temp-humidity-chart'),
        ]),
        
        # Footer
        html.Hr(),
        html.P("🚀 Air Quality AI System - Jetson Nano Compatible", 
               style={'textAlign': 'center', 'color': '#6c757d', 'marginTop': '30px'})
    ])
    
    @app.callback(
        [Output('data-display', 'children'),
         Output('pm25-chart', 'figure'),
         Output('temp-humidity-chart', 'figure')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_dashboard(n):
        # Get latest data
        df = dashboard.get_latest_data()
        predictions = dashboard.get_predictions()
        
        # Data summary
        if not df.empty:
            latest = df.iloc[-1]
            data_summary = html.Div([
                html.H3("📈 Latest Readings"),
                html.Div([
                    html.Div([
                        html.H4(f"{latest['pm25']:.1f} μg/m³", style={'color': '#dc3545' if latest['pm25'] > 35 else '#28a745'}),
                        html.P("PM2.5")
                    ], style={'textAlign': 'center', 'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
                    
                    html.Div([
                        html.H4(f"{latest['pm10']:.1f} μg/m³", style={'color': '#dc3545' if latest['pm10'] > 50 else '#28a745'}),
                        html.P("PM10")
                    ], style={'textAlign': 'center', 'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
                    
                    html.Div([
                        html.H4(f"{latest['temperature']:.1f}°C"),
                        html.P("Temperature")
                    ], style={'textAlign': 'center', 'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
                    
                    html.Div([
                        html.H4(f"{latest['humidity']:.1f}%"),
                        html.P("Humidity")
                    ], style={'textAlign': 'center', 'margin': '10px', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}),
                ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'})
            ])
        else:
            data_summary = html.Div([
                html.H3("📊 No Data Available"),
                html.P("Waiting for sensor data..."),
                html.P("Make sure the system is collecting data.")
            ])
        
        # PM2.5 Chart
        if not df.empty:
            pm25_fig = {
                'data': [
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['pm25'],
                        mode='lines+markers',
                        name='PM2.5',
                        line=dict(color='#dc3545', width=2)
                    )
                ],
                'layout': {
                    'title': 'PM2.5 Levels Over Time',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'PM2.5 (μg/m³)'},
                    'hovermode': 'x unified'
                }
            }
        else:
            pm25_fig = {
                'data': [],
                'layout': {
                    'title': 'PM2.5 Levels - No Data',
                    'annotations': [{
                        'text': 'No data available',
                        'xref': 'paper', 'yref': 'paper',
                        'x': 0.5, 'y': 0.5, 'showarrow': False
                    }]
                }
            }
        
        # Temperature & Humidity Chart
        if not df.empty:
            temp_humidity_fig = {
                'data': [
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['temperature'],
                        mode='lines+markers',
                        name='Temperature (°C)',
                        yaxis='y',
                        line=dict(color='#fd7e14', width=2)
                    ),
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['humidity'],
                        mode='lines+markers',
                        name='Humidity (%)',
                        yaxis='y2',
                        line=dict(color='#20c997', width=2)
                    )
                ],
                'layout': {
                    'title': 'Temperature & Humidity Over Time',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Temperature (°C)', 'side': 'left'},
                    'yaxis2': {'title': 'Humidity (%)', 'side': 'right', 'overlaying': 'y'},
                    'hovermode': 'x unified'
                }
            }
        else:
            temp_humidity_fig = {
                'data': [],
                'layout': {
                    'title': 'Temperature & Humidity - No Data',
                    'annotations': [{
                        'text': 'No data available',
                        'xref': 'paper', 'yref': 'paper',
                        'x': 0.5, 'y': 0.5, 'showarrow': False
                    }]
                }
            }
        
        return data_summary, pm25_fig, temp_humidity_fig
    
    return app

def create_html_dashboard():
    """Create simple HTML dashboard if Dash is not available"""
    dashboard = SimpleDashboard()
    df = dashboard.get_latest_data()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Air Quality AI - Simple Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta http-equiv="refresh" content="30">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; color: #2E86AB; margin-bottom: 30px; }}
            .status {{ background-color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .metrics {{ display: flex; justify-content: space-around; flex-wrap: wrap; }}
            .metric {{ background-color: white; padding: 15px; margin: 10px; border-radius: 8px; text-align: center; min-width: 150px; }}
            .value {{ font-size: 24px; font-weight: bold; }}
            .label {{ color: #6c757d; }}
            .good {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .danger {{ color: #dc3545; }}
            .footer {{ text-align: center; color: #6c757d; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🌬️ Air Quality AI - Simple Dashboard</h1>
            
            <div class="status">
                <h3>📊 System Status</h3>
                <p>🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>✅ System is running</p>
                <p>📁 Data records: {len(df) if not df.empty else 0}</p>
            </div>
    """
    
    if not df.empty:
        latest = df.iloc[-1]
        pm25_class = "danger" if latest['pm25'] > 35 else "good"
        pm10_class = "danger" if latest['pm10'] > 50 else "good"
        
        html_content += f"""
            <div class="metrics">
                <div class="metric">
                    <div class="value {pm25_class}">{latest['pm25']:.1f}</div>
                    <div class="label">PM2.5 (μg/m³)</div>
                </div>
                <div class="metric">
                    <div class="value {pm10_class}">{latest['pm10']:.1f}</div>
                    <div class="label">PM10 (μg/m³)</div>
                </div>
                <div class="metric">
                    <div class="value">{latest['temperature']:.1f}°C</div>
                    <div class="label">Temperature</div>
                </div>
                <div class="metric">
                    <div class="value">{latest['humidity']:.1f}%</div>
                    <div class="label">Humidity</div>
                </div>
            </div>
        """
    else:
        html_content += """
            <div class="status">
                <h3>📊 No Data Available</h3>
                <p>Waiting for sensor data...</p>
                <p>Make sure the system is collecting data.</p>
            </div>
        """
    
    html_content += """
            <div class="footer">
                <p>🚀 Air Quality AI System - Jetson Nano Compatible</p>
                <p>Page auto-refreshes every 30 seconds</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def main():
    """Main function to start the simple dashboard"""
    print("🌬️ Starting Simple Air Quality Dashboard...")
    
    if DASH_AVAILABLE:
        print("📊 Using Dash interactive dashboard")
        app = create_dash_app()
        if app:
            print(f"🌐 Dashboard starting at: http://{config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")
            print("🛑 Press Ctrl+C to stop")
            
            try:
                app.run_server(
                    host=config.DASHBOARD_HOST,
                    port=config.DASHBOARD_PORT,
                    debug=False
                )
            except Exception as e:
                print(f"❌ Error starting Dash app: {e}")
                print("💡 Falling back to HTML dashboard")
    
    # Fallback to HTML
    print("📄 Creating HTML dashboard")
    html_content = create_html_dashboard()
    
    # Save HTML file
    html_file = os.path.join(config.BASE_DIR, 'simple_dashboard.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML dashboard created: {html_file}")
    print(f"🌐 Open in browser: file://{html_file}")

if __name__ == "__main__":
    main()
