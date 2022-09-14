import numpy as np
import networkx as nx
from node import Node

import time

class Clock(nx.Graph):

    ts = 0
    T = nx.Graph()

    def __init__(self, seller, winner, neighbors, start_time):
        ts = round(time.time()-start_time,4)
        nx.Graph.__init__(self,ts=ts, winner=winner, seller=seller)
        self.ts = ts
        self.winner = winner
        self.add_node(seller, weight=ts)
        self.add_node(winner, weight=ts)
        self.add_edge(self, seller)
        [self.winner.add_node(n) for n in neighbors]
        [self.winner.add_edge(self.winner, n) for n in neighbors]
        Clock.T.add_node(self, weight=self.ts)
        print("CLOCK")
        print(Clock.T.nodes)
        print(Clock.T.edges)
        for node in [n for n in Clock.T.nodes]: 
            if type(node) == Node:
                continue
            print("node")
            print(node.nodes)
            print(node.edges)
            if ts - node.ts < 0.5:
                for nb in neighbors:
                    for np in node:
                        if np == nb:
                            if Clock.T.has_edge(self, node):
                                weight=self.ts
                            else:
                                weight=node.ts
                            self.winner.add_edge(nb, np, weight=weight)
                            Clock.T.add_edge(self, node, weight=weight)
                    
    def __repr__(self):
        return str(self.ts)

    def __str__(self):
        return str(self.ts)


class Intersection:

    I = nx.Graph()

    def __init__(self):
        pass
        #G.add_node(
