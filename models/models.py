import numpy as np
import networkx as nx
from nxn import nxNode
from .node import Node
import pandas as pd
import time

class Clock(nxNode):

    ts = pd.to_timedelta(0)
    index = ['ts', 'winner']
    T = nxNode()

    def __init__(self, seller, winner, neighbors, ts):
        self.ts = pd.to_timedelta(ts)
        self.winner = winner.name
        nxNode.__init__(self,
                        ts=self.ts,
                        winner=self.winner,
                        )
        self.add_node(seller)
        self.add_node(winner)
        self.add_edge(self, seller, ts=self.ts)
        for v in neighbors:
            self.winner.add_node(v)
            self.winner.add_edge(self.winner, v)
        Clock.T.add_node(self)
        for node in Clock.T.nodes(): 
            if type(node) == Node:
                continue
            if self.ts - node.ts < 0.5:
                for nb in neighbors:
                    for np in node_ts:
                        if np == nb:
                            if Clock.T.has_edge(self, node):
                                ts=self.ts
                            else:
                                ts=node.ts
                            self.winner.add_edge(nb, np, ts=ts)
                            Clock.T.add_edge(self, node, ts=ts)
   
    def add_edge(self, u, v, ts=None):
        super().add_edge(u ,v,
                    ts=pd.to_timedelta(ts),
                    source=u.name,
                    target=v.name,
                    )

    def __str__(self):
        return f"{self.name}"

    def __array__(self):
        return np.array([
                self.ts,
                self.winner
                ], dtype=object)


