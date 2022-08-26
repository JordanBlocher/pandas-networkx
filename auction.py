from params import * 
import numpy as np
import networkx as nx
from node import Buyer, Seller, Node
import matplotlib

from termcolor import colored
import time

class Auction:

    G = nx.DiGraph()

    def __init__(self): 
        nodes = [Seller() for n in range(MSELLERS)] + [Buyer() for n in range(NBUYERS)]
        for node in nodes:
            self.G.add_node(node, value=node.private_value, type=node.type, color=node.color, demand=node.demand)
        self.nbuyers = NBUYERS
        self.msellers = MSELLERS   
         
        for buyer in self.buyer_list():
            rand = RANDOM(self.seller_list())
            #nx.add_path(self.G, rand)
            for seller in rand:
                self.G.add_edge(buyer, seller, weight = buyer.price)
        for edge in self.G.edges(data=True):
            if WEIGHTED_EDGES:
                self.G.add_edge(edge[1], edge[0], weight=edge[1].price)
            else:
                self.G.add_edge(edge[1], edge[0], weight=0)
        print("INITIAL EDGES", self.G.edges(data=True), '\n\n')
        print("INITIAL NODES", self.G.nodes(data=True), '\n\n')

    def seller_view(self, buyer=None):
        if buyer:
            g = nx.ego_graph(self.G, buyer, 1, False)
            return nx.subgraph_view(g,filter_node=self.seller_filter)
        else:
            g = nx.subgraph_view(self.G,filter_node=self.seller_filter)
        if len(g.nodes) < 2:
            self.add_seller(buyer)
        return g

    def buyer_view(self, seller=None):
        if seller:
            g = nx.ego_graph(self.G, seller, 1, False)
            return nx.subgraph_view(g,filter_node=self.buyer_filter)
        else:
            g = nx.subgraph_view(self.G,filter_node=self.buyer_filter)
        if len(g.nodes) < 2:
            self.add_buyer(seller)
        return g
 
    def node_view(self, node_filter=None, other_node=None):
        if other_node:
            g = nx.ego_graph(self.G, other_node, 1, False)
            return nx.subgraph_view(g,filter_node=node_filter)
        elif node_filter:
            g = nx.subgraph_view(self.G,filter_node=node_filter)
        else:
            g = self.G
        return g      

    def node_list(self, node_filter=None, other_node=None):
        return list(self.node_view(node_filter, other_node).nodes)

    def buyer_list(self, seller=None):
        return list(self.buyer_view(seller).nodes)

    def seller_list(self, buyer=None):
        return list(self.seller_view(buyer).nodes)

    def add_buyer(self, seller=None):
        buyer = Buyer()
        sellers = RANDOM(self.seller_list())
        if seller:
            sellers.append(seller)
        g = nx.star_graph([buyer] + sellers)
        if WEIGHTED_EDGES:
            for edge in g.edges(data=True):
                edge[2]['weight'] = buyer.price
        self.G = nx.compose(self.G,g) 
        for seller in sellers:
            if WEIGHTED_EDGES:
                self.G.add_edge(seller, buyer, weight=seller.price)
            else:
                self.G.add_edge(seller, buyer, weight=0)
        self.G.nodes(data=True)[buyer]['value'] = buyer.private_value
        self.G.nodes(data=True)[buyer]['type'] = buyer.type 
        self.G.nodes(data=True)[buyer]['color'] = buyer.color 
        self.nbuyers += 1

    def add_seller(self, buyer=None):
        seller = Seller()
        buyers =  RANDOM(self.buyer_list())
        if buyer:
            buyers.append(buyer)
        g = nx.star_graph([seller] + buyers)
        for edge in g.edges(data=True):
            if WEIGHTED_EDGES:
                edge[2]['weight'] = seller.price
            else:
                edge[2]['weight'] = 0
        self.G.add_node(seller, value=seller.private_value, \
                        type=seller.type, color=seller.color, demand=seller.demand)
        self.G = nx.compose(self.G,g) 
        for buyer in buyers:
            self.G.add_edge(buyer, seller, weight=buyer.price)
        if PRIVATE_VALUE:
            self.G.add_edge(seller, seller, weight=seller.private_value)
        self.msellers += 1

    def add_node(self, node, other_node=None):
        neighbors =  RANDOM(self.node_list(self.filter_type(node)))
        if other_node:
            neighbors.append(other_node)
        g = nx.star_graph([node] + neighbors)
        for edge in g.edges(data=True):
            edge[2]['weight'] = node.price
        self.G.add_node(node, value=node.private_value, \
                        type=node.type, color=node.color, demand=node.demand)
        for neighbor in neighbors:
            self.G.add_edge(neighbor, node, weight=neighbor.price)
        self.nnodes += 1

    def update_auction(self, seller, winner):
        self.G.nodes(data=True)[winner]['color'] = 'green'
        winner.color = 'green'
        if winner.demand >= 0:
            print("WINNER", winner, "GONE")
            self.G.remove_node(winner)
            self.nbuyers -= 1
            Node.ids.append(winner.id)
        if seller.demand <= 0:
            self.G.remove_node(seller)
            self.msellers -= 1
            Node.ids.append(seller.id)
        if self.nbuyers < NBUYERS:
            self.add_buyer()
        if self.msellers < MSELLERS:
            self.add_seller()
    
    def print_auction(self):
        for seller in self.seller_view():
            print("AUCTION", end=' ')
            cprintnode(seller, '\t')
            for buyer in self.buyer_view(seller):
                cprintnode(buyer, ' ')
            print('')
        print('')
    
    def print_view(self, node, node_filter):
        cprintnode(node, '\t')
        for neighbor in self.view(node, node_filter):
            cprintnode(neighbor, ' ')
        print('')
 
    def seller_filter(self, node):
        return self.G.nodes(data=True)[node]['type'] == 'seller'

    def buyer_filter(self, node):
        return self.G.nodes(data=True)[node]['type'] == 'buyer'

    def filter_type(self, node):
        if self.G.nodes(data=True)[node]['type'] == 'buyer':
            return self.buyer_filter
        else:
            return self.seller_filter
        
 
