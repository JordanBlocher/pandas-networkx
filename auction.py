import numpy as np
import networkx as nx
from node import Node
import random

from termcolor import colored
import seaborn as sns

class Auction:

    G = nx.Graph()
    pos = None

    def __init__(self, make_params, start_time): 
        global params, rng
        rng = nx.utils.create_random_state()
        params = make_params()
        self.make_params = make_params
        self.start_time = start_time

        nodes = [Node(params['seller']) for n in range(params['nsellers'])] + \
                [Node(params['buyer']) for n in range(params['nbuyers'])]
        for node in nodes:
            node.price *= rng.choice(params['price'])
            self.G.add_node(
                            node, 
                            value=node.private_value, 
                            color=node.color, 
                            demand=node.demand
                            )
        for node in self.node_list(self.buyer_filter):
            max_sample = min(
                            len(self.node_list(self.seller_filter)),
                            params['g_max']
                            )
            rand = rsample(  
                            self.node_list(self.seller_filter),
                            max_sample
                            )
            for other_node in rand:
                self.G.add_edge(
                                node, 
                                other_node, 
                                weight = node.price
                                )

        self.pos = nx.spring_layout(self.G, dim=3, seed=779)
      

    def node_view(self, node_filter=None, other_node=None):
        if other_node:
            g = nx.ego_graph(
                        self.G, 
                        other_node, 
                        1, # number of hops
                        False # include center node
                        )
            if node_filter:
                g = nx.subgraph_view(g, filter_node=node_filter)
        elif node_filter:
            g = nx.subgraph_view(self.G, filter_node=node_filter)
        else:
            g = self.G
        return g      

    def node_list(self, node_filter=None, other_node=None):
        return list(
                    self.node_view(
                                node_filter, 
                                other_node
                                  ).nodes
                    )

    def add_node(self, node, other_node=None):
        max_sample = min(
                        len(self.node_list(node.inv_filter)),
                        params['g_max']
                        )
        print(self.node_list(node.inv_filter), max_sample)
        neighbors = rsample(
                            self.node_list(node.inv_filter),
                            max_sample
                            )
        if other_node:
            neighbors.append(other_node)
        g = nx.star_graph([node] + neighbors)
        self.G.add_node(
                        node, 
                        value=node.private_value, 
                        color=node.color, 
                        demand=node.demand
                        )
        self.G = nx.compose(self.G,g) 
        for neighbor in neighbors:
            self.G.add_edge(
                            node, 
                            neighbor, 
                            weight=node.price
                            )
        self.pos = nx.spring_layout(self.G, pos=self.pos, dim=3, seed=779)

    def update_auction(self, winner, seller):
        self.update_demand(winner)
        self.update_demand(seller)
        '''
        The sellers can't add buyers to thier auction. If they
            do it causes instability.
        '''
        for buyer in self.buyer_list():
            if len(self.seller_list(buyer)) < 2:
                self.G.add_edge(
                            buyer,
                            rng.choice(self.seller_list()),
                            weight=buyer.price 
                            )               
    
    def update_demand(self, node):
        if node in self.G:
            if node.demand == 0:
                Node.ids.append(node.id)
                self.G.remove_node(node)
                new_node = Node(params[node.type()])
                self.add_node(new_node) 

    def update_params(self, new_params):
        global params
        params = new_params
        seller = rng.choice(self.seller_list())
        buyer = rng.choice(self.seller_list())
        self.update_nodes(buyer)
        self.update_nodes(seller)
     
    def update_nodes(self, node):
        global params
        if 'net' in params.keys():
            node_filter=node.filter
            ntype=node.type()
            while self.nnodes(node_filter) < params['n'+ntype+'s']:
                new_node = Node(params[ntype])
                self.add_node(new_node) 
                raise("ADDED")
            while self.nnodes(node_filter) > params['n'+ntype+'s']:
                choice = rng.choice(self.node_list(node_filter))
                Node.ids.append(choice.id)
                self.G.remove_node(choice)
                raise("LOST")

    
    def nnodes(self, node_filter=None):
        return len(self.node_list(node_filter))

    def seller_list(self, node=None):
        return self.node_list(self.seller_filter, node)

    def buyer_list(self, node=None):
        return self.node_list(self.buyer_filter, node)

    def nbuyers(self):
        return len(self.buyer_list())

    def nsellers(self):
        return len(self.seller_list())

    def buyer_filter(self, node):
        return node.type() == 'buyer'

    def seller_filter(self, node):
        return node.type() == 'seller'

    def print_auction(self):
        for seller in self.seller_list():
            print(colored('%4s' % seller, 'magenta'), '%2s' % seller.demand, end='\t')
            for buyer in self.buyer_list(seller):
                print(colored(buyer, 'green'), '%3s' % buyer.demand, end=' ')
            print(' ')

# randomly sample from a list 
def rsample(x, n):
    u = random.sample(
                    [n for n in range(len(x))],
                    random.randint(2,n)
                    )
    return [x[z] for z in u]
