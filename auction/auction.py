import numpy as np
import networkx as nx
from nx import nxNode
import random
from termcolor import colored
import seaborn as sns

from models import Node
from nx import nxNode, id


class Auction(nxNode):

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
        
        pos = nx.spectral_layout(self, dim=3)
        for node in self.nodes():
            node.pos = pos[node] 
        self.print_auction()
     

    def nodes(self, ntype=None, v=None):
        return self.subgraph_view(ntype, v)

    def buyers(self, v=None):
        return self.nodes('buyer', v)
 
    def sellers(self, v=None):
        return self.nodes('seller', v)
               
    def add_star(self, node, v=None):
        nbrs = rsample(
                        self.nodes(~node, v),
                        params.g_max
                        )
        if v:
            nbrs.append(v)
        super().add_star(self, [node] + nbrs)
        for w in list(nbrs):
            self.add_edge(node, w)

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
        for buyer in self.buyer_list():
            if len(self.seller_list(buyer)) < 2:
                self.add_edge(buyer, random.choice(self.seller_list()))
         
    def update_demand(self, node):
        global params
        if node in self.nodes:
            if node.demand == 0:
                Node.ids.append(node.id)
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
                choice = random.choice(self.nodes(ntype))
                self.remove_node(choice)
        params['n'+ntype+'s']=self.nnodes(ntype)
    
    def nnodes(self, ntype=None, v=None):
        return len(self.nodes(ntype, v))

    def nbuyers(self, v=None):
        return self.nnodes('buyer', v)

    def nsellers(self):
        return self.nnodes('seller', v)

    def print_auction(self, data=False):
        if data:
            for seller in self.seller_list():
                print(colored(seller, 'magenta'), end=' ') 
            print('')
            for buyer in self.buyer_list():
                print(colored(buyer, 'green'), end=' ')
            print('')
        print(colored(self.nbuyers(), 'green'), end=' ')
        print(colored(self.nsellers(), 'magenta')) 
        for seller in self.seller_list():
            print(colored(seller.id, 'magenta'), end=' ') 
            for buyer in self.buyer_list(seller):
                print(colored(buyer.id, 'green'), end=' ')
            print('')
        return
 
# randomly sample from a list 
def rsample(x, maxn):
    u = random.sample(
                    [n for n in range(len(x))],
                    random.randint(2,maxn)
                    )
    return [x[z] for z in u]

