import pytest

def run(make_params):
    global params
    params = make_params()
    if validate_params():
        print("OK")

    if test_rsample():
        print("OK")
    
    time.sleep(20)
    sim = test_auction_singleton() # live testing (goes last)
    if sim.fnum == 1:
        print("OK")


def validate_params():
    nbuyers = params['nbuyers']
    nsellers = params['nsellers']

    if params['nnodes'] != nbuyers+nsellers:
        raise ValueError #'population mismatch'
    for i in range(100):
        x = params['g_max']
        if x < nbuyers or x < nsellers:
            raise ValueError# 'empty auction warning'

    return 0

def test_rsample():
    z = reversed(range(2,params['nnodes']))
    for n in z: 
        x = range(2,n)
        try:
            u = rsample(x, params['g_max'])
        except ValueError:
            raise 'distribution too small'
    x = range(2,params['nnodes'])
    z = range(2,params['nnodes'])
    for n in z: 
        try:
            u = rsample(x, n)
        except ValueError:
            raise 'g_max too big'
    for n in z: 
        x = range(n,params['nnodes'])
        try:
            u = rsample(x, params['g_max'])
        except ValueError:
            raise 'g_max too big'
 
    return 0
 

def test_auction_singleton(): 
    sim = MarketSim(make_params)
    return sim

def test_add_node(auction, buyer):
 
    buyer = Node(params['buyer'])
    seller = Node(params['seller'])
    try: 
        seller.add_node(buyer)
    except ValueError: 
        raise 'add node to node failed'



@pytest.fixture(autouse=True)
def add_nx(doctest_namespace):
    doctest_namespace["nx"] = networkx

# Do modules load?
try:
    from node import Node
except ImportError:
    raise "Module Node not imported" 

try:
    from nxnode import nxNode
except ImportError:
    raise "Module nxNode not imported" 

try:
    from market_sim import MarketSim
except ImportError:
    raise "Module MarketSim not imported" 

try:
    from auctioneer import Auctioneer
except ImportError:
    raise "Module Auctioneer not imported" 

try:
    from params import make_params
    params = make_params()
except ImportError:
    raise "Params not imported" 

try:
    from auction import Auction, rsample
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



