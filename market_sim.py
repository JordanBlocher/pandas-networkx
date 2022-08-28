import numpy as np
from termcolor import colored

from params import * 
from auctioneer import Auctioneer
from auction import Auction
from auction_state import AuctionState

import networkx as nx
from nxplot import NXPlot

import os
import sys
import time
from subprocess import Popen, PIPE
import curses
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


from scipy.cluster.hierarchy import dendrogram, linkage

class MarketSim(Auctioneer): 

    auctions_history=[] # time series
    market_price=[]
    mat = np.zeros((MSELLERS,MSELLERS), float)
    T = nx.DiGraph()
    SOI = nx.Graph()
    plot = NXPlot([(121,None), (122,None)])
    #plot_tree = NXPlot([(121, None), (122, None)])
    plot_tree = NXPlot([(111, None)])
    df = pd.DataFrame()

    def run_progressive_auction(self):
        
        self.start_auctioneer()
        self.df = nx.to_pandas_edgelist(self.G)
        auction_round = 0
        self.print_auction()
        while auction_round < ROUNDS:
            self.auctions_history.append([])
            self.market_price.append([])
            self.bid_history = []
            pf = self.do_round(auction_round)
            self.plot_price(pf, auction_round)
            self.df.append(nx.to_pandas_edgelist(self.G))
            #self.plotnx(auction_round)
            #self.print_round(auction_round)
            #print("FULLPRICE",self.market_price)
            auction_round += 1
            time.sleep(1)

    def print_round(self, round_number):
        print("Round", auction_round)
        #print(nx.to_dict_of_lists(self.G))
        #print(self.G.nodes(data=True))
        #print(self.G.edges(data=True))
        #print(nx.to_pandas_adjacency(self.G))

        n = 0
        for auction_state in self.auctions_history[round_number]:
            auction_state.print_auction_state()
            n += 1


    def plotnx(self, auction_round=0):

        self.correlate(auction_round)

        print(self.T.nodes(data=True))
        print(self.T.edges(data=True))
        #T =nx.from_edgelist(edges)
        self.plot_tree.nxgraph(self.T, None, 111)
        self.plot_tree.draw()
        #self.T.clear()

    def correlate(self, auction_round):
        adj_matrix = nx.to_pandas_adjacency(self.G)
        corr = adj_matrix.corr()
        links = corr.stack().reset_index()
        links.columns = ['b', 's', 'v']
        links_filtered = links.loc[ (links['v'] > 0) & (links['b'] != links['s']) ]
        G = nx.from_pandas_edgelist(links_filtered, 'b', 's')
        self.plot.nxheatmap(adj_matrix, 121)
        self.plot.nxgraph(G, self.G.nodes, 122)
        self.plot.draw()

    def write_matrix(self, auction_round):
        if NCURSES:
            with open(PIPE_PATH, 'w') as p:
                p.write(np.array_str(self.mat, precision=2, suppress_small=True))
                p.write('\n')
            p.close()
        f = open("mat" + str(auction_round) + ".txt", "w")
        f.write('NAME\t')
        m = nx.to_pandas_adjacency(self.G)
        for i in range(m.shape[0]):    
            f.write('%s\t' % m.columns[i])
        f.write('\n')
        for r in range(m.shape[0]):    
            f.write('%s\t' % m.columns[r])
            for c in range(m.shape[1]):    
                f.write('%s\t' % m.values[r][c])
            f.write('\n')
        f.write('\n')
        f.close()


# Execute with parameters
if __name__ == '__main__':
    program = MarketSim()
    program.run_progressive_auction()

        


