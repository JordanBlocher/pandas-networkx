import random
import time
import sys

import numpy as np
np.set_printoptions(precision=2)
np.set_printoptions(linewidth=120)
import matplotlib
import matplotlib.pyplot as plt
from termcolor import colored
import seaborn as sns
import pandas as pd

import networkx as nx
from auction import Auction
from auction_state import AuctionState
from params import * 

from io import StringIO
import multiprocessing as mp

class Auctioneer(Auction):

    bid_history=[]
    winners=[]
    increase_bidding_factor = np.random.uniform(1, 1.5, size=NBUYERS)
    decrease_bidding_factor = np.random.uniform(0.3, 0.8, size=NBUYERS)

    def run_local_auction(self, seller):
        for buyer in self.buyer_list(seller):
            buyer.calculate_consistent_bid(self.seller_list(buyer))
            self.G[buyer][seller]['weight'] = buyer.price
            self.bid_history.append(buyer)

        winner = seller.calculate_market_price(self.buyer_list(seller))
        profit = winner.price - seller.price #keep?

        self.winners.append(winner.id)

        self.T.add_node(winner)
        self.G[seller][winner]['weight'] = seller.price
        self.G.nodes(data=True)[winner]['color'] = 'red'
        for buyer in self.buyer_list(seller):
            if buyer != winner:
                self.G.add_edge(winner, buyer, weight=seller.price)
                self.T.add_edge(winner, buyer, weight=seller.price)
        seller.demand -= 1
        winner.demand += 1

        return winner

    def do_round(self, auction_round):
        self.bid_history = []
        self.winners = []

        for seller in self.seller_list():
            winner = self.run_local_auction(seller)
            winner.color = 'red'
            auction = self.store_auction_state(
                    winner=winner,
                    seller=seller,
                    auction_round=auction_round) # Watch this
            auction.print_auction_state()

            self.market_price[auction_round].append(
                    seller.price)
                
            self.correlate(auction_round)
            self.plot.nxgraph3d(self.G)
            self.update_auction(seller, winner)

        self.print_round(auction_round)
        auction_round += 1
        time.sleep(1)
    
        return auction_round

    def start_auctioneer(self):
        self.write_matrix(0)
        sorted_nodes = sorted(self.seller_list(), key=lambda x: x.price, reverse=True)
        mean = sorted_nodes[int(len(sorted_nodes)/2.)]

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

    def store_auction_state(self, winner, seller, auction_round):

        auction_state = AuctionState(self.G, self.bid_history, seller, winner)
        self.auctions_history[auction_round].append(auction_state)
        #f = open("mat.txt", "a")
        #f.write(nx.to_pandas_adjacency(self.G).to_string())
        #f.close()
        return auction_state

    def print_round(self, round_number):
        print("ROUND ", round_number)
        #print(nx.to_dict_of_lists(self.G))
        #print(self.G.nodes(data=True))
        #print(self.G.edges(data=True))
        print(nx.to_pandas_adjacency(self.G))

        '''
        n = 0
        for auction_state in self.auctions_history[round_number]:
            auction_state.print_auction_state()
            n += 1
        '''

        if NCURSES:
            with open(PIPE_PATH, 'w') as p:
                #p.write(nx.to_pandas_adjacency(self.G).to_string())
                out = StringIO()
                print(nx.to_dict_of_dicts(self.G), file=out)
                val = out.getvalue()
                p.write(val)
                p.write('\n')
            p.close()

    def filename(self, seller, auction_round):
        return 's' + str(seller) + 'r' + str(auction_round)+".txt"




