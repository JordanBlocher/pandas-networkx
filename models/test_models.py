import pytest 
from .node import Node
from params import make_params
import pandas as pd

#@pytest.fixture
def params():
    params = make_params()
    return params

#@pytest.fixture
def nodes(params):
    nodes = []
    for ntype in ['buyer', 'seller']:
        for i in range(5):
            nodes.append(Node(params[ntype]))
    return nodes

def test_add_node(nodes):
    n = nodes[0]
    for i in range(1,len(nodes)):
        n.add_node(nodes[i])
    return n

def test_add_edge(nodes):
    n = nodes[0]
    n1=nodes[1]
    n2=nodes[2]
    n3=nodes[3]
    n4=nodes[4]

    n.add_edge(n1,n2,ts=10)
    n.add_edge(n3,n2,ts=11)
    n.add_edge(n1,n2,ts=12)
    n.add_edge(n1,n4,ts=13)
    n.add_edge(n3,n4,ts=13)

def test():
    params = make_params()
    node = nodes(params)
    n = test_add_node(node)

    nodez = n.nodes()
    return n, nodez

