import numpy as np
import networkx as nx

from node import Node
import time


class Clock:

    T = nx.Graph()
    t = nx.Graph()
    ts = 0
    neighbors = None
    auction_round = 0

    def __init__(self, seller, winner, neighbors, start_time, auction_round):
        self.seller = seller
        self.winner = winner
        winner.neighbors = neighbors
        self.ts = round(time.time()-start_time,4)
        self.auction_round = auction_round
        self.t = nx.Graph()
        self.t.add_node(seller, weight=self.ts) 
        self.t.add_node(winner, weight=self.ts)
        self.t.add_edge(winner, seller, weight=self.ts)
        Clock.T.add_node(self, weight=self.ts)
        for node in [n for n in Clock.T.nodes]: 
            if type(node) == Node:
                continue
            if self.ts - node.ts < 0.5:
                for node_ns in neighbors:
                    if node_ns in node.t.nodes:
                        if Clock.T.has_edge(winner, node):
                            #Clock.T.add_edge(self, node, weight=node.ts)
                        Clock.T.add_edge(winner, node, weight=self.ts)
    
    def time_node_filter(node):
        return type(node) == Clock
        
    def node_filter(node):
        return type(node) == Node

    def time_nodes():
        return list(nx.subgraph_view(Clock.T, filter_node=Clock.time_node_filter).nodes)

    def inf_nodes():
        return list(nx.subgraph_view(Clock.T, filter_node=Clock.node_filter).nodes)

    def base_nodes():
        base_nodes = []
        for node in [n for n in Clock.T.nodes]: 
            if type(node) == Node:
                if node not in base_nodes:
                    base_nodes.append(node)
                continue
            for node_b in node.t.nodes:
                if node_b not in base_nodes:
                    base_nodes.append(node_b)
            for node_n in node.t.nodes:
                if node_n not in base_nodes:
                    base_nodes.append(node_n)
        return base_nodes
 

    def __repr__(self):
        return str(self.ts)

class Intersection:

    I = nx.Graph()

    def __init__(self):
        pass
        #G.add_node(
