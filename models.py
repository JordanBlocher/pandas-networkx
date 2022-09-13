import numpy as np
import networkx as nx

from node import Node
import time


class Clock:

    T = nx.Graph()
    t = nx.Graph()
    ts = 0

    def __init__(self, seller, winner, neighbors, nsellers, start_time):
        self.ts = round(time.time()-start_time,4)
        self.t = nx.Graph()
        self.t.add_node(seller, demand=seller.demand, value=seller.private_value)
        self.t.add_node(winner, demand=winner.demand, value=winner.private_value)
        self.t.add_edge(winner, seller, weight=self.ts)
        Clock.T.add_node(self, weight=self.ts)
        for node in [n for n in Clock.T.nodes]: 
            if type(node) == Node:
                continue
            if self.ts - node.ts < 0.5:
                for node_ns in neighbors:
                    if node_ns in node.t.nodes:
                        if Clock.T.has_edge(winner, node):
                            print("HOPPING!")
                        Clock.T.add_edge(winner, node, weight=self.ts)


    def __repr__(self):
        return str(self.ts)


class Intersection:

    I = nx.Graph()

    def __init__(self):
        pass
        #G.add_node(
