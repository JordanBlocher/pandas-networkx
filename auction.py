from params import * 
import numpy as np
import networkx as nx
from node import Buyer, Seller, Node
import matplotlib

from termcolor import colored
import time

class Auction:

    G = nx.Graph()
    node_xyz = []

    def __init__(self): 
        nodes = [Seller() for n in range(MSELLERS)] + [Buyer() for n in range(NBUYERS)]
        for node in nodes:
            self.G.add_node(node, value=node.private_value, type=node.type, color=node.color, demand=node.demand)
        self.nnodes = NBUYERS+MSELLERS
         
        for buyer in self.buyer_list():
            rand = RANDOM(self.seller_list())
            #nx.add_path(self.G, rand)
            for seller in rand:
                self.G.add_edge(buyer, seller, weight = buyer.price)
                #self.G.add_edge(seller, buyer, weight = seller.price)
        #print("INITIAL EDGES", self.G.edges(data=True), '\n\n')
        #print("INITIAL NODES", self.G.nodes(data=True), '\n\n')
        #d = nx.to_dict_of_lists(self.G)
        #for key, value in d.items():
        #    print(key, value)

    def node_view(self, node_filter=None, other_node=None):
        if other_node:
            g = nx.ego_graph(self.G, other_node, 1, False)
            if node_filter:
                g = nx.subgraph_view(g,filter_node=node_filter)
        elif node_filter:
            g = nx.subgraph_view(self.G,filter_node=node_filter)
        else:
            g = self.G
        return g      

    def seller_list(self, node=None):
        return self.node_list(self.seller_filter, node)

    def winner_list(self, node=None):
        return self.node_list(self.winner_filter, node)

    def buyer_list(self, node=None):
        return self.node_list(self.buyer_filter, node)

    def node_list(self, node_filter=None, other_node=None):
        return list(self.node_view(node_filter, other_node).nodes)

    def add_node(self, node, other_node=None):
        if node.type == 'buyer':
            node_filter = self.seller_filter
        else:
            node_filter = self.buyer_filter
        neighbors =  RANDOM(self.node_list(node_filter))
        if other_node:
            neighbors.append(other_node)
        g = nx.star_graph([node] + neighbors)
        self.G.add_node(node, value=node.private_value, type=node.type, color=node.color, demand=node.demand)
        self.G = nx.compose(self.G,g) 
        for neighbor in neighbors:
            if node.type == 'buyer':
                self.G.add_edge(node, neighbor, weight=node.price)
                #self.G.add_edge(neighbor, node, weight=neighbor.price)
            else:
                self.G.add_edge(neighbor, node, weight=neighbor.price)
                #self.G.add_edge(node, neighbor, weight=node.price)
        self.nnodes += 1

    def update_auction(self, seller, winner):
        for buyer in self.buyer_list(seller):
            if len(self.seller_list(buyer)) < 2:
                choice = random.choice(self.seller_list())
                self.G.add_edge(buyer, choice, weight=buyer.price)
        if seller.demand <= 0:
            self.G.remove_node(seller)
            self.nnodes -= 1
            Node.ids.append(seller.id)
            self.add_node(Seller())
        self.G.nodes(data=True)[winner]['color'] = 'green'
        winner.color = 'green'
        if winner.demand >= 0:
            self.G.remove_node(winner)
            self.nnodes -= 1
            Node.ids.append(winner.id)
            self.add_node(Buyer())
    
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

    def winner_filter(self, node):
        return node.color == 'red'

 
