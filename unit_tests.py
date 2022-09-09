import random
import numpy as np
np.set_printoptions(precision=2)
from params import * 
from buyer import Buyer
from seller import Seller
from auction import Auction
import networkx as nx


def validate_params(params):
    nbuyers = params['buyers']['n']
    nsellers = params['sellers']['n']

    if params['nnodes'] =! nbuyers+nsellers:
        raise('population mismatch') 
    for i in range(100):
        x = params['g_max']
        if x < nbuyers or x < nsellers:
            raise('empty auction warning')

def test_buyer():
    buyer = Buyer()
    return True

def test_seller():
    seller = Seller()
    return True

def test_auction_singleton(): 
    auction = Auction()
    if auction.nbuyers + auction.msellers == len(auction.G.nodes):
        return auction

def test_add_seller(auction, buyer):
    deg = nx.degree(auction.G, buyer)
    cprintnode(buyer, '\n')
    auction.add_seller(buyer)
    print(deg)
    nx.degree(auction.G, buyer)
    if nx.degree(auction.G, buyer) != deg + 1:
        return False


# Execute with parameters
if __name__ == '__main__':
    if test_buyer() and test_seller():
        print("OK")

    auction = test_auction_singleton()
    if auction:
        print("OK")

    sellers = list(nx.subgraph_view(auction.G,filter_node=auction.seller_filter).nodes)
    buyers = list(nx.subgraph_view(auction.G,filter_node=auction.buyer_filter).nodes)

    buyer = buyers[0]
    if test_add_seller(auction, buyer):
        print("OK")


