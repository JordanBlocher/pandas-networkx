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

import multiprocessing as mp

MAX_NETWORK_SIZE = 200

class Auctioneer(Auction):

    f_num = 0
    auctions_history=[]
    df = pd.Series()
    T = nx.Graph()

    def save_frame(self):
        nodes = sorted(self.node_list(), key=lambda x: x.id)
        self.pos = nx.spring_layout(self.G, dim=3, seed=779)
        df = pd.Series({
                        'ts': self.f_num,
                        str(self.f_num) : {
                            'price': np.array([v.price for v in nodes]), 
                            'id': np.array([v.id for v in nodes]),
                            'color': [sns.palettes.xkcd_palette(
                                                            [v.color]
                                                            ) for v in nodes
                                    ],
                            'adj': nx.to_pandas_adjacency(self.G),
                            'edges': nx.to_pandas_edgelist(self.G),
                            'npos' : np.array([self.pos[v] for v in nodes]),
                            'epos' : np.array([(
                                                self.pos[u], self.pos[v]
                                                ) for u, v in self.G.edges()
                                            ])
                            }, 
                        })
        self.f_num += 1 
        if self.df.empty:
            self.df = df
        else:
            self.df = self.df.append(df)
        return self.df

    def run_local_auction(self, seller):
        node_list = self.buyer_list(seller) 
        seller.price = self.calculate_market_price(seller, node_list)
        
        pool = mp.Pool(mp.cpu_count())
        for buyer in node_list:
            if len(self.seller_list(buyer)) < 2:
                print("FORGOT", buyer)
        pool_params = [( 
                    buyer, 
                    self.seller_list(buyer), 
                    self.buyer_list(buyer)
                  ) for buyer in node_list]
        try:
            bid_history = pool.starmap(
                                    self.calculate_consistent_bid, 
                                    pool_params
                                    )
        except KeyboardInterrupt:
            pool.terminate()
            exit()
        pool.close()
        
        winner = self.second_price_winner(seller)
        ts = time.time()
        #profit = winner.price - seller.price 

        node_list.remove(winner)
        [self.G.add_edge(
                        winner, 
                        buyer, 
                        weight=winner.price
                        ) for buyer in node_list]

        auction = self.save_state(
                                  ts = time.time(),
                                  winner=winner,
                                  seller=seller,
                                  bid_history=bid_history
                                  ) 
        
        self.update_auction(winner, seller, params)
        return auction
               

    def run_auctions(self, round_num, new_params):
        global params, auction_round
          
        auction_round = round_num
        params = new_params

        self.inc_factor = np.random.uniform(1.2, 1.5, size=MAX_NETWORK_SIZE)
        self.dec_factor = np.random.uniform(0.3, 0.7, size=MAX_NETWORK_SIZE)

        self.df = pd.Series()
        self.auctions_history.append([])

        for seller in self.seller_list():
            if len(self.buyer_list(seller)) < 1:
                print("SKIPPING AUCTION", seller)
                continue
            auction = self.run_local_auction(seller)
            
            self.price_intervals(auction)

            pool = mp.Pool(mp.cpu_count())
            pool_params = [(
                        seller, 
                        self.buyer_list(seller)
                      ) for seller in self.seller_list()]
            try:
                market_prices = pool.starmap(
                                            self.calculate_market_price, 
                                            pool_params
                                            )
            except KeyboardInterrupt:
                pool.terminate()
                exit()
            pool.close()

        end_time = time.thread_time()

        return self.df

    def calculate_consistent_bid(self, buyer, node_list, neighbors):
        global params
        sorted_nodes = sorted(node_list, key=lambda x: x.price)
        buyer.price = sorted_nodes[0].price
        if params['option']:
            prices = []
            opt_out_demand = buyer.demand
            for seller in sorted_nodes:
                prices.append(seller.price)

                opt_out_demand += seller.demand
                if opt_out_demand >= 0:
                    break
            buyer.price = max(prices)
        if params['noise']:
            if len(neighbors) > 1:
                if buyer.price <  min([node.price for node in neighbors]):
                    buyer.price = round(
                                    buyer.price * self.inc_factor[buyer.id],
                                    2)
                elif buyer.price >  max([node.price for node in neighbors]):
                    buyer.price = round(
                                    buyer.price * self.dec_factor[buyer.id],
                                    2)
        [self.G.add_edge(
                        buyer, 
                        node, 
                        weight=buyer.price
                        ) for node in node_list]

        self.save_frame()
        return buyer
 
    def second_price_winner(self, seller):
        buyer_list = self.buyer_list(seller)
        sorted_buyers = sorted(buyer_list, key=lambda x: x.price, reverse=True)
        winner = sorted_buyers[0]
        winner.private_value = winner.price
        if len(sorted_buyers) > 1:
            winner.price = sorted_buyers[1].price
        else:
            winner.price = sorted_buyers[0].price
        self.G.add_edge(winner, seller, weight=winner.price)
        seller.demand -= 1
        winner.demand += 1
        return winner

    def calculate_market_price(self, seller, node_list):
        global params
        if len(node_list) < 1:
            return seller.price
        sorted_nodes = sorted(node_list, key=lambda x: x.price, reverse=True)
        seller.price = sorted_nodes[0].price
        if params['option']:
            prices = []
            opt_out_demand = seller.demand
            for buyer in sorted_nodes:
                prices.append(buyer.price)

                opt_out_demand += buyer.demand
                if opt_out_demand <= 0:
                    break
            seller.price = min(prices)
        self.save_frame()
        return seller.price

    def save_state(self, winner, seller, bid_history):
        global auction_round

        nodes = sorted(self.node_list(), key=lambda x: x.id)
        neighbors = np.array([
                              v.id for v in self.buyer_list(winner)
                            ])
                             
        auction = pd.Series(
                            dict(
                             bids = np.array([v.price for v in bid_history]),
                             buyers = np.array([v.id for v in bid_history]),
                             seller = seller.id, 
                             mp     = seller.price,
                             winner = winner.id
                            ))
                        
        self.auctions_history[auction_round].append(auction)

        self.T.add_node(winner)
        self.T.add_node(seller)
        self.T.add_edge(winner, seller, weight=seller.price)
        for node in neighbors:
            if node in list(self.T.nodes):
                self.T.add_edge(winner, node, weight=winner.price)

        return auction
    

    def price_intervals(self, auction):
        nodes = sorted(self.node_list(), key=lambda x: x.price)
        print([node.price for node in nodes])
        sellers = sorted(self.seller_list(), key=lambda x: x.price)
        buyers = sorted(self.buyer_list(), key=lambda x: x.price)
        
        price_intervals=([
                        min(sellers[0].price,
                        buyers[0].price), 
                        max(sellers[-1].price, 
                        buyers[-1].price)
                        ],[
                        max(sellers[0].price, 
                        buyers[0].price), 
                        min(sellers[-1].price, 
                        buyers[-1].price)
                        ])
        print(price_intervals)
