import numpy as np
import networkx as nx

import time

class nxNode(nx.Graph):

    id = 0

    def __init__(self):
        super().__init__()
        self.id = nxNode.id
        nxNode.id += 1

    def __repr__(self):
        return str(self.id)

class Clock(nxNode):

    ts = 0
    auction_round = 0

    def __init__(self, seller, winner, neighbors, start_time, auction_round):
        super().__init__(start_time)
        self.add_edge(winner, seller)
        [self.add_edge(winner, n) for n in neighbors]
        self.ts = round(time.time()-start_time,4)
        self.auction_round = auction_round
        Clock.add_node(self, weight=seller)
        for node in [n for n in Clock.nodes]: 
            if self.ts - node.ts < 0.5:
                for n in neighbors:
                    if n in nx.neighbors(node):
                        Clock.add_edge(self, node, weight=winner)
    

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
