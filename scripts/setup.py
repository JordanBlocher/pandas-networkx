import numpy as np
import networkx as nx
from nx import nxNode
import random
from termcolor import colored
from models import Node
from auction import Auction, Auctioneer
from nx import *
from params import make_params
from globals import *

def test():

   a = Auction()
   a.make_params = make_params
   a.make_graph()

   nodes = list(a.nodes)
   n = nodes[0]
   n1 = nodes[1]

   return a, n, n1, nodes

