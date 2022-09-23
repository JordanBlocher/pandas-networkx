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
values.loc[0,'nbuyers']=11
values.loc[0,'sellers']=7
f = open('./params/params.dat','w')
f.write(values.to_csv(index=False).strip())
f.close()

params=make_params()


nd, nds = test_node(params)
Node.name=0
Node.ids=[]
print("Passed node test...")
g = test_auction()
n=g._node
e=g._adj
print("Passed auction test...")
Node.name=0
Node.ids=[]
G = test_auctioneer()
N=G._node
E=G._adj
G.run_auctions(0)
print("Passed auctioneer test...")
Node.name=0
Node.ids=[]
sim = MarketSim(make_params)
rnum=0
while True:
    print("\n'---------------------------------ROUND", rnum,'----------------------------------\n')
    sim.do_round(rnum)
    rnum+=1
