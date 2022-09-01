import numpy as np
from termcolor import colored

from params import * 
from auctioneer import Auctioneer
from auction import Auction
from auction_state import AuctionState

import networkx as nx
from nxplot import NXPlot, Animate

import os
import sys
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

import dash
from dash import dcc
from dash import html

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor



def get_new_data():
    while True:
        try:
            start = time.time()
            pf = do_round()
            t = time.time()-start
            time.sleep(1)
        except KeyboardInterrupt as err:
            exit()

def do_round():
    global fig
    auction_round = 0
    pf = auctioneer.run_auctions(auction_round)
    fig = animation.price_plot_update(pf)
    print("NFRAMES",len(animation.fig['frames']))
    #print_round(auction_round)
    auction_round += 1

def print_round(round_number):
    print("Round", round_number)
    #print(nx.to_dict_of_lists(self.G))
    #print(self.G.nodes(data=True))  
    #print(self.G.edges(data=True))
    #print(nx.to_pandas_adjacency(self.G))
    n = 0
    for auction_state in self.auctions_history[round_number]:
        auction_state.print_auction_state()
        n += 1

def make_layout():
    global fig
    return html.Div(
        dcc.Graph(id='price-graph', figure=fig, animate=True),
        )


app = dash.Dash(__name__)

auctioneer = Auctioneer()
pf = auctioneer.save_frame()
animation = Animate()
fig = animation.price_plot(pf)

app.layout = make_layout

# Execute with parameters
if __name__ == '__main__':

    executor = ThreadPoolExecutor(max_workers=1)
    executor.submit(get_new_data)
    app.run_server(debug=True, use_reloader=True) 

