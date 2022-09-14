import pytest

nbuyers = 7
nsellers = 5
noise = False
nrounds = 10


def validate_params(params):
    nbuyers = params['nbuyers']
    nsellers = params['nsellers']

    if params['nnodes'] != nbuyers+nsellers:
        raise('population mismatch') 
    for i in range(100):
        x = params['g_max']
        if x < nbuyers or x < nsellers:
            raise('empty auction warning')

    return 0

def test_auction_singleoton(): 
    start_time = time.time()     
    sim = MarketSim()
    sim.make_graph(make_params, start_time)
    sim.make_fig()
    return sim

def test_add_node(auction, buyer):
    deg = nx.degree(auction.G, buyer)
    cprintnode(buyer, '\n')
    auction.add_seller(buyer)
    print(deg)
    nx.degree(auction.G, buyer)
    if nx.degree(auction.G, buyer) != deg + 1:
        return False

# Execute with parameters
if __name__ == '__main__':
    params = make_params()
    if validate_params(params):
        print("OK")

@pytest.fixture(autouse=True)
def add_nx(doctest_namespace):
    doctest_namespace["nx"] = networkx

# Do modules load?
try:
from node import Node
except ImportError:
    raise "Module Node not imported" 

try:
from market_sim import MarketSim
except ImportError:
    raise "Module MarketSim not imported" 

try:
from auctioneer import Auctioneer
except ImportError:
    raise "Module Auctioneer not imported" 

try:
from app import make_params
except ImportError:
    raise "Params not imported" 


# What dependencies are installed?

try:
import time
except ImportError:
    has_time = False

try:
    import numpy

    has_numpy = True
except ImportError:
    has_numpy = False

try:
    import scipy

    has_scipy = True
except ImportError:
    has_scipy = False

try:
    import matplotlib

    has_matplotlib = True
except ImportError:
    has_matplotlib = False

try:
    import pandas

    has_pandas = True
except ImportError:
    has_pandas = False

try:
    import dash
except ImportError:
    has_dash = False

try:
    import seaborn
except ImportError:
    has_seaborn = False

try:
    import sympy

    has_sympy = True
except ImportError:
    has_sympy = False



