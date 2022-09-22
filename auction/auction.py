import numpy as np
import networkx as nx
import random
from termcolor import colored
import seaborn as sns

from models import Node
from nxn import nxNode, spectral_layout, name
import pandas as pd
import time


    
'''
The auction holds all the live data, buyers and sellers
and passes a dataframe up to the auctioneer every time a 
players price changes. The memory in the auction is flash, 
and is updated the next time a player challenges the price.
'''

class Auction(nxNode):


    def __init__(self):
        self.name='auction'
        nxNode.__init__(self)

    def make_graph(self):
        global params, rng
        rng = nx.utils.create_random_state()
        params = self.make_params()
        self.start_time = params.start_time

        for node in range(params.nsellers):
            new_node = Node(params.seller)
            self.add_node(new_node)
        for node in range(params.nbuyers):
            new_node = Node(params.buyer)
            self.add_star(new_node)
        
        pos = spectral_layout(self, dim=3)
        #print("POS", pos)
        #for node in self.nodes():
         #   node.pos = pos[node] 

        self.buyers   = self.buyers()
        self.nbuyers  = self.nbuyers()
        self.sellers  = self.sellers()
        self.nsellers = self.nsellers()
        self.print_auction()
     
    def node_list(self, ntype=None, v=None):
        nodes = self.node_filter(ntype, v)
        idx = [n for n in nodes.index]
        return iter(nodes.loc[n] for n in idx)

    def node_filter(self, ntype=None, v=None):
        #print("IN FILTER", ntype, '\n------------------------------\n')
        idx=pd.IndexSlice
        nbrs = pd.DataFrame()
        if v is not None:
            #print("IN FILTER node", name(v), '\n------------------------------\n')
            for u,w in self[v].T:
                if name(u) == name(v):
                    nbrs = nbrs.append(self._node.loc[name(w)]) 
                elif name(w) == name(v):
                    nbrs = nbrs.append(self._node.loc[name(u)]) 
                #print("\nNBRS1", list(nbrs.index))
            if ntype is not None:
                nbrs = nbrs.loc[ nbrs['type'] == ntype ]
                #print("\nNBRSTYPE2", list(nbrs.index))
            #print("\n---------------------------------\n")
        else:
            nbrs = self._node.loc[ self._node['type'] == ntype ]
        #print("\n---------------------------------\nNBRS", nbrs)
        #print("\n---------------------------------\n")
        return nbrs

    def add_star(self, node, v=None):
        #print("ADDING", node.type, "STAR")

        nbrs = rsample(
                        self.node_filter(Node.inv(node), v),
                        params.g_max
                        )
        #print("SAMPLED", nbrs)
        if v and v not in nbrs:
            nbrs.append(v)
        star_nodes = [node]+nbrs
        nlist = iter(star_nodes)
        try:
            v = next(nlist)
        except StopIteration:
            return
        self.add_node(v)
        #print("CENTER", name(v), '\n')
        edges = ((v, n) for n in nlist)
        for v, n in edges:
            #print("HERE: EDGE", v,n)
            self.add_edge(v, n)

    def add_node(self, node):
        nxNode.add_node(self, node)

    def update_auction(self, winner, seller):
        global params
        seller.demand += 1
        winner.demand -= 1
        self.update_demand(winner)
        self.update_demand(seller)
        for ntype in ['seller', 'buyer']:
            if self.nnodes(ntype)-params.g_max<2:
               new_node = Node(params[ntype]) 
               self.add_star(new_node)  
        '''
        The sellers can't add buyers to thier auction. If they
            do it causes instability.
        '''
        for buyer in self.buyers:
            if len(self.node_list('seller', buyer)) < 2:
                #print("RANOUTOFSELLERS", self.sellers)
                self.add_edge(buyer, random_choice(self.node_filter('seller')))
         
    def update_demand(self, node):
        global params
        if node in self:
            if node.demand == 0:
                Node.names.append(node.name)
                self.remove_node(node)
                new_node = Node(params[node.type]) 
                self.add_star(new_node)
                #print("ADDED NODE", new_node.name)

    def update(self):
        global params
        params = self.make_params()
        for ntype in ['buyer', 'seller']:
            cnt = self.nnodes(ntype)-params['n'+ntype+'s']
            if cnt > 2:
                #print("\n---------------------------------------------\nUPDATE", ntype)
                self.update_nodes(cnt, ntype)
            params.nnodes = self.nnodes()
        return params
  
    def update_nodes(self, cnt, ntype):
        global params
        for n in range(abs(cnt)):
            if cnt < 0:
                new_node = Node(params[ntype])
                self.add_star(new_node) 
            else:
                #print("CHOOSING FROM", self.node_filter(ntype), ntype)
                choice = random_choice(self.node_filter(ntype))
                #print("CHOICE", name(choice),'\n', choice,'\n-------------------\n')
                Node.names.append(name(choice))
                #print("ADDED", name(choice), "TO POOL")
                self.remove_node(choice)
                #print(self.nodes())
                #print(Node.names, "LEFT\n")
        params['n'+ntype+'s']=self.nnodes(ntype)

    def buyers(self):
        buyers = self._node.loc[ self._node.type == 'buyer'].T
        return [buyers[u] for u in buyers]
    def sellers(self):
        sellers = self._node.loc[ self._node.type == 'seller'].T
        return [sellers[v] for v in sellers]
    def nbuyers(self):
        return len(self.buyers)
    def nsellers(self):
        return len(self.sellers)
    def nnodes(self, ntype=None, v=None):
        return len([n for n in self.node_list(ntype, v)])

    def add_edge(self, u, v, ts=None):
        global params
        ts = round(time.time()-params.start_time,4)
        #print("TARGET",v,'\n---------------------------------\n')
        super().add_edge(u ,v,
                    source=u.name,
                    target=v.name,
                    capacity=u.price, 
                    ts=pd.to_timedelta(ts, unit='ms')
                    )

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
            print(colored(seller.name, 'magenta'), end=' ') 
            for buyer in self.node_filter('buyer', seller).T:
                print(colored(buyer, 'green'), end=' ')
            print('')
        return
 
# randomly sample from a list <-- should go in the class
def rsample(x, maxn):
    #print("IN RSAMPLE", x.index)
    if len(x) < 2:
        raise ValueError(f"sample set smaller than min set size")
    if maxn < len(x):
        u = random.sample(
                        [n for n in list(x.index)],
                        random.randint(2,maxn)
                        )
    else:
        rsample(x, len(x)-1)
    try:
        #print("SAMPLE SET", u)
        return [x.loc[z] for z in u]
    except: 
        raise(KeyError,ValueError)
        return

def random_choice(x):
    print("IN CHOICE", x.index)
    n = random.sample(list(x.index),1)
    return x.loc[n[0]]
