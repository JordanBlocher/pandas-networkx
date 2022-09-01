import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import dash
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import plotly.graph_objs as go
import numpy as np

# number of seconds between re-calculating the data                                                                                                                           
UPDADE_INTERVAL = 5

def get_new_data():
    """Updates the global variable 'data' with new data"""
    global data
    data = np.random.normal(size=1000)
    return data


def get_new_data_every(period=UPDADE_INTERVAL):
    """Update the data every 'period' seconds"""
    while True:
        get_new_data()
        print("data updated")
        time.sleep(period)


def make_layout():
    chart_title = "data updates server-side every {} seconds".format(UPDADE_INTERVAL)
    return html.Div([
        dcc.Graph(
            id='chart',
            figure={
                'data': [go.Histogram(x=data)],
                'layout': {'title': 'Fig'}
            }
        ),
        html.Div(id='callback', style={'display': 'none'}, children = data)
        ]
    )

app = dash.Dash(__name__)

# get initial data                                                                                                                                                            
get_new_data()

# we need to set layout to be a function so that for each new page load                                                                                                       
# the layout is re-created with the current data, otherwise they will see                                                                                                     
# data that was generated when the Dash app was first initialised                                                                                                             
app.layout = make_layout

@app.callback(
   Output('chart', 'figure'), [Input('callback', 'children')]
)
def update_graph_with_correct_df(_):
    ### the input value really doesn't matter, hence the "_"
    global data
    fig = dcc.Graph(
            id='chart',
            figure={
                'data': [go.Histogram(x=data)],
                'layout': {'title': 'Fig'}
            }
        )
    return data
   

if __name__ == '__main__':
    # Run the function in another thread
    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(get_new_data_every)
    app.run_server(debug=True)
