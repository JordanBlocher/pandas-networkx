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
from signal import SIGTSTP

class Auctioneer(Auction):

    f_num = 0
    auctions_history=[]
    df = pd.Series()
    

    def save_frame(self):
        nodes = sorted(self.node_list(), key=lambda x: x.id)
        df = pd.Series({
                        'ts': self.f_num,
                        str(self.f_num) : {
                            'price': np.array([v.price for v in nodes]), 
                            'id': np.array([v.id for v in nodes]),
                            'color': [v.color for v in nodes],
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

    def run_local_auction(self, seller, bid_history):
        node_list = self.buyer_list(seller) 
        seller.price = self.calculate_market_price(seller, node_list)
        
        pool = mp.Pool(mp.cpu_count())
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
        
        winner, colors = self.second_price_winner(seller)
        #profit = winner.price - seller.price 

        node_list.remove(winner)
        [self.G.add_edge(
                        winner, 
                        buyer, 
                        weight=winner.price
                        ) for buyer in node_list]
        #[node.color = pallet[node.id] for node in node_list]
        winner.color = self.buyer_colors[seller.id][-1]
        seller.demand -= 1
        winner.demand += 1

        return winner
               

    def run_auctions(self, round_num, new_params):
        global params, auction_round
          
        auction_round = round_num
        params = new_params

        self.inc_factor = np.random.uniform(1.2, 1.5, size=200)
        self.dec_factor = np.random.uniform(0.3, 0.7, size=200)

        self.df = pd.Series()
        bid_history = []
        self.auctions_history.append([])

        self.update_nodes(params)
        pool = mp.Pool(mp.cpu_count())

        for seller in self.seller_list():
            #seller.color = self.seller_colors[seller.id]
            if len(self.buyer_list(seller)) < 1:
                print("SKIPPING AUCTION", seller)
                continue
            winner = self.run_local_auction(seller, bid_history)
            
            auction = self.store_auction_state(
                                              winner=winner,
                                              seller=seller,
                                              bid_history=bid_history,
                                              auction_round=auction_round
                                              ) # Watch this
            self.update_auction(seller, winner)


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

        return self.auctions_history[auction_round], self.df

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
        '''
        palette = sns.diverging_palette(
                                    buyer.color, 
                                    node.color,
                                    l=65, 
                                    center="dark", 
                                    as_cmap=True
                                    ) 
        #[node.color = palette[node.id] for node in node_list]
        '''
        self.save_frame()
        return buyer
 
    def second_price_winner(self, seller):
        buyer_list = self.buyer_list(seller)
        sorted_buyers = sorted(buyer_list, key=lambda x: x.price, reverse=True)
        winner = sorted_buyers[0]
        if len(sorted_buyers) > 1:
            winner.price = sorted_buyers[1].price
        else:
            winner.price = sorted_buyers[0].price
        self.G.add_edge(winner, seller, weight=winner.price)
        '''
        seller.color = sns.diverging_palette(
                                    seller.color,
                                    winner.color, 
                                    l=45, 
                                    center="light", 
                                    as_cmap=True
                                    )[0]

        palette = sns.diverging_palette(
                                    winner.color,
                                    node.color, 
                                    l=65, 
                                    center="light", 
                                    as_cmap=True)
        '''
        return winner#, palette

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
        node_list.append(seller)

        #for buyer in node_list:
         #   self.G.add_edge(seller, buyer, weight=seller.price)
        '''
        pallet = sns.diverging_palette(
                                seller.color,
                                node.color, 
                                l=65, 
                                center="dark", 
                                n_colors=1, 
                                as_cmap=True
                                )
        '''
        #[node.color = palette[node.id] for node in node_list]

        return seller.price


    def price_intervals(self, auction_round):
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


    def store_auction_state(self, winner, seller, bid_history, auction_round):

        nodes = sorted(self.node_list(), key=lambda x: x.id)
        auction_state = dict(bids   = [v.price for v in bid_history],
                             buyers = [v.id for v in bid_history],
                             seller = seller.id, 
                             mp     = seller.price,
                             winner = winner.id
                            )
                        
        self.auctions_history[auction_round].append(auction_state)
        #f = open("mat.txt", "a")
        #f.write(nx.to_pandas_adjacency(self.G).to_string())
        #f.close()
        return auction_state

    def filename(self, seller, auction_round):
        return 's' + str(seller) + 'r' + str(auction_round)+".txt"


    def get_npos(self):
        epos = np.array([(self.pos[u], self.pos[v]) for u, v in self.G.edges()])
        npos = np.array([self.pos[v] for v in nodes])
        return npos, epos

    def get_adj(self):
        return nx.to_pandas_adjacency(self.G)
