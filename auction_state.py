import numpy as np
import networkx as nx
from termcolor import colored
from params import *
import yaml
import json
 
class AuctionState:
    
    def __init__(self, G, bid_history, seller, winner, name=None):
        g = nx.subgraph(G, bid_history + [seller])
        self.auction_state = g.__class__()
        self.auction_state.add_nodes_from(g.nodes(data=True))
        self.auction_state.add_edges_from(g.edges(data=True))
        
        nx.freeze(self.auction_state)
        mapping = dict(zip(G, range(1, len(G.nodes)+1)))
        self.auction_state_string = '\n'.join(nx.generate_gml(\
        G = nx.relabel_nodes(self.auction_state, mapping)))
        if name:
            with open(name, "a") as f:
                print(self.auction_state_string, file=f)    

    def print_auction_state(self, name=None):
        if name:
            self.auction_state = nx.read_gml(name)
        else:
            test = nx.parse_gml(self.auction_state_string)
        for node in self.auction_state.nodes:
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

