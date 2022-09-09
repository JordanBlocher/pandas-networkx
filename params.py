import random 
import networkx as nx
import pandas as pd
from termcolor import colored
import os
from enum import Enum


def make_params():
    MNSZE = 200
    rng = nx.utils.create_random_state()

    return dict(
    option = False,
    noise = True,
    # nnodes, g_mod, and n are not independent, there should be an optimal
    # formula for EQ
    max_price = 15,
    nnodes = 35, 
    nbuyers = 13,
    nsellers = 11,
    price = rng.poisson(num['max_price'], size=MNSZE),
    g_max = min(num['nbuyers'], num['nsellers'])-2,
    noise = dict(
            low = .2, #nOTE: TRY NEGATIVE VALUES
            high = 1.2,
            ),
    buyer = dict(
            init_factor = rng.uniform(.5, .8), # bid under
            max_price = 15,
            max_quantity = 10,
            flow = -1,
            inc_max = 1, #1.5
            inc_min = .9, #1.2
            dec_max = 0.9, #0.7
            dec_min = 0.8, #0.3
            ),
    inc_factor = rng.uniform(
                            buyer['inc_min'], 
                            buyer['inc_max'], 
                            size=MNSZE
                            ),
    dec_factor = rng.uniform(
                            buyer['dec_min'], 
                            buyer['dec_max'], 
                            size=MNSZE
                            ),
    seller = dict(
            init_factor = rng.uniform(1.2, 1.5), # bid over
            max_price = 15,
            max_quantity = 20,
            flow = 1,
            increase_max = 1,
            increase_min = .1,
            decrease_max = 1,
            decrease_min = .1,
            )
        )
