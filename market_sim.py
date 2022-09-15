import numpy as np
import pandas as pd
import sys
import random
import seaborn as sns
from termcolor import colored
import time
import networkx as nx

from auctioneer import Auctioneer
from auction import Auction

import plotly.subplots as sp
import plotly.graph_objects as go
import plotly.colors as cm 
from models import Clock
from node import Node

sns.set()
cscale1 = 'portland'
cscale2 = 'plasma'

# Note: pandas df edge per row

class MarketSim:

    num_frames = 0
    fig = None
    ntraces = 0
    end_time = 0
    auctioneer = Auctioneer()

    def __init__(self, make_params):
        global params, mk
        params = make_params()
        mk = self.auctioneer
        mk.make_params = make_params
        mk.make_graph()
        self.fig = sp.make_subplots(
                        rows=1, 
                        cols=2, 
                        column_widths=[1, 1],
                        row_heights=[1],
                        subplot_titles = ('', '', '', ''),
                        specs=[[{'type':'scatter3d'},
                                {'type':'parcoords'}]],
                        horizontal_spacing = 0.01,
                        vertical_spacing = 0.01
                        )
        df = mk.save_frame(params['start_time'])
        #self.plot(df)

    def do_round(self, rnum):
        global mk
        start = time.time()
        df,clock = mk.run_auctions(rnum)
        self.end_time = time.time()
        self.read_clock(clock, 1)
        #self.plot_update(df)
        return self.fig 

    def plot(self, df):
        rf = df['0']
        mat = rf['adj']
        edges = rf['edges']
        nodes = [node for node in mat.axes[0]]
        ids = sorted([node.id for node in nodes])

        #nodekv = dict([(node.id, node.__dict__()) for node in nodes])

        print(self.fig)
        print(edges)
        self.add_scatter3d(nodes, ids, cscale1, row=1, col=1)
        self.add_lines(edges, ids, cscale1, row=1, col=1)
        self.add_parcoords(nodes, cscale1, row=1, col=2)
        #self.add_contour(mat, ids, cscale2,row=2, col=1)
        #self.add_contour(mat.corr(), ids, cscale2,row=2, col=2)
       
        keys = [df['f']]
        self.num_frames += len(keys) 

        updatemenus, sliders = self.make_menus(keys)

        margin = {'l': 10, 'r': 10, 't': 15, 'b': 5}
        scene = {'aspectratio' : {'x':10,'y':1,'z':3}}
        self.fig.update_layout(
                                height=600, 
                                showlegend=False,  
                                updatemenus=updatemenus, 
                                sliders=[sliders], 
                                margin=margin,
                                scene=scene
                                )
        self.frames = self.fig['frames']

    def read_clock(self, clock, ts):
        global mk
        params = mk.make_params()
        print('\n\n',clock.nodes)
        print('\n\n',clock.T)
        for c in clock.T:
            cf = nx.to_pandas_edgelist(c)
            print(c.nodes)
            print(c.edges)
            print(cf.T)
        
        cf = nx.to_pandas_edgelist(clock.T)
        levels = [cf.loc[ cf['weight'] == node.ts] for node in Clock.T]
        print(cf)
        print(levels)
        print(levels[0]['weight'])

        return cf

    def print_round(self, rnum):
        global mk
        print('round', rnum,
              ': nbuyers=', mk.nbuyers(), 
              ', nsellers=', mk.nsellers(),
              ', nframes=', len(self.fig['frames']))
        #print(nx.to_pandas_adjacency(auctioneer.G))
        #if len(sys.argv) > 1:
        #    for auction in auctioneer.auctions_history[auction_round]:
        #        print(auction, '\t')
        sys.stdout.flush()
        sys.stderr.flush()

    def plot_clock(self, clock, row, col):
        self.read_clock(clock,1)
        return
        global mk
        params = mk.make_params()
        buyers = mk.buyer_list()
        sellers = mk.seller_list()
        inf = np.array([
                        [-1 for v in mk.seller_list(buyer)
                        ] for buyer in buyers], dtype=object
                    ).flatten()
        values = [v.id for v in clock.inf_nodes()]
        rand = np.random.randint(0,len(inf), size=len(values))
        for i in range(len(values)):
            inf[rand[i]] = values[i]
        nbrs = np.array([
                    [-1 for v in self.seller_list(buyer)
                    ] for buyer in buyers], dtype=object
                ).flatten()
        values = np.array([
                        [v.id for v in n.neighbors
                        ] for n in clock.inf_nodes()], dtype=object
                    ).flatten(),
        rand = np.random.randint(0,len(nbrs), size=len(values))
        for i in range(len(values)):
            nbrs[rand[i]] = values[i]
        self.fig.add_trace(go.Parcoords(
            line = dict(
                        color = np.array([
                                    [buyer.color for v in self.seller_list(buyer)
                                    ] for buyer in buyers]
                                ).flatten(),
                        colorscale = cscale1,
                    ),
            dimensions = list([
                dict(
                    range = [1, self.nbuyers()],
                    label = 'Auction', 
                    values = np.array([
                                [buyer.id for v in self.seller_list(buyer)
                                ] for buyer in buyers], dtype=object
                            ).flatten()
                ),
                dict(
                    range = [1, params['seller']['max_price']],
                    label = 'Price', 
                    values = np.array([
                                    [v.price for v in self.seller_list(buyer)
                                    ] for buyer in buyers], dtype=object
                            ).flatten()
                ),
                dict(
                    range = [1, params['buyer']['max_price']],
                    label = 'Bid', 
                    values = np.array([
                                    [buyer.price for v in self.seller_list(buyer)
                                    ] for buyer in buyers], dtype=object
                                    ).flatten()
                ),
               dict(
                    range = [-1, max([v.id for v in buyers])],
                    tickvals = [v.id for v in clock.inf_nodes()],
                    label = 'Winners', 
                    values = nbrs
                 ),
               dict(
                    range = [-1, max([v.id for v in buyers])],
                    tickvals = np.array([
                                    [v.id for v in n.neighbors
                                    ] for n in clock.inf_nodes()], dtype=object
                                ).flatten(),
                    label = 'Influence', 
                    values = inf
                )
               ]) 
               ), row=row, col=col)
        self.ntraces+=1
 


    def add_parcoords(self, nodes, cscale, row, col):
        self.fig.add_trace(go.Parcoords(
            line = dict(
                        color = [v.color for v in nodes],
                        colorscale = cscale,
                    ),
            dimensions = list([
                dict(
                    label = 'Node', 
                    values = [v.id for v in nodes]),
                dict(
                    label = 'Price', 
                    values = [v.price for v in nodes]),
                dict(
                    label = 'Value', 
                    values = [v.private_value for v in nodes]),
                dict(
                    label = 'Demand', 
                    values = [v.demand for v in nodes]),
                ])
            ), row=row, col=col)
        self.ntraces+=1

    def add_scatter_plots(self):
        self.add_scatter3d(nodes, edges, ids, cscale1, row=1, col=1)
        corr = mat.corr()
        links = corr.stack().reset_index()
        links.columns = ['b', 's', 'v']
        corr_edges = links.loc[ (links['v'] > 0) & (links['b'] != links['s']) ]
        G = nx.from_pandas_edgelist(corr_edges, 'b', 's')
        pos = nx.spectral_layout(G, dim=3)
        for v in nodes:
            v.pos = pos[v]
        self.add_scatter3d(nodes, corr_edges, ids, cscale1, row=1, col=2)
        
    def add_scatter3d(self, nodes, ids, cscale, row, col):
        self.fig.add_trace(go.Scatter3d(
                            x=[v.pos[0] for v in nodes],
                            y=[v.pos[1] for v in nodes],
                            z=[v.pos[2] for v in nodes],
                            hovertext=[v.type for v in nodes],
                            ids=ids,
                            hovertemplate='<b>%{hovertext}</b><extra></extra>',
                            showlegend=False,
                            mode = 'markers',
                            surfacecolor = 'darkorchid',
                            surfaceaxis = 2,
                            opacity = 0.5,
                            marker = {  
                                        'color': [v.color for v in nodes],
                                        'colorscale': cscale,
                                        'size' : 5
                                    },
                            ), row=row, col=col)
        self.ntraces+=1

    def add_lines(self, edges, ids, cscale, row, col):
        edge_pos = np.array([(u.pos, v.pos) for u,v,w,z in edges.values])
        for v in edge_pos:
            self.fig.add_trace(go.Scatter3d(
                                x=v.T[0],
                                y=v.T[1],
                                z=v.T[2],
                                mode='lines',
                                line = {  
                                        'colorscale': cscale1,
                                        'width' : 1
                                    },
                            ), row=row, col=col)
        self.ntraces += 1

    def add_surface(self, nodes, edges, ids, cscale, row, col):
        pos = np.array([[u.pos, v.pos] for u,v,z in edges.values])
        print([v for v in pos.T[0]])
        self.fig.add_trace(go.Mesh3d(
                            x=[v.pos[0] for v in nodes], 
                            y=[v.pos[1] for v in nodes],
                            z=[v.pos[2] for v in nodes],
                            colorscale = cscale1
                        ), row=row, col=col)
        self.ntraces += 1
  
    def add_contour(self, mat, ids, cscale, row, col):
        self.fig.add_trace(go.Contour(
                            x=ids,
                            y=ids,
                            z=mat,
                            hovertemplate='<b>%{z}</b><extra></extra>',
                            ids=ids,
                            showlegend=False,
                            contours = {'coloring': 'heatmap'},
                            colorscale = cscale2,
                            line = {'width': 0},
                            showscale=False
                            ), row=row, col=col)
        self.ntraces+=1
    
    def update_scatter_plots(self):
        corr = dict([(k,mat[k].corr()) for k in keys])
        links = [(k,corr[k].stack().reset_index()) for k in keys]
        for k,link in links:
            link.columns = ['b', 's', 'v']
        corr_edges = dict([(k,link.loc[(link['v'] > 0) & (link['b'] != link['s'])]) for k,link in links])
        
        corr_nodes = dict([(k,corr_edges[k].drop(columns='v').stack()) for k in keys])
      
    def plot_update(self, df):
        keys = np.array(df['f'].values, dtype=str)
        args, steps = self.update_menus(keys)
        raw_frames = [(k,df[k]) for k in keys]
        mat = dict([(k,rf['adj']) for k,rf in raw_frames])
        edges = dict([(k,rf['edges']) for k,rf in raw_frames])
        nodes = dict([(k,[node for node in mat[k].axes[0]]) for k in keys])
        ids = dict([(k,sorted([node.id for node in nodes[k]])) for k in keys])

        nodes = dict([(k,edges[k].drop(columns='weight').stack()) for k in keys])

        frames = tuple(
                    [dict( 
                        name=k,
                        data=[
                            go.Scatter3d(
                                x=[v.pos[0] for v in nodes[k]],
                                y=[v.pos[1] for v in nodes[k]],
                                z=[v.pos[2] for v in nodes[k]],
                                ids=ids[k],
                                hovertext=[v.type for v in nodes[k]],
                                marker = {  
                                        'color': [v.color for v in nodes[k]],
                                    },
                            ),
                            go.Contour(
                                x=ids[k],
                                y=ids[k],
                                z=mat[k],
                                ids=ids[k]
                            ),
                            go.Contour(
                                x=ids[k],
                                y=ids[k],
                                ids=ids[k],
                                z=mat[k].corr(),
                            ),
                            ],
                        traces=[n for n in range(self.ntraces)]
                        ) for k in keys]
                        )
        self.fig['frames'] += frames
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

    def make_menus(self, keys):

        updatemenus = [
            dict(
                type='buttons',
                buttons=[
                dict(
                    label='Play',
                    method='animate',
                    args=[
                        [f'{k}' for k in keys],
                        dict(
                            frame=
                            dict(duration=500, redraw=True),
                            transition=dict(duration=0),
                            easing='linear',
                            fromcurrent=True,
                            mode='immediate'
                        )]
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
                    'steps': [{
                        'args': [
                            [k], {
                                'frame': {
                                      'duration': 0, 
                                      'redraw': True
                                }, 
                                'mode': 'immediate', 
                                'fromcurrent': True, 
                                'transition': {
                                      'duration': 0, 
                                      'easing': 'linear',
                                      'order': 'traces first'
                                }
                        }],
                        'label': k, 
                        'method': 'animate'
                        } for k in keys
                    ],
                    'transition': {'duration': 0, 
                                    'easing': 'linear'
                    },
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 0,
                    'yanchor': 'top'
                }

        return updatemenus, sliders

    def show(self):
        self.fig.show()

       
   
