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
        for i in range(params['n'+str(ntype)+'s']):
            nodes.append(Node(params[ntype]))
    return nodes

#@pytest.fixture
def auction():
    auction = Auction()
    auction.make_params = make_params
    auction.make_graph()
    return auction

def test_add_node(nodes):
    n = nodes[0]
    for i in range(1,len(nodes)):
        n.add_node(nodes[i])
        print(n.nodes())
    return n

def test_add_edge(nodes):
    n= nodes[0]
    n1=nodes[1]
    n2=nodes[2]
    n3=nodes[3]
    n4=nodes[4]
    n5=nodes[5]
    n6=nodes[6]
    n7=nodes[7]
    n8=nodes[8]
    n9=nodes[9]

    n.add_edge(n1,n2,ts=10)
    n.add_edge(n3,n2,ts=11)
    n.add_edge(n1,n2,ts=12)
    n.add_edge(n1,n4,ts=13)
    n.add_edge(n4,n5,ts=13)
    n.add_edge(n3,n6,ts=13)
    n.add_edge(n4,n7,ts=13)
    n.add_edge(n4,n8,ts=13)
    n8.price = 888
    n.add_edge(n2,n9,ts=13)
    n.add_edge(n2,n5,ts=13)
    n6.value = 999
    n.add_edge(n1,n6,ts=13)
    n.add_edge(n3,n7,ts=13)
    n.add_edge(n1,n8,ts=13)
    n9.value = 111
    n.add_edge(n3,n9,ts=13)
 
    return n

def test_node(params):
    node = nodes(params)
    n = test_add_node(node)
    n = test_add_edge(node)

    nodez = n.nodes()
    return n, nodez

def test_clock(winner, seller):
    start = time.time()
    buyers=auction.node_list('buyer')
    sellers = auction.node_list('seller')
    c = Clock(winner=buyers[0], 
              seller=sellers[0], 
              neighbors=auction.node_list(buyers[0]), 
              ts=pd.to_timedelta(0)
              )
      
    return c

