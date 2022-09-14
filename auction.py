import numpy as np
import networkx as nx
from node import Node
import random

from termcolor import colored
import seaborn as sns

#rocket = sns.color_palette('rocket')
#mako = sns.color_palette('mako')
#cool = sns.color_palette('cool')


class Auction(nx.Graph):

    def make_graph(self):
        global params, rng
        rng = nx.utils.create_random_state()
        params = self.make_params()
        self.start_time = params['start_time']
        self.update_params('buyer')        
        self.update_params('seller')        

        for ntype in ['buyer', 'seller']:
            for node in range(params['n'+ntype+'s']):
                new_node = Node()
                new_node.build(params[ntype])
                self.add_node(new_node)
        for node in self.node_list(buyer_filter):
            rand = rsample(  
                           self.node_list(seller_filter),
                           params['g_max']
                           )
            for other_node in rand:
                self.add_edge((node,other_node))
        pos = nx.spectral_layout(self, dim=3)
        for node in self.node_list():
            node.pos = pos[node] 
     

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

    def compose_node(self, node, other_node=None):
        neighbors = rsample(
                        self.node_list(
                                inv_type_filter(node.type)
                                ),
                                params['g_max']
                        )
        if other_node:
            neighbors.append(other_node)
        g = nx.star_graph([node] + neighbors)
        self.add_node(node)
        self = nx.compose(self,g) 
        for neighbor in neighbors:
            self.put_edge((node,neighbor))

    def add_node(self, node):
        super().add_node( node,
                price=node.price,
                value=node.private_value, 
                color=node.color, 
                demand=node.demand,
                pos=node.pos,
                type=node.type
                )

    def add_edge(self, edge):
        super().add_edge(
                    edge[0], 
                    edge[1], 
                    weight = edge[0].price,
                    weight1= edge[1].price,
                    )

    def update_auction(self, winner, seller):
        seller.demand -= 1
        winner.demand += 1
        self.update_demand(winner)
        self.update_demand(seller)
        '''
        The sellers can't add buyers to thier auction. If they
            do it causes instability.
        '''
        for buyer in self.buyer_list():
            if len(self.seller_list(buyer)) < 2:
                self.put_edge(buyer, rng.choice(self.seller_list()))
    
    def update_demand(self, node):
        global params
        if node in self.nodes:
            if node.demand == 0:
                Node.ids.append(node.id)
                self.remove_node(node)
                new_node = Node()
                new_node.build(params[node.type]) 
                self.compose_node(new_node)

    def update(self):
        global params
        params = self.make_params()
        for ntype in ['buyer', 'seller']:
            if params['n'+ntype+'s']-self.nnodes(type_filter(ntype)) > 2:
                self.update_params(ntype)
                self.update_nodes(ntype)
        return params

    def update_params(self, ntype):
        global params
        price = rng.poisson(
                        params[ntype]['max_price'], 
                        size=params['nnodes']+10
                        )
        params[ntype]['price'] = price
        self.inc_factor = rng.uniform(
                                params[ntype]['inc'][0], 
                                params[ntype]['inc'][1], 
                                size=params['nnodes']+5
                                ),
        self.dec_factor = rng.uniform(
                                params[ntype]['dec'][0], 
                                params[ntype]['dec'][1], 
                                size=params['nnodes']+5
                                ),
        params[ntype]['inc_factor'] = self.inc_factor
        params[ntype]['dec_factor'] = self.dec_factor

      
    def update_nodes(self, ntype):
        global params
        node_filter=type_filter(ntype)
        cnt = self.nnodes(node_filter) - params['n'+ntype+'s'] - 1
        for n in range(abs(cnt)):
            if cnt < 0:
                new_node = Node()
                new_node.build(params[ntype])
                self.compose_node(new_node) 
            else:
                choice = rng.choice(self.node_list(node_filter))
                Node.ids.append(choice.id)
                self.remove_node(choice)
    
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



    def print_auction(self):
        for seller in self.seller_list():
            print(colored(seller, 'magenta'), end=' ') 
        for buyer in self.buyer_list():
            print(colored(buyer, 'green'), end=' ')
        print('')
        for seller in self.seller_list():
            print(colored(seller, 'magenta'), end=' ') 
            for buyer in self.buyer_list(seller):
                print(colored(buyer, 'green'), end=' ')
            print('')
        return
 
        for seller in self.seller_list():
            print(
                colored(seller, 'magenta'), 
                colored('%3s' % seller.demand, 'yellow'),
                colored('%3s' % seller.price, 'blue'),
                colored('%3s' % seller.private_value, 'cyan'),
                end=' '
                )
            for buyer in self.buyer_list(seller):
                print(
                    colored(buyer, 'green'), 
                    colored('%3s' % buyer.demand, 'yellow'),
                    colored('%3s' % buyer.price, 'blue'),
                    colored('%3s' % buyer.private_value, 'cyan'),
                    end=' '
                    )
            print('\n')

# randomly sample from a list 
def rsample(x, n):
    u = random.sample(
                    [n for n in range(len(x))],
                    random.randint(2,n)
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
