import numpy as np
import networkx as nx
from nx import nxNode

import time

class Clock(nxNode):

    ts = 0
    T = nx.Graph()

    def __init__(self, seller, winner, neighbors, ts):
        self.ts = ts
        self.winner = winner
        self.add_node(seller)
        self.add_node(winner)
        self.add_edge(self, seller, ts=self.ts)
        for v in neighbors:
            self.winner.add_node(v)
            self.winner.add_edge(self.winner, v)
        Clock.add_node(self)
        for node in [n for n in Clock.nodes]: 
            if type(node) == Node:
                continue
            if self.ts - node.ts < 0.5:
                for nb in neighbors:
                    for np in node:
                        if np == nb:
                            if Clock.has_edge(self, node):
                                ts=self.ts
                            else:
                                ts=node.ts
                            self.winner.add_edge(nb, np, ts=ts)
                            Clock.add_edge(self, node, ts=ts)
                    
    def __repr__(self):
        return str(self.ts)

    def __str__(self):
        return str(self.ts)


