#!/usr/bin/env python3
"""
Simple test dashboard to check if web server works
"""

try:
    import dash
    from dash import html, dcc
    import plotly.graph_objs as go
    from datetime import datetime
    
    print("✅ All packages imported successfully")
    
    # Create simple Dash app
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.H1("🌬️ Air Quality AI - Test Dashboard", 
                style={'textAlign': 'center', 'color': '#2E86AB'}),
        html.Hr(),
        html.Div([
            html.H3("✅ System Status: RUNNING"),
            html.P(f"🕐 Server started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
            html.P("🌐 Dashboard is working correctly!"),
            html.P("🔧 If you see this page, the web server is functioning."),
        ], style={'margin': '20px', 'padding': '20px', 'border': '1px solid #ddd'}),
        
        # Simple graph
        dcc.Graph(
            id='test-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=[1, 2, 3, 4, 5],
                        y=[10, 11, 12, 13, 14],
                        mode='lines+markers',
                        name='Test Data'
                    )
                ],
                'layout': {
                    'title': 'Test Graph - Air Quality Simulation',
                    'xaxis': {'title': 'Time'},
                    'yaxis': {'title': 'Value'}
                }
            }
        )
    ])
    
    if __name__ == '__main__':
        print("🚀 Starting test dashboard...")
        print("🌐 Open your browser and go to: http://localhost:8050")
        print("🛑 Press Ctrl+C to stop the server")
        
        app.run_server(
            debug=True,
            host='0.0.0.0',  # Allow external connections
            port=8050,
            dev_tools_hot_reload=False
        )
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Please install missing packages:")
    print("   pip3 install --user dash plotly")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Please check the error message above")
