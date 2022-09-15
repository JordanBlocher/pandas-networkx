import numpy as np
import networkx as nx
from node import Node
from nxnode import nxNode

import time

class Clock(nxNode):

    ts = 0
    T = nxNode()

    def __init__(self, seller, winner, neighbors, ts):
        self.ts = ts
        self.winner = winner
        self.add_node(seller)
        self.add_node(winner)
        self.add_edge(self, seller, ts=self.ts)
        for v in neighbors:
            self.winner.add_node(v)
            self.winner.add_edge(self.winner, v)
        Clock.T.add_node(self)
        for node in [n for n in Clock.T.nodes]: 
            if type(node) == Node:
                continue
            if self.ts - node.ts < 0.5:
                for nb in neighbors:
                    for np in node:
                        if np == nb:
                            if Clock.T.has_edge(self, node):
                                ts=self.ts
                            else:
                                ts=node.ts
                            self.winner.add_edge(nb, np, ts=ts)
                            Clock.T.add_edge(self, node, ts=ts)
                    
    def __repr__(self):
        return str(self.ts)

    def __str__(self):
        return str(self.ts)


class Intersection:

    I = nx.Graph()

    def __init__(self):
        pass
        #G.add_node(
