import random
import time
import sys

import numpy as np
from termcolor import colored
import seaborn as sns
import pandas as pd

import networkx as nx
from auction import Auction
from models import Clock, Intersection
from nxn import nxNode

from pandas.api.extensions import register_dataframe_accessor

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
    df = pd.DataFrame()
    df_e = pd.DataFrame()
    df_r = pd.DataFrame()

    def save_frame(self,ts=0,rnum=0):
        df = pd.DataFrame(
                        self._node.values, 
                        columns=self._node.columns,
                        index=[rnum for n in range(len(self._node.index))]
                        )
        #df.set_index('ts', inplace=True)
        df_e = pd.DataFrame(
                        self._adj.values, 
                        columns=self._adj.columns,
                        index=[rnum for n in range(len(self._adj.index))]
                        )
        #df_e.set_index('ts', inplace=True)
        self.df = self.df.append(df)
        self.df_e = self.df_e.append(df_e)
        idx = pd.IndexSlice
        return pd.Series(dict(
                            nodes=self.df,
                            edges=self.df_e,
                            data=dict(
                                auctions=[
                                            (v, list(self.node_list('buyer', v)))
                                            for v in self.sellers()
                                ],
                                neighbors=[
                                            (n,[v for v in self._adj.loc[idx[:,n],:].index])
                                            for n in self.buyers()
                                ],
                                result=self.df_r
                            )
                        )
                    )

    def run_local_auction(self, seller):
        buyers = self.node_filter('buyer', seller)
        seller.price = self.calculate_market_price(seller, buyers)
        bid_history=[] 
        for buyer in self.node_list('buyer', seller):
            if self.nnodes('seller', buyer) < 2:
                print("Skipping buyer", buyer)
                buyers = buyers.loc[buyers.name != buyer.name]
                continue
            buyer.price = self.calculate_consistent_bid(
                                            buyer,
                                            self.node_filter('seller', buyer), 
                                            self.node_list('buyer', buyer)
                                            )
            #bid_history.append(bid)

        winner = self.second_price_winner(seller, buyers)
        #print("BUYER",winner,"WON")
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

        self.df = pd.DataFrame()
        self.df_e = pd.DataFrame()
        self.df_r = pd.DataFrame()
        self.auction_state = pd.Series()
        winners = []
        for seller in self.sellers():
            if seller not in self:
                continue
            # TODO: make a param
            if self.nnodes('buyer', seller) < 2: #Allows first price if set to 1
                print("Skipping seller", seller)
                continue
            won = self.run_local_auction(seller)
            winners.append(won)

            self.print_auction(seller)

        for n in winners:
            n.type = 'buyer' 
        end_time = time.thread_time()

        idx = pd.IndexSlice
        auction_state = pd.Series(dict(
                            nodes=self.df,
                            edges=self.df_e,
                            data=dict(
                                auctions=[
                                    (v, list(self.node_list('buyer', v)))
                                    for v in self.sellers()
                                ],
                                neighbors=[
                                    (n,[v for v in self._adj.loc[idx[:,n],:].index])
                                    for n in self.buyers()
                                ],
                                result = self.df_r
                            ))
                        )
        return auction_state

    def calculate_consistent_bid(self, buyer, sellers, neighbors):
        global params, auction_round
        sorted_sellers = list(sellers.sort_values('price').index)
        bprice = sorted_sellers[0].price
        if params['option']:
            prices = []
            opt_out_demand = buyer.demand
            for seller in sorted_sellers:
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

        for v in sorted_sellers:
            self.add_edge(buyer, v) 
        ts = round(time.time()-params.start_time,4)
        ts = pd.to_timedelta(ts, unit='ms')
        buyer.ts = ts
        self.save_frame(ts, auction_round)
        return bprice
 
    def second_price_winner(self, seller, buyers):
        global auction_round, params
        sorted_buyers = list(buyers.sort_values('price', ascending=False).index)
        winner = sorted_buyers[0]
        winner.winner = True
        winner.value = winner.price
        if len(sorted_buyers) > 1:
            winner.price = sorted_buyers[1].price
        else:
            print('Taking first price')
        seller.value = sorted_buyers[0].price

        self.add_edge(winner, seller)
        nbrs = list(self.node_filter('buyer', winner).index)
        for w in nbrs:
            self.add_edge(winner, w)

        ts = round(time.time()-params.start_time,4)
        ts = pd.to_timedelta(ts, unit='ms')
        winner.ts = ts
        winner.type = 'winner'
        self.save_frame(ts, auction_round)
        #Clock(seller, winner, self.node_filter('buyer', winner), ts)
        return winner

    def calculate_market_price(self, seller, buyers):
        global params, auction_round
        if len(buyers.index) < 1:
            return seller.price
        sorted_buyers = list(buyers.sort_values('price', ascending=False).index)
        mprice = sorted_buyers[0].price
        if params['option']:
            prices = []
            opt_out_demand = seller.demand
            for buyer in sorted_buyers:
                prices.append(buyer.price)

                opt_out_demand += buyer.demand
                if opt_out_demand <= 0:
                    break
            mprice = min(prices)
        ts = round(time.time()-params.start_time,4)
        ts = pd.to_timedelta(ts, unit='ms')
        seller.ts = ts
        self.save_frame(ts, auction_round)
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



