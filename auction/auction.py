import numpy as np
import networkx as nx
from nx import nxNode
import random
from termcolor import colored
import seaborn as sns

from models import Node

#rocket = sns.color_palette('rocket')
#mako = sns.color_palette('mako')
#cool = sns.color_palette('cool')


class Auction(nx.Graph):

    def make_graph(self):
        global params, rng
        rng = nx.utils.create_random_state()
        params = self.make_params()
        self.start_time = params['start_time']

        for node in range(params['nsellers']):
            new_node = Node(params['seller'])
            self.add_node(new_node)
        for node in range(params['nbuyers']):
            new_node = Node(params['buyer'])
            self.add_star(new_node)
        
        pos = nx.spectral_layout(self, dim=3)
        for node in self.node_list():
            node.pos = pos[node] 
        self.print_auction()
     

    def node_view(self, node_filter=None, other_node=None):
        if other_node != None:
            g = nx.ego_graph(
                        self, 
                        other_node, 
                        1, # number of hops
                        False # include center node
                        )
            if node_filter:
                g = nx.subgraph_view(g, filter_node=node_filter)
        elif node_filter:
            g = nx.subgraph_view(self, filter_node=node_filter)
        else:
            g = self
        return g      

    def node_list(self, node_filter=None, other_node=None):
        return list(
                    self.node_view(
                                node_filter, 
                                other_node
                                  ).nodes
                    )

    def add_star(self, node, other_node=None):
        neighbors = rsample(
                        self.node_list(
                                inv_type_filter(node.type)
                                ),
                                params['g_max']
                        )
        if other_node:
            neighbors.append(other_node)
        nx.add_star(self, [node] + neighbors)
        for v in list(neighbors):
            self.add_edge(node, v)

    '''
    def add_node(self, node):
        super().add_node(node,
                price=node.price,
                value=node.private_value, 
                color=node.color, 
                demand=node.demand,
                pos=node.pos,
                type=node.type
                )

    def add_edge(self, source, target, ts=None):
        super().add_edge(
                    source,
                    target,
                    capacity = source.price,
                    weight = source.demand,
                    ts=ts
                    )
    '''
    def update_auction(self, winner, seller):
        global params
        seller.demand += 1
        winner.demand -= 1
        self.update_demand(winner)
        self.update_demand(seller)
        for ntype in ['seller', 'buyer']:
            if self.nnodes(type_filter(ntype))-params['g_max']<2:
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
            cnt = self.nnodes(type_filter(ntype))-params['n'+ntype+'s']
            if cnt > 2:
                self.update_nodes(cnt, ntype)
            params['nnodes'] = self.nbuyers()+self.nsellers()
        return params
  
    def update_nodes(self, cnt, ntype):
        global params
        for n in range(abs(cnt)):
            if cnt < 0:
                new_node = Node(params[ntype])
                self.add_star(new_node) 
            else:
                choice = random.choice(
                                self.node_list(
                                        type_filter(ntype)
                                            )
                                    )
                Node.ids.append(choice.id)
                self.remove_node(choice)
        params['n'+ntype+'s']=self.nnodes(type_filter(ntype))
    
    def nnodes(self, node_filter=None):
        return len(self.node_list(node_filter))

    def seller_list(self, node=None):
        return self.node_list(seller_filter, node)

    def buyer_list(self, node=None):
        return self.node_list(buyer_filter, node)

    def nbuyers(self):
        return len(self.buyer_list())

    def nsellers(self):
        return len(self.seller_list())

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

def buyer_filter(node):
    return node.type == 'buyer'

def seller_filter(node):
    return node.type == 'seller'

def type_filter(ntype):
    if ntype == 'seller':
        return seller_filter
    else:
        return buyer_filter

def inv_type_filter(ntype):
    if ntype == 'seller':
        return buyer_filter
    else:
        return seller_filter
