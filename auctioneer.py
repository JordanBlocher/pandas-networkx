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
    frame = None
    increase_bidding_factor = np.random.uniform(1.2, 1.5, size=MAX_NETWORK_SIZE)
    decrease_bidding_factor = np.random.uniform(0.3, 0.7, size=MAX_NETWORK_SIZE)

    def save_frame(self):
        nodes = sorted(self.node_list(), key=lambda x: x.id)
        frame = pd.DataFrame({'price' : [node.price for node in nodes], \
                              'id' : [node.id for node in nodes],
                              'time_ms': self.start_time,
                              'color' : [node.color for node in nodes]})
        self.start_time += 1 
        if self.frame.empty:
            self.frame = frame
        else:
            self.frame = self.frame.append(frame)

    def run_local_auction(self, seller):
        node_list = self.buyer_list(seller) 
        seller.price = self.calculate_market_price(seller, node_list)
        
        pool = mp.Pool(mp.cpu_count())
        params = [(buyer, self.seller_list(buyer), \
                          self.buyer_list(buyer))\
                          for buyer in node_list]
        self.bid_history = pool.starmap(self.calculate_consistent_bid, params)
        pool.close()
        
        winner = self.second_price_winner(seller)
        #profit = winner.price - seller.price 

        node_list.remove(winner)
        [self.G.add_edge(winner, buyer, weight=winner.price) for buyer in node_list]
        seller.demand -= 1
        winner.demand += 1

        return winner
               

    def do_round(self, auction_round):
        self.frame = pd.DataFrame()
        self.bid_history = []
        self.winners = []
        pool = mp.Pool(mp.cpu_count())

        for seller in self.seller_list():
            print("t=", time.thread_time())
            if len(self.buyer_list(seller)) < 1:
                print("SKIPPING AUCTION", seller)
                continue
            winner = self.run_local_auction(seller)
            
            seller_pool = mp.Pool(mp.cpu_count())
            params = [(seller, self.buyer_list(seller)) for seller in self.seller_list()]
            market_prices = seller_pool.starmap(self.calculate_market_price, params)
            seller_pool.close()
            auction = self.store_auction_state(
                    winner=winner,
                    seller=seller,
                    auction_round=auction_round) # Watch this
            self.market_price[auction_round].append(seller.price)
            self.update_auction(seller, winner)
        end_time = time.thread_time()

        return self.frame

    def start_auctioneer(self):
        #self.price_intervals(0)
        #print(nx.current_flow_closeness_centrality(self.G, weight='weight'))
        self.frame = pd.DataFrame()
        self.save_frame() 
        return self.frame

    def dt(self, price):
        td = pd.to_timedelta(time.time())
        self.ps = self.ps.append(pd.Series(data=[price], index=[td.delta]))

    def calculate_consistent_bid(self, buyer, node_list, neighbors):
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
            if len(neighbors) > 1:
                if buyer.price <  min([node.price for node in neighbors]):
                    buyer.price = RD(buyer.price*\
                    self.increase_bidding_factor[buyer.id])
                elif buyer.price >  max([node.price for node in neighbors]):
                    buyer.price = RD(buyer.price*\
                    self.decrease_bidding_factor[buyer.id])
        [self.G.add_edge(buyer, seller, weight=buyer.price) for seller in node_list]
        self.save_frame()
        self.dt(buyer.price)
        return buyer
 
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
        self.G.add_edge(winner, seller, weight=winner.price)
        self.dt(winner.price)
        return winner

    def calculate_market_price(self, seller, node_list):
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
        self.save_frame()
        self.dt(seller.price)
        #for buyer in node_list:
         #   self.G.add_edge(seller, buyer, weight=seller.price)
        return seller.price


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




