import random 
import networkx as nx
import pandas as pd
from termcolor import colored
import os
import time

def make_params():
    global nbuyers, nsellers, noise, rounds, start_time

    rng = nx.utils.create_random_state()
    rng.seed(random.randint(1,999999))

    df=pd.read_csv('./params/params.dat').loc[0]
    nnodes = df.nbuyers+df.nsellers

    return pd.Series(dict(
    start_time=time.time(),
    option = df.option,
    noise = df.noise,
    nsellers = df.nsellers,
    nbuyers = df.nbuyers,
    # nnodes, g_mod, and nbuyers/sellers are not independent, 
    # there should be an optimal
    # formula for EQ
    nnodes = nnodes,
    g_max = max(min(df.nbuyers, df.nsellers)-2, 3),
    noise_factor = pd.Series(dict(
                        low = df.noise_low,
                        high = df.noise_high,
        )),
    buyer = pd.Series(dict(# negative flow wants to send out 
            init_factor = rng.uniform(df.buyer_init_0, df.buyer_init_1),
            max_price = df.buyer_max_price,
            max_quantity = df.buyer_max_quantity,
            inc_factor = rng.uniform(
                                df.buyer_inc_0,
                                df.buyer_inc_1,
                                size=nnodes+15
                                ),
            dec_factor = rng.uniform(
                                df.buyer_inc_0,
                                df.buyer_inc_1,
                                size=nnodes+15
                                ),         
            flow=-1,
            price = rng.poisson(
                        df.buyer_max_price,
                        size=nnodes+15
                        )
            )),
    seller = pd.Series(dict( 
            init_factor=rng.uniform(df.seller_init_0, df.seller_init_1),
            max_price=df.seller_max_price,
            max_quantity=df.seller_max_quantity,
            inc_factor = rng.uniform(
                                df.seller_inc_0,
                                df.seller_inc_1,
                                size=nnodes+15
                                ),
            dec_factor = rng.uniform(
                                df.seller_dec_0,
                                df.seller_dec_1,
                                size=nnodes+15
                                ),         
            flow=1,
            price = rng.poisson(
                        df.seller_max_price,
                        size=nnodes+15
                        )
            
            ))
        ))


