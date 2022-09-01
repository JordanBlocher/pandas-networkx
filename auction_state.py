import numpy as np
import networkx as nx
from termcolor import colored
from params import *
import yaml
import json
 
class AuctionState:
    
    def __init__(self, G, bid_history, seller, winner):
        primary_inflencing_set =  nx.ego_graph(G, winner, 1, False)
        self.nodes = bid_history + [seller]
        self.winner = winner

    def print_auction_state(self):
        for node in self.nodes:
            cprintnode(node, '\t')
        print(' ')

    def get_info(self, seller):
        if nx.is_tree(self.auction_state):
            print("IS A TREE!!")
            T = nx.to_nested_tuple(nx.to_undirected(self.auction_state), seller)
            print(nx.forest_str(T, sources=[0]))
            mapping = dict(zip(self.auction_state, range(0, len(self.auction_state.nodes))))
            R = nx.to_prufer_sequence(nx.to_undirected(nx.relabel_nodes(self.auction_state, mapping)))
            self.R = [n for n in range(len(R))]
            for i in range(len(R)):
                self.R[i] = list(self.auction_state.nodes)[list(R)[i]]

    def print_info(self):
       print(self.T)
       print(self.R) 

    def tree_to_newick(self, root=None):
        if root is None:
            roots = list(filter(lambda p: p[1] == 0, self.G.in_degree()))
            assert 1 == len(roots)
            root = roots[0][0]
        subgs = []
        for child in g[root]:
            if len(g[child]) > 0:
                subgs.append(tree_to_newick(self.G, root=child))
            else:
                subgs.append(child)
        return "(" + ','.join(subgs) + ")"

