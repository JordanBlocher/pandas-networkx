import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import seaborn as sns
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage

from params import * 
from auctioneer import Auctioneer
from auction import Auction
from auction_state import AuctionState

from termcolor import colored
import networkx as nx
import numpy as np

sns.set()

class NXPlot:

    fig = plt.figure()
    axes = []
    
    def __init__(self, subplots):
        plt.clf()
        for n in subplots:
            self.axes.append(self.fig.add_subplot(n))
        self.axes.append(self.fig.add_subplot(133, projection='3d'))
        #for ax in self.axes:
        #    self.format_axes(ax)

    def corr(self, mat, G, nodes):
        self.nxheatmap(mat)
        self.nxgraph(G, nodes)
        self.draw(1)

    def nxheatmap(self, mat):
        ax = plt.subplot(121).axes
        plt.sca(ax)
        plt.cla()
        sns.heatmap(mat, ax=ax)

    def nxgraph(self, G, nodes):  
        ax = plt.subplot(122).axes
        plt.sca(ax)
        plt.cla()
        color_map = []
        for node in G.nodes:
            color_map.append(nodes[node]['color'])
        pos = nx.spring_layout(G, dim=3, seed=779)
        nx.draw(G, ax=ax, with_labels=True, node_color=color_map)

    def nxgraph3d(self, G):
        ax = plt.subplot(133).axes
        plt.sca(ax)
        plt.cla()
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


    def format_axes(self, ax):
        ax.grid(False)
        for dim in (ax.xaxis, ax.yaxis):
            dim.set_ticks([])

    def draw(self, n):
        plt.figure(n)
        plt.draw()
        plt.pause(.1)




matplotlib.interactive(True)

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

