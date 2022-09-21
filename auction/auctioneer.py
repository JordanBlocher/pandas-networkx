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
from nxn import nxNode, name

import multiprocessing as mp

'''
The auctioneer tells the auction where it is in time w.r.t to 
the round it is playing, and stores history of how player's 
connectivity influences the price over time. The auctioneer 
also controls the clock, which determines where in time the price
was influenced by previous rounds.
'''

class Auctioneer(Auction):

    auctions_history=[]
    df = pd.Series()
    fnum=0

    def __init__(self):
        self.type='auctioneer'
        Auction.__init__(self)

    def save_frame(self, start_time=0):
        ts = round(time.time()-start_time,4),
   
        df = pd.Series({
                        'f' : self.fnum,
                        'ts' : ts,
                        'nodes': self._node,
                        'edges': self._adj
                    })
        self.fnum+=1
        if self.df.empty:
            self.df = df
        else:
            self.df = self.df.append(df)
            print(df)
        return self.df

    def run_local_auction(self, seller):
        buyers = self.node_filter('buyer', seller)
        print("PREICE",seller.price)
        seller.price = self.calculate_market_price(seller, buyers)
        print("PREICE",seller.price)
        print("PREICE",self._node.loc[name(seller)].price)
        bid_history=[] 
        for buyer in self.node_list('buyer', seller):
            if len(self.node_list('seller', buyer)) < 2:
                node_list.remove(buyer)
                print("SKIPPING BUYER", buyer)
                continue
            bid = self.calculate_consistent_bid(
                                            buyer,
                                            self.node_filter('seller', buyer), 
                                            self.node_filter('buyer', buyer)
                                            )
            bid_history.append(bid)

        winner = self.second_price_winner(seller)
        #profit = winner.price - seller.price 

        '''
        auction = self.save_state(
                                  ts = round(time.time()-self.start_time,4),
                                  winner=winner,
                                  seller=seller,
                                  bid_history=bid_history
                                  ) 
        '''
        
        self.update_auction(winner, seller)
        #return auction
               

    def run_auctions(self, rnum):
        global params, auction_round
        auction_round = rnum
        params = self.update()

        self.df = pd.Series()
        self.auctions_history.append([])

        for seller in self.sellers:
            self.print_auction()

            if seller not in self:
                continue
            if len(self.node_list('buyer', seller)) < 1:
                continue
            auction = self.run_local_auction(seller)
            
        end_time = time.thread_time()

        print(self.df)
        return self.df, Clock

    def calculate_consistent_bid(self, buyer, nodes, neighbors):
        global params
        sorted_nodes = nodes.sort_values('price')
        idx=list(sorted_nodes.index)
        buyer.price = nodes.loc[idx[0]].price
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
                if buyer.price <  min([node.price for node in neighbors.T]):
                    buyer.price = round(
                                    buyer.price * params.buyer.inc[buyer.name],
                                    2)
                elif buyer.price >  max([node.price for node in neighbors.T]):
                    buyer.price = round(
                                    buyer.price * params.buyer.dec[buyer.name],
                                    2)

        for v in idx:
            self.add_edge(buyer, self._node.loc[name(v)]) 
        #[self.add_edge(buyer, nodes.loc[name(v)]) for v in nodes.index]
        self.save_frame()
        return buyer
 
    def second_price_winner(self, seller):
        global auction_round, params
        nodes = self.node_filter('buyer', seller)
        sorted_nodes = nodes.sort_values('price', ascending=False)
        idx=list(sorted_nodes.index)
 
        winner = nodes.loc[idx[0]]
        winner.private_value = round(winner.price,2)
        if len(idx) > 1:
            winner.price = nodes.loc[idx[1]].price
        else:
            print('Taking first price')
            winner.price = nodes.loc[idx[0]].price
        seller.private_value = nodes.loc[idx[0]].price

        ts = round(time.time()-params['start_time'],4)
        self.add_edge(winner, seller)
        nodes = self.node_filter('buyer', winner)
        for v in nodes.index:
            self.add_edge(winner, self._node.loc[name(v)]) 
        #[self.add_edge(winner, nodes.loc[name(v)]) for v in idx]

        #Clock(seller, winner, self.node_filter('buyer', winner), ts)
        return winner

    def calculate_market_price(self, seller, nodes):
        global params, start_time
        if len(nodes) < 1:
            return seller.price
        sorted_nodes = nodes.sort_values('price', ascending=False)
        idx=list(sorted_nodes.index)
        seller.price = nodes.loc[idx[0]].price
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

    '''
    def save_state(self, winner, seller, bid_history, ts):
        pass
        global auction_round

        nodes = sorted(self.node_list(), key=lambda x: x.name)
        nodes = list(node_list.sort_values('id'))
        neighbors = np.array([
                              v for v in self.node_filter('buyer', winner).T
                            ])
        bids = np.array([v.price for v in bid_history]),
        demand = np.array([v.demand for v in bid_history]),
        buyers = np.array([v.name for v in bid_history]),
        
        auction = pd.Series(
                    dict(
                        ts = ts,
                        neighbors = neighbors,
                        bids = bids, 
                        demand = demand,
                        buyers = buyers,
                        seller = seller.name, 
                        mp     = seller.price,
                        winner = winner.name
                        )
                    )
                        
        self.auctions_history[auction_round].append(auction)
        return auction
    '''



