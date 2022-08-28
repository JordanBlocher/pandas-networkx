import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import seaborn as sns
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import plotly.express as px 

from params import * 
from auctioneer import Auctioneer
from auction import Auction
from auction_state import AuctionState

from termcolor import colored
import networkx as nx
import numpy as np

sns.set()

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

