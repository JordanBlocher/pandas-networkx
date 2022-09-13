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
        print([str(n) for n in neighbors])
        print(Clock.T.nodes)
        for node in list(Clock.T.nodes): 
            print(node.t.nodes)
            for node_ns in neighbors:
                if node_ns in list(node.t.nodes):
                    print("ADDING EDGE!!!\n\n\n")
                    if node.ts < self.ts:
                        Clock.T.add_edge(self, node, weight=winner.price)


class Intersection:

    I = nx.Graph()

    def __init__(self):
        pass
        #G.add_node(
