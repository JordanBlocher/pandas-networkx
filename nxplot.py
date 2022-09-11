import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import seaborn as sns
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import plotly.subplots as sp
import plotly.graph_objects as go

import networkx as nx
import numpy as np

sns.set()
rocket = sns.color_palette('rocket', as_cmap=True)
mako = sns.color_palette('mako', as_cmap=True)
winter = sns.color_palette('winter', as_cmap=True)
cool = sns.color_palette('cool', as_cmap=True)


class Animate:

    fig = None
    num_frames = 0
    ntraces = 0

    def __init__(self):
        self.fig = sp.make_subplots(
                                    rows=2, 
                                    cols=2, 
                                    column_widths=[1, 1],
                                    row_heights=[1, 1],
                                    subplot_titles = ('', '', '', ''),
                                    specs=[
                                            [{'type': 'contour', 'colspan':2},{}],
                                            [{'type': 'scatter'},{'type': 'scatter3d'}]
                                        ],
                                    )

    def plot(self, df):
        rf = df['0']
        nodes = [eval(frame['nodes'][key]) for key in rf['nodes']]
        ndata = np.array([
                    [key for key in frame['nodes']],
                    [node['type'] for node in nodes],
                    [node['price'] for node in nodes],
                    [node['demand'] for node in nodes],
                    [node['value'] for node in nodes]
                ], dtype=object)
        pos = np.array([node['pos'] for node in nodes], dtype=object)
        color = np.array([node['color'] for node in nodes], dtype=object)
        nbuyers = list(ndata[1]).count('buyer')
        nsellers = list(ndata[1]).count('seller')
        print(nsellers)
        mat = frame['adj']
        index = frame['adj'].index
        print(frame['adj'][index[nsellers]:index[-1]])

        self.fig.add_trace(
                        go.Contour(
                            z=mat[index[df['nsellers']:index[-1]],
                            hovertemplate='<b>%{z}</b><extra></extra>',
                            ids=df['id'],
                            showlegend=False,
                            coloraxis='coloraxis1'
                            ),
                         row=1, 
                         col=1
                         )
        self.fig.add_trace(
                        go.Scatter(
                            x=df['pos'][:,0],
                            y=df['pos'][:,1],
                            ids=ndata[2],
                            showlegend=False,
                            mode='markers',
                            ),
                         row=2, 
                         col=1
                        )
        self.fig.add_trace(
                        go.Scatter3d(
                            x=pos[:,0],
                            y=pos[:,1],
                            z=pos[:,2],
                            ids=ndata[2],
                            showlegend=False,
                            mode='markers',
                            ),
                         row=2, 
                         col=2
                         )
        self.ntraces = 3
 
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
            pad=dict(r=10, t=85),
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
                    'pad': {'b': 10, 't': 60},
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
        coloraxis = {'colorscale':'magma'}
        coloraxis1 = {'colorscale':'viridis'}
    
        MAX_X = nsellers+nbuyers
        MAX_Y = max(ndata[2])
 
        self.fig.update_layout(height=900, showlegend=False,  updatemenus=updatemenus, sliders=[sliders], margin=margin)
        self.frames = self.fig['frames']
        return self.fig


    def plot_update(self, df):
        keys = np.array(df['f'].values, dtype=str)
        print(keys)
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

        raw_frames = [df[k] for k in keys]
        nodemat = [[eval(rf['nodes'][key]) for key in rf['nodes']] for rf in raw_frames]
        ndata = [np.array([
                    [node['type'] for node in nodes],
                    [node['price'] for node in nodes],
                    [node['demand'] for node in nodes],
                    [node['value'] for node in nodes],
                ], dtype=object) for nodes in nodemat]
        pos = [np.array([node['pos'] for node in nodes], dtype=object)
                    for nodes in nodemat]
        color = [np.array([node['color'] for node in nodes], dtype=object)
                    for nodes in nodemat]
        nbuyers = list(ndata[0][0]).count('buyer')
        nsellers = list(ndata[0][0]).count('seller')
        print(nsellers)
        index = [rf['adj'].index for rf in raw_frames]
        mat = [rf['adj'] for rf in raw_frames]

        frames = tuple(
                    [dict( 
                        name=k,
                        data=[
                            go.Contour(
                                z=np.array(mat[k][index[k][nsellers]:index[k][-1]]),
                                ids=ndata[k][2],
                                showlegend=False,
                            ),
                            go.Scatter(
                                x=pos[k][:,0],
                                y=pos[k][:,1],
                                ids=ndata[k][2],
                                showlegend=False,
                                mode='markers',
                            ),
                            go.Scatter3d(
                                x=pos[k][:,0],
                                y=pos[k][:,1],
                                z=pos[k][:,2],
                                ids=ndata[k][2],
                                showlegend=False,
                                mode='markers',
                                ),
                            ],
                        traces=[n for n in range(self.ntraces)]
                        ) for k in range(len(raw_frames))]
                        )
        MAX_X = nbuyers+nsellers+2
        MAX_Y = max([max(ndata[k][1]) for k in range(len(raw_frames))])
        self.fig['frames'] += frames
        self.fig['layout']['updatemenus'][0]['buttons'][0]['args'] = args
        self.fig['layout']['sliders'][0]['steps'] += steps 
        self.fig['layout']['xaxis']['range'] = [1, MAX_X]
        self.fig['layout']['yaxis']['range'] = [1, MAX_Y]
        xaxis1 = {
                'anchor': 'x1', 
                'range': [1, MAX_X]
                }
        yaxis1 = {
                'anchor': 'y1', 
                'range': [1, MAX_Y]
                }
        xaxis2 = {
                'anchor': 'x2', 
                'range': [-1, 1]
                }
        yaxis2 = {
                'anchor': 'y2', 
                'range': [-1, 1]
                }
        self.fig.update_xaxes(xaxis1, xaxis2)
        self.fig.update_yaxes(yaxis1, yaxis2)
        return self.fig


    def show(self):
        #print("FRAMES", self.fig['frames'])
        self.fig.show()

    
    '''
    def price_plot_old(self, df):
        #self.df = self.df.append(df)
        price = px.bar(df, x='id', y='price', 
                        animation_frame='time_ms',
                        hover_name='price', animation_group='id', 
                        log_x=False, range_x=[1,MSELLERS+NBUYERS], 
                        range_y=[1,1.5*MAX_PRICE])
        price_traces = []
        for trace in range(len(price['data'])):
            price_traces.append(price['data'][trace])
        frames = []
        for t in range(len(price['frames'])):
            frames.append( dict( name = (price['frames'][t]['name']),
            data = [price['frames'][t]['data'][trace] for trace \
            in range(len(price['frames'][t]['data']))],
            traces=[0]))
        updatemenus = []
        sliders = []
        xaxis = []
        yaxis = []
        for trace in price['layout']['sliders']:
            sliders.append(trace)
        for trace in price['layout']['updatemenus']:
            updatemenus.append(trace)
        for trace in price['layout']['xaxis']:
            xaxis.append(trace)
        for trace in price['layout']['yaxis']:
            yaxis.append(trace)
        for traces in price_traces:
            self.fig.append_trace(traces, row=1, col=1)
        xaxis = {'anchor': 'y', 'domain': [0.0, 1.0], 'range': [1, MAX_NETWORK_SIZE], 'title': {'text': 'id'}}
        yaxis = {'anchor': 'x', 'domain': [0.0, 1.0], 'range': [1, 22.5], 'title': {'text': 'price'}}

        #print(sliders)
        self.fig.update_xaxes(xaxis)
        self.fig.update_yaxes(yaxis)
        self.fig.update_layout(updatemenus=updatemenus, sliders=sliders)
        self.fig.update(frames=frames)



        frames = [ dict ( name=k,
            data = [go.Bar(x=df['id'], y=df['t'])], 
            traces=[0]) for k in df['time_ms']]
        self.fig.update(frames=frames)
        pos = nx.spring_layout(self.G, dim=3, seed=779)
        # Extract node and edge positions from the layout
        node_xyz = np.array([pos[v] for v in sorted(self.G)])
        edge_xyz = np.array([(pos[u], pos[v]) for u, v in self.G.edges()])
        # Plot the nodes - alpha is scaled by "depth" automatically
        self.fig.add_scatter(*node_xyz.T, row=1, col=2)
        # Plot the edges
        for vizedge in edge_xyz:
            fig.add_trace(*vizedge.T, color="tab:gray", row=1, col=2)
        '''


class NXPlot:

    fig = []
    axes = []
    id = 1
    
    def __init__(self, subplots):
        self.fig.append(plt.figure())
        self.axes.append([])
        for n in subplots:
            self.axes[self.id-1].append(self.fig[self.id-1].add_subplot(n[0], projection=n[1]))
        self.id = NXPlot.id
        NXPlot.id += 1
        for ax in self.axes[self.id-1]:
            self.format_axes(ax)
    
    def set_axes(self, sp):
        plt.figure(self.id)
        ax = plt.subplot(sp).axes
        plt.cla()
        plt.sca(ax)
        self.format_axes(ax)
        return ax

    def format_axes(self, ax):
        ax.grid(False)
        for dim in (ax.xaxis, ax.yaxis):
            dim.set_ticks([])

    def correlation(G, auction_round):
        adj_matrix = nx.to_pandas_adjacency(self.G)
        corr = adj_matrix.corr()
        links = corr.stack().reset_index()
        links.columns = ['b', 's', 'v']
        links_filtered = links.loc[ (links['v'] > 0) & (links['b'] != links['s']) ]
        g = nx.from_pandas_edgelist(links_filtered, 'b', 's')
        self.plot.nxheatmap(adj_matrix, 121)
        self.plot.nxgraph(g, G.nodes, 122)
        self.plot.draw()

    def dendrogram(self, adj_matrix, sp):
        Z = linkage(adj_matrix.corr(), 'ward')
        dendrogram(Z, labels=adj_matrix.corr().index, leaf_rotation=0)

    def nxheatmap(self, mat, sp):
        ax = self.set_axes(sp)
        sns.heatmap(mat, ax=ax)

    def nxgraph(self, G, nodes, sp):  
        ax = self.set_axes(sp)
        color_map = []
        if nodes:
            for node in G.nodes:
                color_map.append(nodes[node]['color'])
        else:
            colormap = sns.cm
        pos = nx.spring_layout(G, dim=3, seed=779)
        nx.draw(G, ax=ax, with_labels=True, node_color=color_map)

    def nxgraph3d(self, G):
        ax = self.set_axes(sp)
        pos = nx.spring_layout(G, dim=3, seed=779)
        # Extract node and edge positions from the layout
        node_xyz = np.array([pos[v] for v in sorted(G)])
        edge_xyz = np.array([(pos[u], pos[v]) for u, v in G.edges()])
        # Plot the nodes - alpha is scaled by "depth" automatically
        ax.scatter(*node_xyz.T)
        # Plot the edges
        for vizedge in edge_xyz:
            ax.plot(*vizedge.T, color="tab:gray")
        plt.show()

    def draw(self):
        plt.figure(self.id)
        plt.draw()
        plt.pause(.1)




'''
def plot_graph(self, auction_round, winner):
    """
    Plot the bid graph
    """
    #communities = girvan_newman(self.G)

    #node_groups = []
    #for com in next(communities):  
    #    node_groups.append(list(com))

    #print(node_groups)

    color_map = []
    for seller in range(self.nsellers):
        color_map.append('blue')
    for buyer in range(self.nbuyers):
        if buyer == winner:
            color_map.append('red')
        else:
            color_map.append('green')

    plt.title("Round " + str(auction_round))
    #nx.draw_kamada_kawai(self.G, node_size=size_map, node_color=color_map, with_labels=True)
    nx.draw_shell(self.G, node_size=size_map, node_color=color_map, with_labels=True)
    #nx.draw_spectral(self.G, node_size=size_map, node_color=color_map, with_labels=True)
    plt.show()


    # Plot price history
    for seller in range(self.nsellers):
        plt.semilogy(self.market_price[:, seller], label="Seller " + str(seller))
        #plt.plot(market_prices[:, seller], label="Seller " + str(seller))

    plt.title('Price history across all rounds for each seller')
    plt.ylabel('Price')
    plt.xlabel('Rounds')
    plt.legend()

    if n_rounds < 10:
        plt.xticks(range(n_rounds)) 

    plt.figure()
    for seller in range(sellers):
        plt.plot(reserve_price[:][seller], label="RP Seller " + str(seller))

    plt.title('Reserve Price')
    plt.ylabel('Price')
    plt.xlabel('Rounds')
    plt.legend()

    plt.figure()
    for seller in range(sellers):
        plt.plot(market_price[:][seller], label="MP Seller " + str(seller))

    plt.title('Market Price')
    plt.ylabel('Price')
    plt.xlabel('Rounds')
    plt.legend()
    plt.show()
'''

