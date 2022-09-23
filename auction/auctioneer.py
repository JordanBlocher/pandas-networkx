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
from nxn import nxNode

import multiprocessing as mp

'''
The auctioneer tells the auction where it is in time w.r.t to 
the round it is playing, and stores history of how player's 
connectivity influences the price over time. The auctioneer 
also controls the clock, which determines where in time the price
was influenced by previous rounds.
'''

class Auctioneer(Auction):
    name: str = 'auctioneer'
    index = ['name']
    auctions_history=[]
    df = pd.Series()
    fnum=0


    def save_frame(self,ts=0):
        df = pd.DataFrame(self._node.values, index=[ts for n in self._node.index], columns=self._node.columns)
        self.fnum+=1
        if self.df.empty:
            self.df = df
        else:
            self.df = self.df.append(df)
        return self.df

    def run_local_auction(self, seller):
        buyers = self.node_filter('buyer', seller)
        seller.price = self.calculate_market_price(seller, buyers)
        bid_history=[] 
        for buyer in self.node_list('buyer', seller):
            if self.nnodes('seller', buyer) < 2:
                node_list.remove(buyer)
                print("SKIPPING BUYER", buyer)
                continue
            buyer.price = self.calculate_consistent_bid(
                                            buyer,
                                            self.node_filter('seller', buyer), 
                                            self.node_list('buyer', buyer)
                                            )
            #bid_history.append(bid)

        winner = self.second_price_winner(seller)
        winner.winner=True
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
        return winner
               

    def run_auctions(self, rnum):
        global params, auction_round
        auction_round = rnum
        params = self.update()

        self.df = pd.Series()
        self.auctions_history.append([])
        for seller in self.sellers():
            if seller not in self:
                continue
            # TODO: make a param
            if self.nnodes('buyer', seller) < 1: #Allow first price 
                print("SKIPPING SELLER", seller)
                continue
            winner = self.run_local_auction(seller)
            self.print_auction(seller, data=True)
            time.sleep(2)
            winner.winner=False
            
        end_time = time.thread_time()

        return self.df, Clock

    def calculate_consistent_bid(self, buyer, nodes, neighbors):
        global params
        sorted_nodes = list(nodes.sort_values('price').index)
        bprice = sorted_nodes[0].price
        if params['option']:
            prices = []
            opt_out_demand = buyer.demand
            for seller in sorted_nodes:
                prices.append(seller.price)

                opt_out_demand += seller.demand
                if opt_out_demand >= 0:
                    break
            bprice = max(prices)
        if params['noise']:
            if len(neighbors) > 1:
                if buyer.price <  min([node.price for node in neighbors]):
                    bprice = round(
                                buyer.price * params.buyer.inc[buyer.name],
                                2)
                elif buyer.price >  max([node.price for node in neighbors]):
                    bprice = round(
                                buyer.price * params.buyer.dec[buyer.name],
                                2)

        for v in sorted_nodes:
            self.add_edge(buyer, v) 
        #[self.add_edge(buyer, nodes.loc[name(v)]) for v in nodes.index]
        ts = round(time.time()-params.start_time,4)
        self.save_frame(pd.to_timedelta(ts, unit='ms'))
        return 999
 
    def second_price_winner(self, seller):
        global auction_round, params
        nodes = self.node_filter('buyer', seller)
        sorted_nodes = list(nodes.sort_values('price', ascending=False).index)
 
        winner = sorted_nodes[0]
        winner.private_value = winner.price
        try:
            winner.price = sorted_nodes[1].price
        except KeyError:
            print('Taking first price')
        seller.private_value = sorted_nodes[0].price

        ts = round(time.time()-params.start_time,4)
        self.add_edge(winner, seller)
        nodes = self.node_filter('buyer', winner)
        for v in sorted_nodes:
            self.add_edge(winner, v)
        #[self.add_edge(winner, nodes.loc[name(v)]) for v in idx]

        #Clock(seller, winner, self.node_filter('buyer', winner), ts)
        return winner

    def calculate_market_price(self, seller, nodes):
        global params, start_time
        if len(nodes.index) < 1:
            return seller.price
        sorted_nodes = list(nodes.sort_values('price', ascending=False).index)
        mprice = sorted_nodes[0].price
        if params['option']:
            prices = []
            opt_out_demand = seller.demand
            for buyer in sorted_nodes:
                prices.append(buyer.price)

                opt_out_demand += buyer.demand
                if opt_out_demand <= 0:
                    break
            mprice = min(prices)
        ts = round(time.time()-params.start_time,4)
        self.save_frame(pd.to_timedelta(ts, unit='ms'))
        return mprice

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



