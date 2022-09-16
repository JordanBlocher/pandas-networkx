import numpy as np
import networkx as nx
from nx import nxNode
import random
from termcolor import colored
from models import Node,Clock
from auction import Auction, Auctioneer
from nx import *
from params import make_params
from globals import *


a = Auction()
a.make_params = make_params
a.make_graph()

nodes = list(a.nodes)

n = nxNode()

def test():
    global a, n, nodes
    print(type(n))
    n = nodes[0]
    print(type(n))
    for i in range(1,len(nodes)):
        n.add_node(nodes[i])

    ne=nodes[len(nodes)-1]
    ne.price=200
    n.add_node(ne)

    n1=nodes[1]
    n2=nodes[2]
    n3=nodes[3]
    n4=nodes[4]
    n.add_edge(n1,n2,ts=10)
    n.add_edge(n3,n2,ts=11)
    n.add_edge(n1,n2,ts=12)
    n.add_edge(n1,n4,ts=13)
    n.add_edge(n3,n4,ts=13)

    return a, n, nodes
