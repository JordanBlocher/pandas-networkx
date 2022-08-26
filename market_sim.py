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


class MarketSim(Auctioneer): 

    auctions_history=[] # time series
    market_price=[]
    mat = np.zeros((MSELLERS,MSELLERS), float)
    T = nx.DiGraph()
    plot = NXPlot([131, 132])

    def run_progressive_auction(self):
        
        if NCURSES:
            self.proc =  Popen([ 'sh', '-c', 'tail -f %s | gnome-terminal -- python3 sim.py' % PIPE_PATH ], stdout=PIPE, stdin=PIPE)

        self.start_auctioneer()
        auction_round = 0
        while auction_round < ROUNDS:
            self.auctions_history.append([])
            self.market_price.append([])
            self.bid_history = []
            auction_round = self.do_round(auction_round)
            self.print_round(auction_round-1)

        if NCURSES:
            time.sleep(2)
            while True:
                if np.size(self.mat) == 0:
                    break
                try:
                    stdin, stdout = self.proc.communicate(timeout=5)
                except:
                    time.sleep(2)
                print(stdin, stdout)
                #init_state = AuctionState(self.G)
            
    def print_round(self, round_number):
        print("ROUND ", round_number)
        print("MASTER", nx.to_pandas_adjacency(self.G))
        n = 0
        for auction_state in self.auctions_history[round_number]:
            auction_state.print_auction_state()
            n += 1

    def correlate(self, auction_round):
        adj_matrix = nx.to_pandas_adjacency(self.G)
        corr = adj_matrix.corr()
        links = corr.stack().reset_index()
        links.columns = ['buyer', 'seller', 'value']
        links_filtered = links.loc[ (links['value'] > 0) & (links['buyer'] != links['seller']) ]
        G = nx.from_pandas_edgelist(links_filtered, 'buyer', 'seller')
        self.plot.corr(nx.to_pandas_adjacency(self.G), G, self.G.nodes)
        time.sleep(1)

    def plot_nxgraph(self, aution_round=0):
        pass
        #Z = linkage(adj_matrix.corr(), 'ward')
        #dendrogram(Z, labels=adj_matrix.corr().index, leaf_rotation=0)
    

# Execute with parameters
if __name__ == '__main__':
    program = MarketSim()
    program.run_progressive_auction()

        

'''
    def pipe_auction(self):
        #with open(PIPE_PATH, 'w') as p:
       #     p.write(str(nx.to_dict_of_lists(self.G)))
        #p.close()
 
        line = []
        line.append('\t')
        for node in self.seller_view():
            line.append(str(node.id))
            line.append(str(node.price))
            line.append(str(node.quantity))
        line.append('\n')
        buyers = []
        n=0
        m=0
        for seller in self.seller_view():
            buyers.append(self.buyer_list(seller))
        for k in range(self.nbuyers):
            line.append('\t')
            for m in range(self.msellers):
                if len(buyers[m]) > n:
                    node = buyers[m%3][n]
                    line.append(str(node))
                    line.append(str(node.price))
                    line.append(str(node.quantity))
                    line.append('\n') 
                else:
                    line.append('\t\t')
            n+=1
            line.append(' ')
        print(' '.join(line))
        return(' '.join(line))
'''


