import numpy as np
import pandas as pd
import sys
import random
from termcolor import colored
import time

from auctioneer import Auctioneer
from auction import Auction
from nxplot import NXPlot, Animate

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from signal import pthread_kill, SIGTSTP

params = dict(
    nnodes = 35,
    buyer = dict(
                n = 12,
                nmax = 100,
                factor = random.uniform(.5, .8),
                max_price = 15,
                max_quantity = 10,
                flow = -1
                ),
    seller = dict(
                n = 5,
                mmax = 80,
                factor = random.uniform(1.2, 1.5),
                max_price = 15,
                max_quantity = 10,
                flow = 1
                ),
    option = False,
    noise = True,
    rounds = 25,
    mingroupsize = 2,
    maxgroupsize = 5,
    )


def get_new_data():
    start = time.time()
    while True:
        try:
            df = do_round()
            t = round(time.time()-start,2)
            print('t=',t)
            time.sleep(.1)
        except KeyboardInterrupt:
            pthread_kill(executor, SIGTSTP)
            exit()

def do_round():
    global auction_round, fig, params
    df = auctioneer.run_auctions(auction_round, params)
    fig = animation.plot_update(df)
    print_round()
    auction_round += 1

def print_round():
    global auction_round, params
    print('round', auction_round, 
          ': nbuyers=', params['buyer']['n'], 
          ', nsellers=', params['seller']['n'],
          ', nframes=', len(animation.fig['frames']))
    if len(sys.argv) > 1:
        for auction in auctioneer.auctions_history[auction_round]:
            print(auction, '\t')
    sys.stdout.flush()
    sys.stderr.flush()
 

def make_layout():
    global fig, params
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
                    value=params['buyer']['n'], 
                    tooltip={'placement': 'bottom'}
                ),
                html.Label('nsellers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-sellers',
                    min=0,
                    max=100,
                    value=params['seller']['n'],
                    tooltip={'placement': 'bottom'}
                )
            ],
            style={'display': 'grid', 'grid-template-columns': '10% 35% 10% 35%'}
        ),
        html.Div(id='hidden-div')  
        ])


app = dash.Dash(__name__)
executor = ThreadPoolExecutor(max_workers=1)
    
auction_round = 0
auctioneer = Auctioneer(params)
df = auctioneer.save_frame()
animation = Animate()
fig = animation.plot(df)

app.layout = make_layout

@app.callback(
    Output('hidden-div', 'children'),[
    Input('n-slider', 'value'), Input('m-slider', 'value')
    ]
)
def update_output(n, m):
    global params
    params['buyer']['n'] = n
    params['seller']['n'] = m


# Execute with parameters
if __name__ == '__main__':
    if len(sys.argv) > 1:
        executor.submit(get_new_data)
        app.run_server(debug=True, use_reloader=False) 
    else:
        get_new_data()

