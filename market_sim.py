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
import seaborn as sns


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
    #if len(sys.argv) > 1:
    #    for auction in auctioneer.auctions_history[auction_round]:
    #        print(auction, '\t')
    sys.stdout.flush()
    sys.stderr.flush()
   
   

app = dash.Dash(__name__)
executor = ThreadPoolExecutor(max_workers=1)
  

def make_params():
    global start_time, nsellers, nbuyers, auction_round

    auction_round = 0
    rng = nx.utils.create_random_state()

    option = False
    noise = False
    nnodes = nbuyers+nsellers
    max_price = 15
    noise_low = .2, #nOTE: TRY NEGATIVE VALUES
    noise_high = 1.2

    buyer_init_factor = rng.uniform(.5, .8) # bid under
    buyer_max_price = 15
    buyer_max_quantity = 10
    buyer_inc = [.9, 1] # 1.2 1.5
    buyer_dec = [0.8, 9] #0.3 0.7

    seller_init_factor = rng.uniform(1.2, 1.5) # bid over
    seller_max_price = 12
    seller_max_quantity = 10
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

def make_layout():
    global fig, params
    params = make_params()
    return html.Div(
        [
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
        dcc.Graph(
            id='price', 
            figure=fig, 
            animate=True
        ),
        html.Br(),
        html.Div(id='hidden-div')  
        ])

global start_time
auction_round = 0
start_time = time.time()     

nsellers = 5
nbuyers = 7

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


# Execute with parameters
if __name__ == '__main__':
    if len(sys.argv) > 1:
        executor.submit(get_new_data)
        app.run_server(debug=True, use_reloader=False) 
    else:
        get_new_data()

