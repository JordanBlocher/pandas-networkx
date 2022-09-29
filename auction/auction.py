import numpy as np
import networkx as nx
import random
from termcolor import colored
import seaborn as sns
np.set_printoptions(precision=2)

from models import Node
from nxn import nxNode, spectral_layout, name
import pandas as pd
import time
import sys
from collections import namedtuple

    
'''
The auction holds all the live data, buyers and sellers
and passes a dataframe up to the auctioneer every time a 
players price changes. The memory in the auction is flash, 
and is updated the next time a player challenges the price.
'''


class Auction(nxNode):
    name: str = 'auction'
    index = ['name']
    layout = None

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

        self.layout = {}
        layout = spectral_layout(self, dim=3)
        for node in layout:
            pos = np.array(layout[node]).round(2) 
            #pos = np.clip(pos, 0, params.clamp)
            self.layout[node.name] = pos
            node.pos_x = pos[0]
            node.pos_y = pos[1]
            node.pos_z = pos[2]
    
        self._node = self._node.astype({'name':np.int, 'value':np.float, 'demand':np.int, 'price':np.float, 'pos_x':np.float, 'pos_y':np.float, 'pos_z':np.float})

        for seller in self.sellers():
            self.print_auction(seller)

    def node_list(self, ntype=None, v=None):
        nodes = self.node_filter(ntype, v)
        return iter(nodes.index)

    def node_filter(self, ntype=None, v=None): #TODO: generalize filter
        #print("IN FILTER", ntype, '\n------------------------------\n')
        idx=pd.IndexSlice
        nbrs = pd.DataFrame()
        if v is not None and v in self._node.index:
            #print("using node", v, '\n------------------------------\n')
            for u,w in self[v].index:
                if name(u) == name(v):
                    nbrs = nbrs.append(self._node.loc[self._node.name == name(w)]) 
                elif name(w) == name(v):
                    nbrs = nbrs.append(self._node.loc[self._node.name == name(u)]) 
            #print("\nNBRS1", list(nbrs.index))
            if ntype is not None and v in self and not nbrs.empty:
                nbrs = nbrs.loc[ nbrs['type'] == ntype ]
                #print("\nNBRSTYPE2", list(nbrs.index))
            #print("\n---------------------------------\n")
        elif ntype is not None:
            nbrs = self._node.loc[ self._node['type'] == ntype ]
        else:
            nbrs = self._node.loc[:]
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

    def update(self):
        global params
        params = self.make_params()
        return params
  
    def update_auction(self, winner, seller):
        global params
        flag = False
        winner.type='buyer'
        flag = self.update_demand(winner)
        winner.type='winner'
        flag = self.update_demand(seller)
        while not flag:
            time.sleep(.1)
        for ntype in ['seller', 'buyer']:
            if self.nnodes(ntype)-params.g_max<2:
               new_node = Node(params[ntype]) 
               self.add_star(new_node)  
        '''
        The sellers can't add buyers to thier auction. If they
            do it causes instability.
        '''
        for buyer in self.buyers():
            if self.nnodes('seller', buyer) < 2:
                #print("RANOUTOFSELLERS", self.sellers)
                sellers = self.node_filter('seller')
                self.add_edge(buyer, random_choice(sellers))
         
    def update_demand(self, node):
        global params
        node.demand += 1*(-node.demand/abs(node.demand)) 
        if node.demand == 0:
            new_node = Node(params[node.type]) 
            Node.names.append(node.name)
            self.df_r.append(node.graph)
            self.remove_node(node)
            #print("REMOVED", node.type, "NODE", node.name)
            self.add_star(new_node)
            #print("ADDED", new_node.type, "NODE", new_node.name)
        return True

    def buyers(self):
        buyers = self._node.loc[ self._node.type == 'buyer']
        return list(buyers.index)
    def sellers(self):
        sellers = self._node.loc[ self._node.type == 'seller']
        return list(sellers.index)
    def nbuyers(self):
        return len(self.buyers())
    def nsellers(self):
        return len(self.sellers())
    def nnodes(self, ntype=None, v=None):
        return len(list(self.node_list(ntype, v)))

    def add_edge(self, u, v, ts=None):
        global params
        ts = round(time.time()-params.start_time,4)
        super().add_edge(u ,v,
                    source=u.name,
                    target=v.name,
                    capacity=u.price, 
                    demand=u.demand,
                    ts=pd.to_timedelta(ts, unit='ms')
                    )

    def print_auction(self, seller, data=False):
        global params
        ts = round(time.time()-params.start_time,4)
        ts = pd.to_timedelta(ts, unit='ms')
        print(ts)
        if data:
            print(colored(seller, 'magenta'), end=' ') 
            print('')
            for buyer in self.node_list('buyer', seller):
                if buyer.winner:
                    print(colored(buyer, 'green'), end=' ')
                else:
                    print(colored(buyer, 'yellow'), end=' ')
                print('')
            print('')
        else:
            print(colored(seller.name, 'magenta'), end=' ') 
            for buyer in self.node_list('buyer', seller):
                if buyer.winner:
                    print(colored(buyer.name, 'green'), end=' ')
                else:
                    print(colored(buyer.name, 'yellow'), end=' ')
            print('')
        sys.stdout.flush()
        sys.stderr.flush()
 
    def __str__(self):
        return f"{self.name}"



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
        return u
    except: 
        raise(KeyError,ValueError)
        return

def random_choice(x):
    #print("IN CHOICE", x.index)
    n = random.sample(list(x.index),1)
    return n[0]
