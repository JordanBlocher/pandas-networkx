import random 
import networkx as nx
import pandas as pd
from termcolor import colored
import os
from globals import *

def make_params():

    rng = nx.utils.create_random_state()

    option = False
    nnodes = nbuyers+nsellers
    noise_low = .2, #nOTE: TRY NEGATIVE VALUES
    noise_high = 1.2

    buyer_init_factor = rng.uniform(.5, .8) # bid under
    buyer_max_price = 75
    buyer_max_quantity = 70
    buyer_inc = [.9, 1] # 1.2 1.5
    buyer_dec = [0.8, 9] #0.3 0.7

    seller_init_factor = rng.uniform(1.2, 1.5) # bid over
    seller_max_price = 95
    seller_max_quantity = 100
    seller_inc = [.1, 1]
    seller_dec = [.1, 1]

    return dict(
    auction_round = auction_round,
    start_time = start_time,
    option = option,
    noise = noise,
    nsellers = nsellers,
    nbuyers = nbuyers,
    # nnodes, g_mod, and nbuyers/sellers are not independent, 
    # there should be an optimal
    # formula for EQ
    nnodes = nnodes,
    g_max = max(min(nbuyers, nsellers)-2, 3),
    noise_factor = dict(
                        low = noise_low,
                        high = noise_high,
        ),
    buyer = dict(
            init_factor = buyer_init_factor,
            max_price = buyer_max_price,
            max_quantity = buyer_max_quantity,
            inc_factor = rng.uniform(
                                buyer_inc[0],
                                buyer_inc[1],
                                size=nnodes+15
                                ),
            dec_factor = rng.uniform(
                                buyer_inc[0],
                                buyer_inc[1],
                                size=nnodes+15
                                ),         
            flow=1,
            price = rng.poisson(
                        buyer_max_price,
                        size=nnodes+15
                        )
            ),
    seller = dict(
            init_factor=seller_init_factor,
            max_price=seller_max_price,
            max_quantity=seller_max_quantity,
            inc_factor = rng.uniform(
                                seller_inc[0],
                                seller_inc[1],
                                size=nnodes+15
                                ),
            dec_factor = rng.uniform(
                                seller_dec[0],
                                seller_dec[1],
                                size=nnodes+15
                                ),         
            flow=-1,
            price = rng.poisson(
                        seller_max_price,
                        size=nnodes+15
                        )
            
            )
        )


