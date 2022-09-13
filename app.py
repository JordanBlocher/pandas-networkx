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

from market_sim import MarketSim

def get_new_data():
    while True and sim.auction_round < nrounds:
        try:
            df = do_round()
            time.sleep(.1)
        except KeyboardInterrupt:
            exit()

def do_round():
    global fig
    fig = sim.do_round()
    sim.print_round()
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

def make_params():
    global start_time, nsellers, nbuyers, noise, auction_round

    auction_round = 0
    rng = nx.utils.create_random_state()

    option = False
    nnodes = nbuyers+nsellers
    noise_low = .2, #nOTE: TRY NEGATIVE VALUES
    noise_high = 1.2

    buyer_init_factor = rng.uniform(.5, .8) # bid under
    buyer_max_price = 75
    buyer_max_quantity = 70
    buyer_inc = [.9, 1] # 1.2 1.5
    buyer_dec = [0.8, 9] #0.3 0.7

    seller_init_factor = rng.uniform(1.2, 1.5) # bid over
    seller_max_price = 95
    seller_max_quantity = 100
    seller_inc = [.1, 1]
    seller_dec = [.1, 1]

    return dict(
    auction_round = auction_round,
    option = option,
    noise = noise,
    nsellers = nsellers,
    nbuyers = nbuyers,
    # nnodes, g_mod, and nbuyers/sellers are not independent, 
    # there should be an optimal
    # formula for EQ
    nnodes = nnodes,
    g_max = min(nbuyers, nsellers)-2,
    noise_factor = dict(
                        low = noise_low,
                        high = noise_high,
        ),
    buyer = dict(
            init_factor = buyer_init_factor,
            max_price = buyer_max_price,
            max_quantity = buyer_max_quantity,
            inc = buyer_inc,
            dec = buyer_dec,
            flow = -1,
            price = []
            ),
    seller = dict(
            init_factor = seller_init_factor,
            max_price = seller_max_price,
            max_quantity = seller_max_quantity,
            inc = seller_inc,
            dec = seller_dec,
            flow = 1,
            price = []
            )
        )

def params():
    return make_params()


nbuyers = 7
nsellers = 5
noise = False
nrounds = 10

start_time = time.time()     
sim = MarketSim(make_params, start_time)
fig = sim.start()

app.layout = make_layout


# Execute with parameters
if __name__ == '__main__':
    if len(sys.argv) > 1:
        executor.submit(get_new_data)
        app.run_server(debug=True, use_reloader=False) 
    else:
        get_new_data()



