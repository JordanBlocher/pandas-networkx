import random
import numpy as np
np.set_printoptions(precision=2)
from node import Node
from market_sim import MarketSim
from auctioneer import Auctioneer
import networkx as nx
import time

from app import make_params

nbuyers = 7
nsellers = 5
noise = False
nrounds = 10

def validate_params():
    params = make_params()
    nbuyers = params['nbuyers']
    nsellers = params['nsellers']

    if params['nnodes'] != nbuyers+nsellers:
        raise('population mismatch') 
    for i in range(100):
        x = params['g_max']
        if x < nbuyers or x < nsellers:
            raise('empty auction warning')

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
    pass




