"""
Real-time Dashboard for Air Quality AI System
Shows real-time values, forecasts, and historical accuracy
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from data_logger import DataLogger, PredictionLogger
from prediction_system import PredictionSystem
import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL), format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Initialize components
data_logger = DataLogger()
prediction_system = PredictionSystem()

# Initialize Dash app with modern theme
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
])
app.title = "🌬️ Air Quality AI Dashboard"

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .main-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                margin: 20px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }
            .metric-card {
                background: linear-gradient(145deg, #ffffff, #f0f0f0);
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: none;
            }
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.15);
            }
            .header-title {
                background: linear-gradient(45deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            .section-header {
                color: #2c3e50;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }
            .status-badge {
                border-radius: 20px;
                padding: 8px 16px;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Color scheme
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff7f0e',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# PM2.5 color mapping based on AQI
def get_pm25_color(value):
    if value <= 12:
        return '#00e400'  # Good
    elif value <= 35:
        return '#ffff00'  # Moderate
    elif value <= 55:
        return '#ff7e00'  # Unhealthy for Sensitive Groups
    elif value <= 150:
        return '#ff0000'  # Unhealthy
    elif value <= 250:
        return '#8f3f97'  # Very Unhealthy
    else:
        return '#7e0023'  # Hazardous

# Layout components
def create_metric_card(title, value, unit, color='primary', icon=None):
    """Create a modern metric display card"""
    # Icon mapping
    icon_map = {
        'PM2.5': 'fas fa-smog',
        'PM10': 'fas fa-cloud',
        'Temperature': 'fas fa-thermometer-half',
        'Humidity': 'fas fa-tint'
    }
    
    card_icon = icon_map.get(title, 'fas fa-chart-line')
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.I(className=f"{card_icon} fa-2x text-{color} mb-2"),
                    html.H6(title, className="card-title text-muted mb-1"),
                    html.H2(f"{value:.1f}", className=f"text-{color} mb-0 fw-bold"),
                    html.Small(unit, className="text-muted")
                ], className="text-center")
            ])
        ], className="p-4")
    ], className="metric-card mb-3 h-100")

def create_alert_card(message, color='info'):
    """Create an alert card"""
    return dbc.Alert(message, color=color, className="mb-3")

# Main layout
app.layout = html.Div([
    dbc.Container([
        # Header with modern design
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1([
                        html.I(className="fas fa-wind me-3"),
                        "Air Quality AI Dashboard"
                    ], className="header-title text-center mb-3"),
                    html.P([
                        html.I(className="fas fa-robot me-2"),
                        "Real-time monitoring and AI-powered forecasting"
                    ], className="text-center text-muted mb-4 fs-5"),
                    html.Hr(className="my-4")
                ])
            ])
        ]),
    
        # Status indicators with modern badges
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-info-circle me-2"),
                        "System Status"
                    ], className="section-header"),
                    html.Div(id="status-indicators")
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Current readings with enhanced design
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-tachometer-alt me-2"),
                        "Current Readings"
                    ], className="section-header"),
                    html.Div(id="current-readings")
                ])
            ], width=12)
        ], className="mb-4"),
    
        # Real-time charts with modern styling
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-chart-line me-2"),
                        "Real-time Trends (Last 24 Hours)"
                    ], className="section-header"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="realtime-chart", config={'displayModeBar': False})
                        ])
                    ], className="metric-card")
                ])
            ], width=12)
        ], className="mb-4"),
        
        # Predictions and accuracy in modern cards
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-crystal-ball me-2"),
                        "AI Predictions"
                    ], className="section-header"),
                    html.Div(id="predictions-display")
                ])
            ], width=6),
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-bullseye me-2"),
                        "Prediction Accuracy"
                    ], className="section-header"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="accuracy-chart", config={'displayModeBar': False})
                        ])
                    ], className="metric-card")
                ])
            ], width=6)
        ], className="mb-4"),
        
        # Historical comparison with enhanced design
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-balance-scale me-2"),
                        "Historical vs Predicted"
                    ], className="section-header"),
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id="comparison-chart", config={'displayModeBar': False})
                        ])
                    ], className="metric-card")
                ])
            ], width=12)
        ], className="mb-4"),
    
        # Auto-refresh with status indicator
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Auto-refresh every 30 seconds"
                    ], className="text-muted text-center mb-0"),
                    dcc.Interval(
                        id='interval-component',
                        interval=30*1000,  # Update every 30 seconds
                        n_intervals=0
                    )
                ])
            ])
        ], className="mt-4")
        
    ], className="main-container", fluid=True)
], style={'minHeight': '100vh'})

@app.callback(
    Output('status-indicators', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_status_indicators(n):
    """Update system status indicators"""
    try:
        # Check data availability
        data_count = data_logger.get_data_count()
        latest_data = data_logger.get_latest_data(n_rows=1)
        
        indicators = []
        
        # Data status with enhanced styling
        if data_count > 0 and latest_data is not None:
            last_update = pd.to_datetime(latest_data.iloc[0]['timestamp'])
            time_diff = datetime.now() - last_update
            
            if time_diff < timedelta(minutes=2):
                indicators.append(
                    dbc.Badge([
                        html.I(className="fas fa-circle me-1"),
                        "Data Live"
                    ], color="success", className="status-badge me-2")
                )
            elif time_diff < timedelta(minutes=10):
                indicators.append(
                    dbc.Badge([
                        html.I(className="fas fa-exclamation-triangle me-1"),
                        "Data Delayed"
                    ], color="warning", className="status-badge me-2")
                )
            else:
                indicators.append(
                    dbc.Badge([
                        html.I(className="fas fa-times-circle me-1"),
                        "Data Stale"
                    ], color="danger", className="status-badge me-2")
                )
        else:
            indicators.append(
                dbc.Badge([
                    html.I(className="fas fa-ban me-1"),
                    "No Data"
                ], color="secondary", className="status-badge me-2")
            )
        
        # Model status with icons
        if prediction_system.model_manager.current_model_type:
            indicators.append(
                dbc.Badge([
                    html.I(className="fas fa-brain me-1"),
                    f"{prediction_system.model_manager.current_model_type} Model"
                ], color="info", className="status-badge me-2")
            )
        else:
            indicators.append(
                dbc.Badge([
                    html.I(className="fas fa-robot me-1"),
                    "No Model"
                ], color="secondary", className="status-badge me-2")
            )
        
        # Data count with icon
        indicators.append(
            dbc.Badge([
                html.I(className="fas fa-database me-1"),
                f"{data_count:,} Records"
            ], color="primary", className="status-badge me-2")
        )
        
        return html.Div(indicators, className="mb-3")
        
    except Exception as e:
        logger.error(f"Error updating status indicators: {e}")
        return dbc.Alert("Error loading status", color="danger")

@app.callback(
    Output('current-readings', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_current_readings(n):
    """Update current sensor readings"""
    try:
        latest_data = data_logger.get_latest_data(n_rows=1)
        
        if latest_data is None or latest_data.empty:
            return dbc.Alert("No current data available", color="warning")
        
        data = latest_data.iloc[0]
        
        # Create metric cards
        cards = dbc.Row([
            dbc.Col([
                create_metric_card("PM2.5", data['pm25'], "μg/m³", 
                                 color='danger' if data['pm25'] > config.PM25_THRESHOLD else 'success')
            ], width=3),
            dbc.Col([
                create_metric_card("PM10", data['pm10'], "μg/m³",
                                 color='danger' if data['pm10'] > config.PM10_THRESHOLD else 'success')
            ], width=3),
            dbc.Col([
                create_metric_card("Temperature", data['temperature'], "°C", color='info')
            ], width=3),
            dbc.Col([
                create_metric_card("Humidity", data['humidity'], "%", color='primary')
            ], width=3)
        ])
        
        # Add timestamp
        timestamp = pd.to_datetime(data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        timestamp_info = html.P(f"Last updated: {timestamp}", className="text-muted text-center mt-2")
        
        # Add alerts for unhealthy levels
        alerts = []
        if data['pm25'] > config.PM25_THRESHOLD:
            alerts.append(create_alert_card(f"⚠️ PM2.5 level ({data['pm25']:.1f} μg/m³) exceeds safe threshold", "warning"))
        if data['pm10'] > config.PM10_THRESHOLD:
            alerts.append(create_alert_card(f"⚠️ PM10 level ({data['pm10']:.1f} μg/m³) exceeds safe threshold", "warning"))
        
        return html.Div([cards, timestamp_info] + alerts)
        
    except Exception as e:
        logger.error(f"Error updating current readings: {e}")
        return dbc.Alert("Error loading current readings", color="danger")

@app.callback(
    Output('realtime-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_realtime_chart(n):
    """Update real-time trend chart"""
    try:
        # Get last 24 hours of data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        data = data_logger.get_data_range(
            start_time.isoformat(),
            end_time.isoformat()
        )
        
        if data is None or data.empty:
            return go.Figure().add_annotation(
                text="No data available for the last 24 hours",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Create subplots
        fig = go.Figure()
        
        # PM2.5 and PM10
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['pm25'],
            mode='lines',
            name='PM2.5',
            line=dict(color=COLORS['danger'], width=2),
            yaxis='y1'
        ))
        
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['pm10'],
            mode='lines',
            name='PM10',
            line=dict(color=COLORS['warning'], width=2),
            yaxis='y1'
        ))
        
        # Temperature and Humidity on secondary axis
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['temperature'],
            mode='lines',
            name='Temperature',
            line=dict(color=COLORS['info'], width=2),
            yaxis='y2'
        ))
        
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data['humidity'],
            mode='lines',
            name='Humidity',
            line=dict(color=COLORS['primary'], width=2),
            yaxis='y2'
        ))
        
        # Add threshold lines
        fig.add_hline(y=config.PM25_THRESHOLD, line_dash="dash", 
                     line_color="red", annotation_text="PM2.5 Threshold")
        
        # Update layout
        fig.update_layout(
            title="24-Hour Air Quality Trends",
            xaxis_title="Time",
            yaxis=dict(
                title="PM2.5 & PM10 (μg/m³)",
                side="left",
                color=COLORS['danger']
            ),
            yaxis2=dict(
                title="Temperature (°C) & Humidity (%)",
                side="right",
                overlaying="y",
                color=COLORS['info']
            ),
            legend=dict(x=0.01, y=0.99),
            height=400,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating realtime chart: {e}")
        return go.Figure().add_annotation(
            text=f"Error loading chart: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

@app.callback(
    Output('predictions-display', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_predictions_display(n):
    """Update predictions display"""
    try:
        # Get latest predictions
        predictions = prediction_system.force_prediction()
        
        if 'error' in predictions:
            return dbc.Alert(f"Prediction error: {predictions['error']}", color="danger")
        
        cards = []
        
        for horizon, pred_data in predictions.items():
            if 'error' in pred_data:
                continue
                
            card = dbc.Card([
                dbc.CardHeader(html.H5(f"🔮 {horizon} Forecast")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P(f"PM2.5: {pred_data['pm25']:.1f} μg/m³", 
                                  className=f"text-{'danger' if pred_data['pm25'] > config.PM25_THRESHOLD else 'success'}"),
                            html.P(f"PM10: {pred_data['pm10']:.1f} μg/m³",
                                  className=f"text-{'danger' if pred_data['pm10'] > config.PM10_THRESHOLD else 'success'}")
                        ], width=6),
                        dbc.Col([
                            html.P(f"Temp: {pred_data['temperature']:.1f}°C"),
                            html.P(f"Humidity: {pred_data['humidity']:.1f}%")
                        ], width=6)
                    ]),
                    html.Small(f"Model: {pred_data['model_type']}", className="text-muted")
                ])
            ], className="mb-2")
            
            cards.append(card)
        
        return html.Div(cards)
        
    except Exception as e:
        logger.error(f"Error updating predictions: {e}")
        return dbc.Alert("Error loading predictions", color="danger")

@app.callback(
    Output('accuracy-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_accuracy_chart(n):
    """Update accuracy chart"""
    try:
        accuracy_summary = prediction_system.get_accuracy_summary(days=7)
        
        if not accuracy_summary:
            return go.Figure().add_annotation(
                text="No accuracy data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        fig = go.Figure()
        
        # Extract data for plotting
        models = []
        horizons = []
        mae_pm25 = []
        
        for model_type, model_data in accuracy_summary.items():
            for horizon, metrics in model_data.items():
                models.append(f"{model_type}")
                horizons.append(horizon)
                mae_pm25.append(metrics['mae_pm25'])
        
        if mae_pm25:
            fig.add_trace(go.Bar(
                x=[f"{m} {h}" for m, h in zip(models, horizons)],
                y=mae_pm25,
                name='MAE PM2.5',
                marker_color=COLORS['primary']
            ))
        
        fig.update_layout(
            title="Prediction Accuracy (MAE PM2.5)",
            xaxis_title="Model & Horizon",
            yaxis_title="Mean Absolute Error (μg/m³)",
            height=300
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating accuracy chart: {e}")
        return go.Figure().add_annotation(
            text=f"Error loading accuracy: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

@app.callback(
    Output('comparison-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_comparison_chart(n):
    """Update historical vs predicted comparison chart"""
    try:
        # Get recent predictions with actual values
        predictions_df = prediction_system.get_latest_predictions(hours=48)
        
        if predictions_df is None or predictions_df.empty:
            return go.Figure().add_annotation(
                text="No prediction comparison data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        # Filter for completed predictions (with actual values)
        completed = predictions_df.dropna(subset=['actual_pm25'])
        
        if completed.empty:
            return go.Figure().add_annotation(
                text="No completed predictions for comparison",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
        
        fig = go.Figure()
        
        # Plot predicted vs actual for PM2.5
        fig.add_trace(go.Scatter(
            x=completed['prediction_time'],
            y=completed['predicted_pm25'],
            mode='markers+lines',
            name='Predicted PM2.5',
            line=dict(color=COLORS['primary'], dash='dash'),
            marker=dict(symbol='circle')
        ))
        
        fig.add_trace(go.Scatter(
            x=completed['prediction_time'],
            y=completed['actual_pm25'],
            mode='markers+lines',
            name='Actual PM2.5',
            line=dict(color=COLORS['danger']),
            marker=dict(symbol='x')
        ))
        
        fig.update_layout(
            title="Predicted vs Actual PM2.5 (Last 48 Hours)",
            xaxis_title="Time",
            yaxis_title="PM2.5 (μg/m³)",
            height=400,
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error updating comparison chart: {e}")
        return go.Figure().add_annotation(
            text=f"Error loading comparison: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

if __name__ == "__main__":
    print("Starting Air Quality AI Dashboard...")
    print(f"Dashboard will be available at: http://localhost:{config.DASHBOARD_PORT}")
    
    app.run(
        host=config.DASHBOARD_HOST,
        port=config.DASHBOARD_PORT,
        debug=config.DASHBOARD_DEBUG
    )
