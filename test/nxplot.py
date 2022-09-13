import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import seaborn as sns
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import plotly.subplots as sp
import plotly.graph_objects as go
import plotly.colors as cm 

import networkx as nx
import numpy as np

sns.set()
cscale = 'portland'
cscale2 = 'plasma'

class Animate:

    fig = None
    num_frames = 0
    ntraces = 0
    nodes = []
    corr_nodes = []

    def __init__(self):
        self.fig = sp.make_subplots(
                                    rows=2, 
                                    cols=2, 
                                    column_widths=[1, 1],
                                    row_heights=[1, 1],
                                    subplot_titles = ('', '', '', ''),
                                    specs=[
                                            [{'type': 'scatter3d'},
                                             {'type': 'scatter3d'}],
                                            [{'type': 'contour'},
                                             {'type': 'contour'}],
                                        ],
                                        horizontal_spacing = 0.1,
                                        vertical_spacing = 0.05
                                    )

    def plot(self, df):
        rf = df['0']
        mat = rf['adj']
        edges = rf['edges']
        nodes = [node for node in mat.axes[0]]
        types = [node.type for node in nodes]
        nbuyers = types.count('buyer')
        nsellers = types.count('seller')
        ids = sorted([node.id for node in nodes])

        corr = mat.corr()
        links = corr.stack().reset_index()
        links.columns = ['b', 's', 'v']
        corr_edges = links.loc[ (links['v'] > 0) & (links['b'] != links['s']) ]
        
        nodekv = dict([(node.id, node.__dict__()) for node in nodes])
        buyers = sorted(nodes, key=lambda x: x.type)[:nbuyers]
        sellers = sorted(nodes, key=lambda x: x.type)[:nsellers]
        nodes = edges.drop(columns='weight').stack()
        corr_nodes = corr_edges.drop(columns='v').stack()

        self.fig.add_trace(
                        go.Scatter3d(
                            x=[v.pos[0] for v in nodes],
                            y=[v.pos[1] for v in nodes],
                            z=[v.pos[2] for v in nodes],
                            hovertext=[v.id for v in nodes],
                            ids=ids,
                            hovertemplate='<b>%{hovertext}</b><extra></extra>',
                            showlegend=False,
                            marker = {  
                                        'color': [v.color for v in nodes],
                                        'colorscale': cscale
                                    },
                            ),
                         row=1, 
                         col=1
                         )
        self.fig.add_trace(
                        go.Scatter3d(
                            x=[v.pos[0] for v in corr_nodes],
                            y=[v.pos[1] for v in corr_nodes],
                            z=[v.pos[2] for v in corr_nodes],
                            hovertext=[v.id for v in corr_nodes],
                            ids=ids,
                            hovertemplate='<b>%{hovertext}</b><extra></extra>',
                            showlegend=False,
                            marker = {  
                                        'color': [v.color for v in corr_nodes],
                                        'colorscale': cscale
                                    }
                            ),
                         row=1, 
                         col=2
                         )
        self.fig.add_trace(
                        go.Contour(
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
                            ),
                         row=2, 
                         col=1
                         )
        self.fig.add_trace(
                        go.Contour(
                            x=ids,
                            y=ids,
                            z=mat.corr(),
                            hovertemplate='<b>%{z}</b><extra></extra>',
                            ids=ids,
                            showlegend=False,
                            contours = {'coloring': 'heatmap'},
                            colorscale = cscale2,
                            line = {'width': 0},
                            showscale=False
                            ),
                         row=2, 
                         col=2
                         )
        self.ntraces = 4
 
        keys = [df['f']]
        self.num_frames += len(keys) 

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

        margin = {'l': 10, 'r': 10, 't': 15, 'b': 5}
    
        self.fig.update_layout(height=600, showlegend=False,  updatemenus=updatemenus, sliders=[sliders], margin=margin)
        self.frames = self.fig['frames']
        return self.fig


    def plot_update(self, df):
        keys = np.array(df['f'].values, dtype=str)
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
        raw_frames = [(k,df[k]) for k in keys]
        mat = dict([(k,rf['adj']) for k,rf in raw_frames])
        edges = dict([(k,rf['edges']) for k,rf in raw_frames])
        nodes = dict([(k,[node for node in mat[k].axes[0]]) for k in keys])
        types = [node.type for node in nodes[keys[0]]]
        nbuyers = types.count('buyer')
        nsellers = types.count('seller')
        ids = dict([(k,sorted([node.id for node in nodes[k]])) for k in keys])

        corr = dict([(k,mat[k].corr()) for k in keys])
        links = [(k,corr[k].stack().reset_index()) for k in keys]
        for k,link in links:
            link.columns = ['b', 's', 'v']
        corr_edges = dict([(k,link.loc[(link['v'] > 0) & (link['b'] != link['s'])]) for k,link in links])
        
        nodes = dict([(k,edges[k].drop(columns='weight').stack()) for k in keys])
        corr_nodes = dict([(k,corr_edges[k].drop(columns='v').stack()) for k in keys])

        frames = tuple(
                    [dict( 
                        name=k,
                        data=[
                            go.Scatter3d(
                                x=[v.pos[0] for v in nodes[k]],
                                y=[v.pos[1] for v in nodes[k]],
                                z=[v.pos[2] for v in nodes[k]],
                                ids=ids[k]
                            ),
                            go.Scatter3d(
                                x=[v.pos[0] for v in corr_nodes[k]],
                                y=[v.pos[1] for v in corr_nodes[k]],
                                z=[v.pos[2] for v in corr_nodes[k]],
                                ids=ids[k]
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

        return self.fig

    def show(self):
        self.fig.show()

    
