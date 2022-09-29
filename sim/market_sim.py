import numpy as np
import pandas as pd
import sys
import random
import seaborn as sns
from termcolor import colored
import time
import networkx as nx

from auction import Auction, Auctioneer
from nxn import nxNode, spectral_layout

import plotly.subplots as sp
import plotly.graph_objects as go
import plotly.colors as cm 
from models import Clock
from .figs import *

sns.set()
cscale1 = 'ice'
cscale2 = 'plasma'
cscale3 = 'electric'
surfcolor1 = 'royalblue'
surfcolor2 = 'deeppink'
surfcolor3 = 'lightgrey'
linecscale = 'icefire'

# Note: pandas df edge per row

class MarketSim:

    fig = None
    auctioneer = Auctioneer()
    node_history = pd.DataFrame()
    edge_history = pd.DataFrame()
    results = pd.DataFrame()

    def __init__(self, make_params):
        global params, G
        params = make_params()
        params.start_time=time.time()
        G = self.auctioneer
        G.make_params = make_params
        G.make_graph()
        df = G.run_auctions(0)
        self.node_history = self.node_history.append(df['nodes'])
        self.edge_history = self.edge_history.append(df['edges'])
        self.make_plot()

    def do_round(self, rnum):
        global G
        start = time.time()
        df = G.run_auctions(rnum)
        self.node_history = self.node_history.append(df['nodes'])
        self.edge_history = self.edge_history.append(df['edges'])
        self.results = self.results.append(df['result'])
        end_time = time.time()
        self.plot(rnum)
        return self.fig 

    def make_plot(self):
        global G
        self.fig = sp.make_subplots(
                        rows=2, 
                        cols=2, 
                        column_widths=[1, 1],
                        row_heights=[1,1],
                        subplot_titles = ('', '', '', ''),
                        specs=[[{'type':'parcoords', 'colspan':2},None],
                                [{'type': 'scatter', 'colspan':2}, None]],
                        horizontal_spacing = 0.06,
                        vertical_spacing = 0.08
                        )
        self.fig.add_trace(
                    go_parcoords(
                                self, 
                                self.node_history.stack(), 
                                'plasma',
                                params,
                                rnum=0
                            ), row=1, col=1)
        self.fig.add_trace(
                       go_scatter(
                                self, 
                                self.node_history.stack(), 
                                'plasma',
                                msize=15,
                                rnum=0
                            ), row=2, col=1)
        self.fig.add_trace(
                       go_line(
                                self, 
                                self.node_history.stack(), 
                                self.edge_history.stack(), 
                                'plasma',
                                rnum=0
                            ), row=2, col=1)
        self.ntraces=3
        updatemenus, sliders = self.make_menus()

        margin = {'l': 50, 'r': 50, 't': 65, 'b': 60}
        scene = {'aspectratio' : {'x':10,'y':5,'z':3}}
        self.fig.update_layout(
                                height=900, 
                                showlegend=False,  
                                updatemenus=updatemenus, 
                                sliders=[sliders], 
                                margin=margin,
                                scene=scene,
                                )


    def print_round(self, rnum):
        global G
        print('Round', rnum,
              ': nbuyers=', G.nbuyers(), 
              ', nsellers=', G.nsellers(),
              ', nframes=', len(self.fig['frames']))
        print('Completed:', self.result.stack())
        #if len(sys.argv) > 1:
        #    for auction in auctioneer.auctions_history[auction_round]:
        #        print(auction, '\t')
        sys.stdout.flush()
        sys.stderr.flush()
   
    def plot(self, rnum):
        global params, G
        nodes = self.node_history.stack()
        edges = self.edge_history.stack()
        keys = list(range(rnum))
        args, steps = self.update_menus([rnum])
        print("****************************HERE****************************")

        frame = tuple(
                    [dict( 
                        name=rnum,
                        data=[
                            go_parcoords(
                                self, 
                                nodes, 
                                'plasma',
                                params,
                                rnum=rnum
                            ),
                            go_scatter(
                                self, 
                                nodes, 
                                'plasma',
                                msize=15,
                                rnum=rnum
                            ),
                            go_line(
                                self, 
                                nodes, 
                                edges,
                                'plasma',
                                rnum=rnum
                            ),
                            ],
                        traces=[n for n in range(self.ntraces)]
                        )]
                        )
        print("############################HERE############################")
        self.fig['frames'] += frame

        self.fig.frames[-1]['layout']['xaxis']['range'] = [max(-0.1,rnum-5.2), rnum+.2]
        self.fig.frames[-1]['layout']['yaxis']['range'] = [-1,1]
        self.fig['layout']['updatemenus'][0]['buttons'][0]['args'] = args
        self.fig['layout']['sliders'][0]['steps'] += steps 

    def update_menus(self, keys):
        args  = tuple(
                    [[f'{k}' for k in keys],
                    dict(
                        frame=dict(duration=500, redraw=True),
                        transition=dict(duration=0),
                        easing='linear',
                        fromcurrent=True,
                        mode='immediate'
                        )
                    ])
        steps = tuple(
                    [{'args': [
                        [k], {
                            'frame':{'duration': 0, 'redraw': True}, 
                            'mode':'immediate', 
                            'fromcurrent': True, 
                            'transition':{
                                'duration': 0, 
                                'easing': 'linear'
                            }}],
                    'label': k, 
                    'method': 'animate'
                    } for k in keys]
                    )
        return args, steps

    def make_menus(self):

        menus = [
            dict(
                type='buttons',
                buttons=[
                dict(
                    label='Play',
                    method='animate',
                    ),
              dict(
                label='Pause',
                method='animate',
                args=[
                    [None],
                    dict(
                        frame=dict(duration=0, redraw=False),
                         transition=dict(duration=0),
                         mode='immediate'
                         )
                     ]
                 )],
            direction='left',
            pad=dict(r=10, t=25),
            showactive=True, 
            x=0.1, y=0, 
            xanchor='right', yanchor='top'
            )]

        sliders = {'active': 0,
                   'currentvalue': {
                                'font': {'size': 16}, 
                                'prefix': 'ts=', 
                                'visible': True, 
                                'xanchor': 'right'
                    },
                    'len': 0.9, 
                    'pad': {'b': 10, 't': 25},
                    'steps': [],
                    'transition': {'duration': 0, 
                                    'easing': 'linear'
                    },
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 0,
                    'yanchor': 'top'
                }

        return menus, sliders

    def show(self):
        self.fig.show()

       
   
