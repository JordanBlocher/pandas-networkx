from nxn import * 
import nxn as nxn
from models import *
from auction import *
from scripts import *
from params import make_params
from sim import *
import networkx as nx
import pandas as pd
import numpy as np
import random
import time
from termcolor import colored
from tests import *

values = pd.read_csv('./params/params.dat')
values.loc[0].nbuyers=15
values.loc[0].nsellers=7
f = open('./params/params.dat','w')
f.write(values.to_csv())
f.close()

params=make_params()


nd, nds = test_node(params)
Node.name=0
Node.ids=[]
g = test_auction()
n=g._node
e=g._adj
Node.name=0
Node.ids=[]
G = test_auctioneer()
N=G._node
E=G._adj


