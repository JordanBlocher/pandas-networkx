import numpy as np
import pandas as pd
import sys
import random
from termcolor import colored
import time

from auctioneer import Auctioneer
from auction import Auction
from nxplot import NXPlot, Animate
import networkx as nx

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from signal import pthread_kill, SIGTSTP


def get_new_data():
    global start_time
    while True:
        try:
            df = do_round(start_time)
            t = round(time.time()-start_time,2)
            print('t=',t)
            time.sleep(.1)
        except KeyboardInterrupt:
            pthread_kill(executor, SIGTSTP)
            exit()

def do_round(start_time):
    global auction_round, fig
    df = auctioneer.run_auctions(auction_round)
    fig = animation.plot_update(df)
    print_round()
    auction_round += 1

def print_round():
    global auction_round, nbuyers, nsellers
    print('round', auction_round, 
          ': nbuyers=', nbuyers, 
          ', nsellers=', nsellers,
          ', nframes=', len(animation.fig['frames']))
    if len(sys.argv) > 1:
        for auction in auctioneer.auctions_history[auction_round]:
            print(auction, '\t')
    sys.stdout.flush()
    sys.stderr.flush()
   
   

app = dash.Dash(__name__)
executor = ThreadPoolExecutor(max_workers=1)
  

def make_params():
    global start_time, nsellers, nbuyers
    MNSZE = 200
    rng = nx.utils.create_random_state()
    
    max_price = 15
    nsellers = 11
    nbuyers = 17
 
    inc_max = 1, #1.5
    inc_min = .9, #1.2
    dec_max = 0.9, #0.7
    dec_min = 0.8, #0.3

    return dict(
    option = False,
    noise = False,
    max_price = max_price,
    nsellers = nsellers,
    nbuyers = nbuyers,
    # nnodes, g_mod, and nbuyers/sellers are not independent, 
    # there should be an optimal
    # formula for EQ
    nnodes = nbuyers+nsellers,
    price = rng.poisson(max_price, size=MNSZE),
    g_max = min(nbuyers, nsellers)-2,
    noise_factor = dict(
                        low = .2, #nOTE: TRY NEGATIVE VALUES
                        high = 1.2,
        ),
    buyer = dict(
            init_factor = rng.uniform(.5, .8), # bid under
            max_price = 15,
            max_quantity = 10,
            flow = -1,

            ),
    inc_factor = rng.uniform(
                            inc_min, 
                            inc_max, 
                            size=MNSZE
                            ),
    dec_factor = rng.uniform(
                            dec_min, 
                            dec_max, 
                            size=MNSZE
                            ),
    seller = dict(
            init_factor = rng.uniform(1.2, 1.5), # bid over
            max_price = 15,
            max_quantity = 10,
            flow = 1,
            increase_max = 1,
            increase_min = .1,
            decrease_max = 1,
            decrease_min = .1,
            )
        )

def make_layout():
    global fig, params
    params = make_params()
    return html.Div(
        [
        dcc.Graph(
            id='price', 
            figure=fig, 
            animate=True
        ),
        html.Br(),
        html.Div(
            [
                html.Label('nbuyers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-buyers',
                    min=0,
                    max=100,
                    value=params['nbuyers'], 
                    tooltip={'placement': 'bottom'}
                ),
                html.Label('nsellers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-sellers',
                    min=0,
                    max=100,
                    value=params['nsellers'],
                    tooltip={'placement': 'bottom'}
                )
            ],
            style={'display': 'grid', 'grid-template-columns': '10% 35% 10% 35%'}
        ),
        html.Div(id='hidden-div')  
        ])

global start_time
auction_round = 0
start_time = time.time()     

auctioneer = Auctioneer(make_params, start_time)
df = auctioneer.save_frame()
animation = Animate()
fig = animation.plot(df)

app.layout = make_layout

@app.callback(
    Output('hidden-div', 'children'),[
    Input('n-buyers', 'value'), Input('n-sellers', 'value')
    ]
)
def update_output(n, m):
    global nbuyers, nsellers
    nbuyers = n
    nsellers = m
    auctioneer.update_params()


# Execute with parameters
if __name__ == '__main__':
    if len(sys.argv) > 1:
        executor.submit(get_new_data)
        app.run_server(debug=True, use_reloader=False) 
    else:
        get_new_data()

