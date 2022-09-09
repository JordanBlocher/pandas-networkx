import numpy as np
import networkx as nx
from node import Buyer, Seller, Node
import random

from termcolor import colored

class Auction:

    G = nx.Graph()
    pos = None

    def __init__(self, new_params): 
        global params
        params = new_params
        nodes = [Seller(params) for n in range(params['seller']['m'])] + \
                [Buyer(params) for n in range(params['buyer']['n'])]
        for node in nodes:
            self.G.add_node(
                            node, 
                            value=node.private_value, 
                            type=node.type, 
                            color=node.color, 
                            demand=node.demand
                            )
        self.nnodes = params['buyer']['n']+params['seller']['m']         

        for buyer in self.buyer_list():
            rand = rsample(  
                            self.seller_list(),
                            params
                            )
            for seller in rand:
                self.G.add_edge(
                                buyer, 
                                seller, 
                                weight = buyer.price
                                )

        self.pos = nx.spring_layout(self.G, dim=3, seed=779)
        self.npos = np.array([self.pos[v] for v in nodes]),
        self.epos = np.array([(
                                self.pos[u], self.pos[v]
                                ) for u, v in self.G.edges()
                            ])
  

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
        if node.type == 'buyer':
            node_filter = self.seller_filter
        else:
            node_filter = self.buyer_filter
        neighbors =  rsample(
                                self.node_list(node_filter),
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
            if node.type == 'buyer':
                weight = node.price
            else:
                weight = neighbor.price
            self.G.add_edge(
                            node, 
                            neighbor, 
                            weight=weight
                            )
        self.nnodes += 1
        self.pos = nx.spring_layout(self.G, dim=3, seed=779)
        self.npos = np.array([self.pos[v] for v in nodes]),
        self.epos = np.array([(
                                self.pos[u], self.pos[v]
                                ) for u, v in self.G.edges()
                            ])
                           

    def update_nodes(self):
        global params
        params = self.make_params()
        while self.nbuyers() < params['buyer']['n']:
            self.add_node(
                        Buyer(params)
                        )
        while self.msellers() < params['seller']['m']:
            self.add_node(
                        Seller(params)
                        )
        while self.nbuyers() > params['buyer']['n']:
            self.G.remove_node(
                            random.choice(self.buyer_list())
                              )
            self.nnodes -= 1
        while self.msellers() >  params['seller']['m']:
            self.G.remove_node(
                            random.choice(self.seller_list())
                            )
            self.nnodes -= 1
        if self.nnodes % 40:
            self.get_colors()
         
    def update_auction(self, seller, winner):
        for buyer in self.buyer_list(seller):
            if len(self.seller_list(buyer)) < 2:
                self.G.add_edge(
                                buyer, 
                                random.choice(self.seller_list()),
                                weight=buyer.price
                                )
        if seller.demand <= 0:
            self.G.remove_node(seller)
            self.nnodes -= 1
            Node.ids.append(seller.id)
            self.add_node(
                        Seller(params)
                        )
        if winner.demand >= 0:
            self.G.remove_node(winner)
            self.nnodes -= 1
            Node.ids.append(winner.id)
            self.add_node(
                        Buyer(params)
                        )
    
    def print_auction(self):
        for seller in self.seller_list():
            cprintnode(seller, '\t')
            for buyer in self.buyer_list(seller):
                cprintnode(buyer, ' ')
            print('')
        print('')
    
    def print_view(self, node, node_filter):
        cprintnode(node, '\t')
        for neighbor in self.view(node, node_filter):
            cprintnode(neighbor, ' ')
        print('')
 
    def seller_filter(self, node):
        return node.type == 'seller'
        return self.G.nodes(data=True)[node]['type'] == 'seller'

    def buyer_filter(self, node):
        return node.type == 'buyer'
        return self.G.nodes(data=True)[node]['type'] == 'buyer'

    def nbuyers(self):
        return len(self.buyer_list())

    def msellers(self):
        return len(self.seller_list())

    def seller_list(self, node=None):
        return self.node_list(self.seller_filter, node)

    def buyer_list(self, node=None):
        return self.node_list(self.buyer_filter, node)

    def get_colors(self):
        pass
    '''
        self.seller_colors = np.array_split(
                                list(sns.palettes.xkcd_palette(
                                    sns.colors.xkcd_rgb)
                                    ), 
                                10*max([node.id for node in self.seller_list()])
                                )
       self.buyer_colors = np.array_split(
                                list(sns.palettes.xkcd_palette(
                                    sns.colors.xkcd_rgb)
                                    ), 
                                10*max([node.id for node in self.buyer_list()])
                                )
        for node in self.seller_list():
            node.color = self.seller_colors[node.id]
        for node in self.buyer_list():
            node.color = self.buyer_colors[node.id]
    '''
 

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
