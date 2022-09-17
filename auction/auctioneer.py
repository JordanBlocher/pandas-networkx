import random
import time
import sys

import numpy as np
np.set_printoptions(precision=2)
np.set_printoptions(linewidth=120)
from termcolor import colored
import seaborn as sns
import pandas as pd
import plotly.express as px

import networkx as nx
from auction import Auction
from models import Clock, Intersection

import multiprocessing as mp

class Auctioneer(Auction):

    auctions_history=[]
    df = pd.Series()
    fnum=0

    def save_frame(self, start_time=0):
        ts = round(time.time()-start_time,4),
        nodes = sorted(self.node_list(), key=lambda x: x.id)
   
        adj_mat = nx.to_pandas_adjacency(self)
        edges = nx.to_pandas_edgelist(self)
        df = pd.Series({
                        'f' : self.fnum,
                        'ts' : ts,
                        str(self.fnum) : {
                            'adj': nx.to_pandas_adjacency(self),
                            'edges': nx.to_pandas_edgelist(self),
                            },
                    })
        self.fnum+=1
        if self.df.empty:
            self.df = df
        else:
            self.df = self.df.append(df)
        return self.df

    def run_local_auction(self, seller):
        node_list = self.buyer_list(seller) 
        seller.price = self.calculate_market_price(seller, node_list)
        bid_history=[] 
        for buyer in node_list:
            if len(self.node_list(buyer.inv_filter, buyer)) < 2:
                #node_list.remove(buyer)
                print("SKIPPING BUYER", buyer)
                continue
            bid = self.calculate_consistent_bid(
                                            buyer, 
                                            self.seller_list(buyer), 
                                            self.buyer_list(buyer)
                                            )
            bid_history.append(bid)

        winner = self.second_price_winner(seller)
        #profit = winner.price - seller.price 

        auction = self.save_state(
                                  ts = round(time.time()-self.start_time,4),
                                  winner=winner,
                                  seller=seller,
                                  bid_history=bid_history
                                  ) 
        
        self.update_auction(winner, seller)
        return auction
               

    def run_auctions(self, rnum):
        global params, auction_round
        auction_round = rnum
        params = self.update()

        self.df = pd.Series()
        self.auctions_history.append([])

        for seller in self.seller_list():
            self.print_auction()

            if seller not in self:
                continue
            if len(self.buyer_list(seller)) < 1:
                continue
            auction = self.run_local_auction(seller)
            
        end_time = time.thread_time()

        return self.df, Clock

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
                                    buyer.price * params.buyerinc[buyer.id],
                                    2)
                elif buyer.price >  max([node.price for node in neighbors]):
                    buyer.price = round(
                                    buyer.price * params.buyerdec[buyer.id],
                                    2)
        [self.add_edge(buyer, node) for node in node_list]
        self.save_frame()
        return buyer
 
    def second_price_winner(self, seller):
        global auction_round, params
        buyer_list = self.buyer_list(seller)
        sorted_buyers = sorted(buyer_list, key=lambda x: x.price, reverse=True)
        winner = sorted_buyers[0]
        winner.private_value = round(winner.price,2)
        if len(sorted_buyers) > 1:
            winner.price = sorted_buyers[1].price
        else:
            print('Taking first price')
            winner.price = sorted_buyers[0].price
        seller.private_value = sorted_buyers[0].price

        ts = round(time.time()-params['start_time'],4)
        self.add_edge(winner, seller)
        [self.add_edge(winner, buyer) for buyer in self.buyer_list(seller)]

        Clock(seller, winner, self.buyer_list(winner), ts)

        return winner

    def calculate_market_price(self, seller, node_list):
        global params, start_time
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

    def save_state(self, winner, seller, bid_history, ts):
        global auction_round

        nodes = sorted(self.node_list(), key=lambda x: x.id)
        neighbors = np.array([
                              v.id for v in self.buyer_list(winner)
                            ])
        bids = np.array([v.price for v in bid_history]),
        demand = np.array([v.demand for v in bid_history]),
        buyers = np.array([v.id for v in bid_history]),
        
        auction = pd.Series(
                    dict(
                        ts = ts,
                        neighbors = neighbors,
                        bids = bids, 
                        demand = demand,
                        buyers = buyers,
                        seller = seller.id, 
                        mp     = seller.price,
                        winner = winner.id
                        )
                    )
                        
        self.auctions_history[auction_round].append(auction)
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
