import dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash(__name__)


def compute_expensive_data():
    """Updates the global variable 'data' with new data"""
    global data
    data = np.random.normal(size=1000)
    return data


compute_expensive_data()
app.layout = html.Div([
        dcc.Graph(
            id='chart',
            figure={
                'data': [go.Histogram(x=data)],
                'layout': {'title': 'Fig'}
            }
        ),
                        
        # Hidden div inside the app that stores the intermediate value
        html.Div(id='intermediate-value', style={'display': 'none'}, children = data),
        
        dcc.Interval(
            id='interval-component',
            interval=20*100 # 20 seconds in milliseconds
        )
        
    ])
        
@app.callback(
    Output('chart', 'figure'),
    [Input('intermediate-value', 'children')])
def render(dat):
    global data
    data = dat
    
    return data
    
@app.callback(Output('intermediate-value', 'children'),
              [Input('interval-component', 'interval')])
def update_global_var(n):
    return compute_expensive_data()

if __name__ == '__main__':
    app.run_server(debug=True)
