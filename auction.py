import numpy as np
import networkx as nx
from node import Buyer, Seller, Node
import random

from termcolor import colored
import seaborn as sns

class Auction:

    G = nx.Graph()
    pos = None

    def __init__(self, new_params): 
        global params
        params = new_params
        nodes = [Seller(params) for n in range(params['seller']['n'])] + \
                [Buyer(params) for n in range(params['buyer']['n'])]
        for node in nodes:
            self.G.add_node(
                            node, 
                            value=node.private_value, 
                            type=node.type, 
                            color=node.color, 
                            demand=node.demand
                            )
        for node in self.node_list(self.buyer_filter):
            rand = rsample(  
                            self.node_list(self.seller_filter),
                            params
                            )
            for other_node in rand:
                self.G.add_edge(
                                node, 
                                other_node, 
                                weight = node.price
                                )

        self.pos = nx.spring_layout(self.G, dim=3, seed=779)
        self.get_colors()
      

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
        pos = self.node_list()
        neighbors =  rsample(
                        self.node_list(node.inv_filter),
                        params
                        )
        if other_node:
            neighbors.append(other_node)
        g = nx.star_graph([node] + neighbors)
        self.G.add_node(
                        node, 
                        value=node.private_value, 
                        type=node.type, 
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
        self.pos = nx.spring_layout(self.G, dim=3, seed=779)

    def update_auction(self, buyer, seller, new_params):
        global params
        params = new_params
        self.update_nodes(buyer)
        self.update_nodes(seller)
                
    def update_nodes(self, node):
        while self.nnodes(node.filter) < params[node.type]['n']:
            self.add_node(
                        Node(node.color, node.type, params[node.type])
                        )
        while self.nnodes(node.filter) > params[node.type]['n']:
            self.G.remove_node(
                            random.choice(self.node_list(node.filter))
                              )
        for other_node in self.node_list(node.inv_filter, node): 
            if len(self.node_list(node.filter, other_node)) < 2:
                self.G.add_edge(
                                other_node,
                                random.choice(self.node_list(node.filter)),
                                weight=other_node.price 
                                )
        if node.demand == 0:
            self.G.remove_node(node)
            Node.reids.append(node.id)
            self.add_node(
                        Node(node.color, node.type, params[node.type])
                        ) 
 
        if self.nnodes() % 40:
            self.get_colors()

    
    def nnodes(self, node_filter=None):
        return len(self.node_list(node_filter))

    def seller_list(self, node=None):
        return self.node_list(self.seller_filter, node)

    def buyer_list(self, node=None):
        return self.node_list(self.buyer_filter, node)

    def get_colors(self, node_filter=None):
        maxid = max([node.id for node in self.node_list(
                                                    node_filter
                                                    )
                    ])

        self.colors = np.array_split(
                                list(sns.colors.xkcd_rgb),
                                10 * maxid              
                                )
        for node in self.node_list(node_filter):
            print(self.colors[node.id])
            node.color = self.colors[node.id][0]
 
    def buyer_filter(self, node):
        return node.type == 'buyer'

    def seller_filter(self, node):
        return node.type == 'seller'

    def print_auction(self):
        for seller in self.seller_list():
            print(colored(seller, 'magenta'), seller.price, seller.demand, end='\t')
            for buyer in self.buyer_list(seller):
                print(colored(buyer, 'green'), buyer.price, buyer.demand, end=' ')

            print('')
        print('')

    
# randomly sample from a list 
def rsample(x, params):
    u = random.sample(
                    [n for n in range(len(x))],
                    random.randint(
                                params['mingroupsize'],
                                params['maxgroupsize']
                                )
                    )
    return [x[z] for z in u]
