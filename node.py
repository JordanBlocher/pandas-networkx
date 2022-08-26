import random
import numpy as np
np.set_printoptions(precision=2)
from params import * 
import json

def Buyer():
    return Node('green', 'buyer', BUYER_FACTOR, -1)

def Seller():
    return Node('magenta', 'seller', SELLER_FACTOR, 1)

class Node:

    ids = [n for n in range(1, MAX_NETWORK_SIZE)]
    id = 0

    def __init__(self, color, ntype, factor, flow):
        self.id = self.ids.pop(0)
        self.demand = int(np.random.uniform(1, MAX_QUANTITY))*flow
        self.private_value = RD(np.random.uniform(1, MAX_PRICE))
        self.color = color
        self.type = ntype
        self.price = RD(self.private_value*factor)

    def __str__(self):
        return str(self.id)
     
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    def bid(self):
        return {"price": RD(self.price), "demand": self.demand}

    def __repr__(self):
        return str(self.id)

    def data(self):
        return {"price": RD(self.price), \
                "value": RD(self.private_value), \
                "color": self.color,\
                 "type": self.type}


    def calculate_consistent_bid(self, seller_list):
        #cprintnode(self, '\n')
        #print(seller_list)
        # Simple calcuate, no opt-out
        #if len(seller_list) < 2 and self.demand > 1:
        #    G.add_edge(self, random.choice(G.nodes))
            
        sorted_sellers = sorted(seller_list, key=lambda x: x.price)
        if len(sorted_sellers) > 0:
            self.price = sorted_sellers[0].price
        return self.price
        # Add in opt-out function
        '''
        opt_out_demand = 0
        prices = []
        for seller in self.seller_group:
            prices.append(seller.market_price)

            opt_out_demand += seller.demand
            if opt_out_demand >= buyer.demand
                break
        self.bid = max(prices)

        if price_to_pay > seller.reserve_price:
            seller.market_price */
            self.increase_bidding_factor[winner_id]
        else:
            self.market_price[auction_round+1, seller] *= \
            self.decrease_bidding_factor[winner_id]
        '''


    def calculate_market_price(self, buyer_list):
        winner = None
        sorted_buyers = sorted(buyer_list, key=lambda x: x.price, reverse=True)
        print(sorted_buyers)
        #   self.reserve_price = sorted_buyers[1].price # WTF am I doing here?
        if len(sorted_buyers) > 0:
            winner = sorted_buyers[0]
        if len(sorted_buyers) > 1:
            self.price = sorted_buyers[1].price
        return winner
        opt_out_demand = 0


