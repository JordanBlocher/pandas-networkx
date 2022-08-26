from params import * 
from prettytable import PrettyTable
import numpy as np
import networkx as nx
from buyer import Buyer
from seller import Seller
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation

from user import User
from termcolor import colored


class Auction:

    G = nx.DiGraph()
    buyers = []
    sellers = []

    def __init__(self): # This should be done with networkx

        self.G.add_nodes_from([Seller() for n in range(MSELLERS)])
        self.G.add_nodes_from([Buyer() for n in range(NBUYERS)])
        self.nbuyers = NBUYERS
        self.msellers = MSELLERS   
        self.build_connections()

    def seller_filter(self, node):
        return type(node) == type(Seller())

    def buyer_filter(self, node):
        return type(node) == type(Buyer())

    def sellers(self):
        Auction.sellers = list(nx.subgraph_view(self.G, \
                filter_node=self.seller_filter).nodes)
        return Auction.sellers

    def buyers(self):
        Auction.buyers = list(nx.subgraph_view(self.G, \
                filter_node=self.buyer_filter).nodes)
        return Auction.buyers

    def buyer_list(self, seller):
        return [n for n in nx.neighbors(\
                nx.reverse_view(self.G), seller)]

    def build_connections(self, node, node_list):
        for node in node_list:
            node_list = RANDOM(self.sellers())
            self.G.add_weighted_edges_from(\
                [(node, node, RD(buyer.price)) \
                 for node1 in node1_list])

    def update_auction(self, seller, winner):
        if winner.quantity <= 0:
            self.G.remove_node(winner)
            self.nbuyers -= 1
        if seller.quantity <= 0:
            self.G.remove_node(seller)
            self.msellers -= 1
        winner.color = 'green'
   
    def print_auction(self):
        
        print('\t', end='')
        for node in Auction.sellers:
            cprintnode(node, '\t')
        print('')
        buyers = []
        n=0
        m=0
        for seller in Auction.sellers:
            buyers.append([n for n in nx.neighbors(nx.reverse_view(self.G), seller)])
        for k in range(len(Auction.buyers)):
            print('\t', end='')
            for m in range(len(Auction.sellers)):
                if len(buyers[m]) > n:
                    cprintnode(buyers[m%3][n], '\t')
                else:
                    print('\t\t', end='')
            n+=1
            print(' ')
