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
import plotly.express as px

import networkx as nx
from auction import Auction
from auction_state import AuctionState
from params import * 

from io import StringIO
import multiprocessing as mp

class Auctioneer(Auction):

    bid_history=[]
    increase_bidding_factor = np.random.uniform(1.2, 1.5, size=MAX_NETWORK_SIZE)
    decrease_bidding_factor = np.random.uniform(0.3, 0.7, size=MAX_NETWORK_SIZE)

    def save_frame(self, seller, winner, auction_round):
        nodes = sorted(self.node_list(), key=lambda x: x.price)
        
        frame = pd.DataFrame({'t-1' : \
        [node.price for node in nodes], 't' : \
        [node.price for node in nodes], 't+1' : \
        [node.price for node in nodes], \
        'id' : [node.id for node in nodes], \
        'winner': winner, 'seller': seller, \
        'round' : auction_round, \
        'time_ms': time.thread_time() - self.start_time})
        self.pf = self.pf.append(frame)

    def run_local_auction(self, seller, auction_round):
        self.calculate_market_price(seller, auction_round)

        for buyer in self.buyer_list(seller):
            self.calculate_consistent_bid(buyer, auction_round)
            self.bid_history.append(buyer)
     
        winner = self.second_price_winner(seller)
        #profit = winner.price - seller.price 

        for buyer in self.buyer_list(seller):
            if buyer != winner:
                self.G.add_edge(winner, buyer, weight=winner.price)
        seller.demand -= 1
        winner.demand += 1
        '''
        g = nx.ego_graph(self.G, winner, 1, True)
        print("g=", g.nodes)
        for node in self.seller_list():
            if node != seller:
                g=nx.ego_graph(self.G, node, 1, True)
                if winner in g.nodes:
                    print(node, "--->", winner, nx.shortest_path(self.G, node, winner))
        '''
        return winner

    def do_round(self, auction_round):
        self.bid_history = []
        self.winners = []

        for seller in self.seller_list():
            if len(self.buyer_list(seller)) < 1:
                print("SKIPPING AUCTION", seller)
                continue
            self.save_frame(seller, 0, auction_round)
 
            winner = self.run_local_auction(seller, auction_round)

            self.save_frame(seller, winner, auction_round)
            auction = self.store_auction_state(
                    winner=winner,
                    seller=seller,
                    auction_round=auction_round) # Watch this
            #auction.print_auction_state()
            self.market_price[auction_round].append(
                    seller.price)
                
            self.update_auction(seller, winner)

        end_time = time.thread_time()

        return self.pf


    def calculate_consistent_bid(self, buyer, auction_round):
        if len(self.seller_list(buyer)) < 2:
            seller = random.choice(self.seller_list())
            self.G.add_edge(buyer, seller, weight=buyer.price)
        node_list = self.seller_list(buyer) 
        sorted_nodes = sorted(node_list, key=lambda x: x.price)
            
        buyer.price = sorted_nodes[0].price
        if OPTION:
            prices = []
            opt_out_demand = buyer.demand
            for seller in sorted_nodes:
                prices.append(seller.price)

                opt_out_demand += seller.demand
                if opt_out_demand >= 0:
                    break
            buyer.price = max(prices)
        
        if NOISE:
            neighbors = self.buyer_list(buyer)
            if len(neighbors) > 1:
                if buyer.price <  min([node.price for node in neighbors]):
                    buyer.price = RD(buyer.price*\
                    self.increase_bidding_factor[buyer.id])
                elif buyer.price >  max([node.price for node in neighbors]):
                    buyer.price = RD(buyer.price*\
                    self.decrease_bidding_factor[buyer.id])
        for seller in node_list:
            self.G.add_edge(buyer, seller, weight=buyer.price)
        
        self.save_frame(seller, 0, auction_round)
 
    def second_price_winner(self, seller):
        buyer_list = self.buyer_list(seller)
        sorted_buyers = sorted(buyer_list, key=lambda x: x.price, reverse=True)
        winner = sorted_buyers[0]
        if len(sorted_buyers) > 1:
            winner.price = sorted_buyers[1].price
        else:
            winner.price = sorted_buyers[0].price
        self.G.nodes(data=True)[winner]['color'] = 'red'
        winner.color = 'red'
        self.G.add_edge(seller, winner, weight=winner.price)
        return winner

    def calculate_market_price(self, seller, auction_round):
        node_list = self.buyer_list(seller)
        sorted_nodes = sorted(node_list, key=lambda x: x.price, reverse=True)
        seller.price = sorted_nodes[0].price

        if OPTION:
            prices = []
            opt_out_demand = seller.demand
            for buyer in sorted_nodes:
                prices.append(buyer.price)

                opt_out_demand += buyer.demand
                if opt_out_demand <= 0:
                    break
            seller.price = min(prices)

        self.save_frame(seller, 0, auction_round)
        #for buyer in node_list:
         #   self.G.add_edge(seller, buyer, weight=seller.price)

    def start_auctioneer(self):
        self.start_time = time.thread_time()
        self.price_intervals(0)
        nodes = sorted(self.node_list(), key=lambda x: x.price)
        self.pf = pd.DataFrame({'t-1' : [node.price for node in nodes],\
                                  't' : [node.price for node in nodes],\
                                't+1' : [node.price for node in nodes],\
                                'id' : [node.id for node in nodes], \
                                'round' : 0, \
                             'winner': 0, 'seller': 0, 'time_ms': 0})
        print(self.pf)
        #print(nx.current_flow_closeness_centrality(self.G, weight='weight'))

    def price_intervals(self, auction_round):
        nodes = sorted(self.node_list(), key=lambda x: x.price)
        print([node.price for node in nodes])
        sellers = sorted(self.seller_list(), key=lambda x: x.price)
        buyers = sorted(self.buyer_list(), key=lambda x: x.price)
        
        price_intervals = \
                ([min(sellers[0].price, buyers[0].price), 
                  max(sellers[-1].price, buyers[-1].price)],
                  [max(sellers[0].price, buyers[0].price), \
                 min(sellers[-1].price, buyers[-1].price)])
        pd
        print(price_intervals)


    def store_auction_state(self, winner, seller, auction_round):

        auction_state = AuctionState(self.G, self.bid_history, seller, winner)
        self.auctions_history[auction_round].append(auction_state)
        #f = open("mat.txt", "a")
        #f.write(nx.to_pandas_adjacency(self.G).to_string())
        #f.close()
        return auction_state

    def filename(self, seller, auction_round):
        return 's' + str(seller) + 'r' + str(auction_round)+".txt"




