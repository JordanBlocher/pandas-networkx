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
from subprocess import Popen, PIPE
import curses
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go

from scipy.cluster.hierarchy import dendrogram, linkage

class MarketSim(Auctioneer): 

    auctions_history=[] # time series
    market_price=[]
    pf = pd.DataFrame()
    ps = pd.Series()
    start_time = 0

    def run_progressive_auction(self):
        
        animation = Animate()
        #animation2 = Animate()
        self.pf = self.start_auctioneer()
        print("START", self.pf)
        animation.price_plot(self.pf)
        auction_round = 0
        self.print_auction()
        animation.show()
        while auction_round < ROUNDS:
            self.auctions_history.append([])
            self.market_price.append([])
            pf = self.do_round(auction_round)
            animation.price_plot_update(pf)
            self.pf = self.pf.append(pf)
            #self.plotnx(auction_round)
            #self.print_round(auction_round)
            #print("FULLPRICE",self.market_price)
            auction_round += 1
            print("TIME ",  self.start_time, '\n\n\n')
        print("OLD PLOT\n\n\n")
        #animation2.price_plot_old(self.pf)
        #animation.show()

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

        


