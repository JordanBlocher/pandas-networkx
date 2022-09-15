import random
import networkx as nx
import numpy as np

from params import * 

class Initialize():

    def initialize_quantities(self):

        self.buyers_bid = {}
        for buyer in range(self.n_buyers):
            self.consistent_buyer_bid[buyer] = 0
        for seller in range(self.k_sellers):    
            self.buyers_bid[seller] = {}
        self.bidding_factor = self.calculate_bidding_factor()

        # Random increase/ decrease
        self.increase_bidding_factor = np.random.uniform(INCREASE_MIN,
                INCREASE_MAX, size=self.n_buyers)
        self.decrease_bidding_factor = np.random.uniform(DECREASE_MIN,
                DECREASE_MAX, size=self.n_buyers)


