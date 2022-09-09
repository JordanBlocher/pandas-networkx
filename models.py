import numpy as np
import networkx as nx

from node import Node
import time


class Clock:

    T =  nx.Graph()

    def __init__(self, seller, winner, neighbors, nsellers, start_time):
        self.ts = round(time.time()-start_time,2)
        self.t = nx.Graph()
        self.t.add_node(seller, demand=seller.demand, value=seller.private_value)
        self.t.add_node(winner, demand=winner.demand, value=winner.private_value)
        self.t.add_edge(winner, seller, weight=seller.price)
        Clock.T.add_node(self, demand=seller.demand+winner.demand)
        for node_ns in neighbors:
            for node in list(Clock.T.nodes): 
                if node_ns in list(node.t.nodes):
                    if node.ts < self.ts:
                        Clock.T.add_edge(winner, node_ns,  weight=winner.price)
                    else:
                        Clock.T.add_edge(node_ns, winner, weight=winner.price)


    def __repr__(self):
        return str(self.ts)

    def print(self):
        pass



class Intersection:

    I = nx.Graph()

    def __init__(self):
        pass
        #G.add_node(
