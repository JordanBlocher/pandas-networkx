import numpy as np
import networkx as nx
import random
from termcolor import colored
import seaborn as sns

from models import Node
from nxn import nxNode, name, spectral_layout
import pandas as pd


    
'''
The auction holds all the live data, buyers and sellers
and passes a dataframe up to the auctioneer every time a 
players price changes. The memory in the auction is flash, 
and is updated the next time a player challenges the price.
'''

class Auction(nxNode):

    def __init__(self):
        self.type='auction'
        nxNode.__init__(self)

    def make_graph(self):
        global params, rng
        rng = nx.utils.create_random_state()
        params = self.make_params()
        self.start_time = params.start_time

        for node in range(params.nsellers):
            new_node = Node(params.seller)
            print("ADDING", new_node.type, new_node.name, '\n', new_node) 
            self.add_node(new_node)
        for node in range(params.nbuyers):
            new_node = Node(params.buyer)
            print("ADDING", new_node.type, new_node.name, '\n', new_node) 
            self.add_filter_star(new_node)
        
        pos = spectral_layout(self, dim=3)
        #print("POS", pos)
        #for node in self.nodes():
         #   node.pos = pos[node] 

        self.buyers   = self.buyers()
        self.nbuyers  = self.nbuyers()
        self.sellers  = self.sellers()
        self.nsellers = self.nsellers()
        self.print_auction()
     

    def node_filter(self, ntype=None, v=None):
        #print("IN FILTER", ntype, "node", v,'\n------------------------------\n')
        idx=pd.IndexSlice
        nbrs = pd.DataFrame()
        if v is not None:
            for n,u in self[v].T:
                nbrs = nbrs.append(self._node.loc[n]) 
            #print("\nNBRS1", nbrs.T)
            if ntype is not None:
                nbrs = nbrs.loc[ nbrs.type == ntype ]
                #print("\nNBRSTYPE2", nbrs.T)
            #print("\n---------------------------------\n")
        else:
            nbrs = self._node.loc[ self._node.type == ntype ]
        print("\n---------------------------------\nNBRS", nbrs.index)
        return nbrs

    def add_filter_star(self, node, v=None):
        print("ADDING", node, "STAR")

        nbrs = rsample(
                        self.node_filter(node.inv(), v),
                        params.g_max
                        )
        print("SAMPLED", nbrs)
        if v:
            nbrs.append(v)
        star_nodes = [node]+nbrs
        self.add_star(star_nodes)

    def update_auction(self, winner, seller):
        global params
        self.print_auction()
        seller.demand += 1
        winner.demand -= 1
        self.update_demand(winner)
        self.update_demand(seller)
        for ntype in ['seller', 'buyer']:
            if self.nnodes(ntype)-params.g_max<2:
               new_node = Node(params[ntype]) 
               self.add_filter_star(new_node)  
        '''
        The sellers can't add buyers to thier auction. If they
            do it causes instability.
        '''
        for buyer in self.buyers():
            if len(self.node_filter(buyer)) < 2:
                self.add_edge(buyer, random_choice(self.sellers))
         
    def update_demand(self, node):
        global params
        if node in self.nodes:
            if node.demand == 0:
                Node.names.append(node.name)
                self.remove_node(node)
                new_node = Node(params[node.type]) 
                self.add_filter_star(new_node)
                print("ADDED NODE", new_node.name)

    def update(self):
        global params
        params = self.make_params()
        for ntype in ['buyer', 'seller']:
            cnt = self.nnodes(ntype)-params['n'+ntype+'s']
            if cnt > 2:
                self.update_nodes(cnt, ntype)
            params.nnodes = self.nnodes()
        return params
  
    def update_nodes(self, cnt, ntype):
        global params
        for n in range(abs(cnt)):
            if cnt < 0:
                new_node = Node(params[ntype])
                self.add_filter_star(new_node) 
            else:
                #print("CHOOSING FROM", self.node_filter(ntype))
                choice = random_choice(self.node_filter(ntype))
                print("CHOICE", name(choice), choice,'\n-------------------\n')
                Node.names.append(name(choice))
                self.remove_node(name(choice))
        params['n'+ntype+'s']=self.nnodes(ntype)

    def buyers(self):
        return self._node.loc[ self._node.type == 'buyer'].T
    def sellers(self):
        return self._node.loc[ self._node.type == 'seller'].T
    def nbuyers(self):
        return len(self.buyers.T)
    def nsellers(self):
        return len(self.sellers.T)

    def print_auction(self, data=False):
        if data:
            for seller in self.sellers:
                print(colored(seller, 'magenta'), end=' ') 
            print('')
            for buyer in self.buyers:
                print(colored(buyer, 'green'), end=' ')
            print('')
        print(colored(str(self.nbuyers)+' buyers', 'green'), end=' ')
        print(colored(str(self.nsellers)+' sellers', 'magenta')) 
        for seller in self.sellers:
            print(colored(seller, 'magenta'), end=' ') 
            for buyer in self.node_filter('buyer', seller).T:
                print(colored(buyer, 'green'), end=' ')
            print('')
        return
 
# randomly sample from a list <-- should go in the class
def rsample(x, maxn):
    if len(x) < 2:
        raise ValueError 
    if maxn < len(x):
        u = random.sample(
                        [n for n in list(x.index)],
                        random.randint(2,maxn)
                        )
    else:
        rsample(x, len(x)-1)
    try:
        print("IN RSAMPLE", x.index)
        print("SAMPLE SET", u)
        return [x.loc[z] for z in u]
    except: 
        raise(KeyError,ValueError)
        return

def random_choice(x):
    n = random.sample(list(x.index),1)
    return x.loc[n[0]]
