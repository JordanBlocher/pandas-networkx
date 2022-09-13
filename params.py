import random 
import networkx as nx
import pandas as pd
from termcolor import colored
import os
from enum import Enum

def make_params():
    global start_time, nsellers, nbuyers, noise, auction_round

    auction_round = 0
    rng = nx.utils.create_random_state()

    option = False
    nnodes = nbuyers+nsellers
    max_price = 15
    noise_low = .2, #nOTE: TRY NEGATIVE VALUES
    noise_high = 1.2

    buyer_init_factor = rng.uniform(.5, .8) # bid under
    buyer_max_price = 15
    buyer_max_quantity = 3
    buyer_inc = [.9, 1] # 1.2 1.5
    buyer_dec = [0.8, 9] #0.3 0.7

    seller_init_factor = rng.uniform(1.2, 1.5) # bid over
    seller_max_price = 15
    seller_max_quantity = 10
    seller_inc = [.1, 1]
    seller_dec = [.1, 1]

    return dict(
    auction_round = auction_round,
    option = option,
    noise = noise,
    nsellers = nsellers,
    nbuyers = nbuyers,
    # nnodes, g_mod, and nbuyers/sellers are not independent, 
    # there should be an optimal
    # formula for EQ
    nnodes = nnodes,
    g_max = min(nbuyers, nsellers)-2,
    noise_factor = dict(
                        low = noise_low,
                        high = noise_high,
        ),
    buyer = dict(
            init_factor = buyer_init_factor,
            max_price = buyer_max_price,
            max_quantity = buyer_max_quantity,
            inc = buyer_inc,
            dec = buyer_dec,
            flow = -1,
            price = []
            ),
    seller = dict(
            init_factor = seller_init_factor,
            max_price = seller_max_price,
            max_quantity = seller_max_quantity,
            inc = seller_inc,
            dec = seller_dec,
            flow = 1,
            price = []
            )
        )
