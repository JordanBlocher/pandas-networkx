import numpy as np
import networkx as nx
import random
from termcolor import colored
from models import Node,Clock
from auction import Auction, Auctioneer
from nx import *
from params import make_params
from params.globals import *
import time
import pytest


def auction():
    auction = Auction()
    auction.make_params = make_params
    auction.make_graph()
    return auction


def test(auction):
    start = time.time()
    buyers=auction.buyer_list()
    sellers = auction.seller_list()
    c = Clock(winner=buyers[0], 
              seller=sellers[0], 
              neighbors=auction.buyer_list(buyers[0]), 
              ts=round((time.time()-start)*10000,4)
              )
      
    return c

