import numpy as np
import pandas as pd
import sys
import random
import time
import networkx as nx

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from sim import MarketSim
from params import make_params
from params.globals import *

def get_new_data():
    global auction_round
    while True: #and auction_round < nrounds:
        try:
            df = do_round()
            time.sleep(.1)
        except KeyboardInterrupt:
            executor.shutdown()
            exit()

def do_round():
    global fig, auction_round
    fig = sim.do_round(auction_round)
    sim.print_round(auction_round)
    auction_round += 1
    return fig


app = dash.Dash(__name__)
executor = ThreadPoolExecutor(max_workers=1)
  

def make_layout():
    global fig
    return html.Div(
        [
        html.Br(),
        dcc.Graph(
            id='price', 
            figure=fig, 
            animate=True
        ),
        html.Br(),
        ])

start_time = time.time()     
sim = MarketSim(make_params)
fig = sim.fig

app.layout = make_layout


# Execute with parameters
if __name__ == '__main__':
    if len(sys.argv) > 1:
        executor.submit(get_new_data)
        app.run_server(debug=True, use_reloader=False) 
    else:
        get_new_data()


sys.modules[__name__] = make_params

