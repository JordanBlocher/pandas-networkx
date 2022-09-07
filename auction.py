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
        for node in self.node_list(self.filter('buyer')):
            rand = rsample(  
                            self.node_list(
                                        self.filter('seller')
                                        ),
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
        self.pos = nx.spring_layout(self.G, fixed=pos, dim=3, seed=779)

    def update_nodes(self, new_params):
        global params
        params = new_params
        while self.nnodes(node.filter) <= params[node.type]['n']:
            self.add_node(
                        Node(node.color, node.type, params[node.type])
                        )
        while self.nnodes(node.filter) > params[node.type]['n']:
            self.G.remove_node(
                            random.choice(self.node_list(node.filter))
                              )
        if self.nnodes() % 40:
            self.get_colors()
                 
    def update_auction(self, node):
        if len(self.node_list(node.inv_filter, node)) < 2:
            self.G.add_edge(
                            node,
                            random.choice(self.node_list(node.inv_filter)),
                            weight=node.price 
                            )
        if node.demand == 0:
            self.G.remove_node(node)
            Node.ids.append(node.id)
            self.add_node(
                        Node(node.color, node.type, params[node.type])
                        )
    
    def nnodes(self, node_filter=None):
        return len(self.node_list(node_filter))

    def seller_list(self, node=None):
        return self.node_list(self.filter('seller'), node)

    def buyer_list(self, node=None):
        return self.node_list(self.filter('buyer'), node)

    def get_colors(self, node_filter=None):
        pass
        maxid = max([node.id for node in self.node_list(
                                                        node_filter
                                                        )
                    ])

        colors = np.array_split(
                            list(sns.palettes.xkcd_palette(
                                sns.colors.xkcd_rgb)
                                ), 
                                10 * maxid              
                             )
        for node in self.node_list(node_filter):
            node.color = colors[node.id]
 
    def filter(self, node, type):
        return node.type == type

    def print_auction(self):
        for seller in self.seller_list():
            cprintnode(seller, '\t')
            for buyer in self.buyer_list(seller):
                cprintnode(buyer, ' ')
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
