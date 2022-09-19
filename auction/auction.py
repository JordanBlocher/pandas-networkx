import numpy as np
import networkx as nx
import random
from termcolor import colored
import seaborn as sns

from models import Node
from nxn import nxNode, name, spectral_layout


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
            print(new_node)
            self.add_node(new_node)
        print(self)
        for node in range(params.nbuyers):
            new_node = Node(params.buyer)
            print(new_node)
            self.add_star(new_node)
        
        #self.print_auction()
        #pos = spectral_layout(self, dim=3)
        #for node in self.nodes():
         #   node.pos = pos[node] 

        self.buyers = self.buyers()
        self.nbuyers = self.nbuyers()
        self.sellers = self.sellers()
        self.nsellers = self.nsellers()
     

    def node_filter(self, ntype=None, v=None):
        try:
            nbrs = self[v]
        except KeyError:
            return
        print(nbrs)
        #g = self.subgraph_view(ntype, v)
        #return nxNode.nodes(g)

    def add_star(self, node, v=None):
        nbrs = rsample(
                        self.node_filter(~node, v),
                        params.g_max
                        )
        if v:
            nbrs.append(v)
        star_nodes = [node]+nbrs
        nxNode.add_star(self, star_nodes)

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
        for buyer in self.buyers():
            if len(self.node_filter(buyer)) < 2:
                self.add_edge(buyer, random.choice(self.sellers))
         
    def update_demand(self, node):
        global params
        if node in self.nodes:
            if node.demand == 0:
                Node.names.append(node.name)
                self.remove_node(node)
                new_node = Node(params[node.type]) 
                self.add_star(new_node)

    def update(self):
        global params
        print(self.nnodes())
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
                self.add_star(new_node) 
            else:
                choice = random.choice(self.node_filter(ntype))
                self.remove_node(choice)
        params['n'+ntype+'s']=self.nnodes(ntype)

    def buyers(self):
        return self._node.loc[ self._node.type == 'seller']
    def sellers(self):
        return self._node.loc[ self._node.type == 'buyer']
    def nbuyers(self):
        return len(self.buyers)
    def nsellers(self):
        return len(self.sellers)

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
            for buyer in self.node_view('seller', seller):
                print(colored(buyer, 'green'), end=' ')
            print('')
        return
 
# randomly sample from a list 
def rsample(x, maxn):
    u = random.sample(
                    [n for n in range(1,len(x)+1)],
                    random.randint(2,maxn)
                    )
    return [x[z] for z in u]

