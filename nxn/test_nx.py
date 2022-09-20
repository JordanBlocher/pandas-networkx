import pytest 
from nx import *

@pytest.fixture
def nodes():
    nodes = []
    for i in range(20):
        nodes.append(nxNode(id=i, ts=1))
    return nodes

def test_nxnode():
    n = nxNode()

def test_add_node(nodes):
    for i in range(20):
        nodes.append(nxNode(id=i, ts=1))
    n = nodes[0]
    for i in range(1,len(nodes)):
        n.add_node(nodes[i])

def test_assignment(nodes):
    ne=nodes[len(nodes)-1]
    ne.price=200
    n.add_node(ne)


def test_add_edge(nodes):
    n1=nodes[1]
    n2=nodes[2]
    n3=nodes[3]
    n4=nodes[4]

    n.add_edge(n1,n2,ts=10)
    n.add_edge(n3,n2,ts=11)
    n.add_edge(n1,n2,ts=12)
    n.add_edge(n1,n4,ts=13)
    n.add_edge(n3,n4,ts=13)

def nodes():
    nodes = []
    for i in range(20):
        node = nxNode(id=i, ts=i)
        nodes.append(node)
    return nodes
