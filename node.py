import random
import numpy as np
np.set_printoptions(precision=2)

    
MAX_NETWORK_SIZE = 200


def Buyer(params):
    return Node('green', 'buyer', params['buyer'])

def Seller(params):
    return Node('magenta', 'seller', params['seller'])

class Node:
    
    ids = [n for n in reversed(range(1, MAX_NETWORK_SIZE))]
    #factor = np.random.uniform(0.09, 0.99, size=200)
    id = 0

    def __init__(self, color, type, params):
        self.id = Node.ids.pop()
        self.demand = int(
                        np.random.uniform(1, params['max_quantity'])
                         ) * params['flow']
        self.private_value = round(np.random.uniform(1, params['max_price']),2)
        self.color = color
        self.type = type
        self.price = round(self.private_value*params['factor'],2)

    def __repr__(self):
        return str(self.id)

    def filter(self, node):
        return node.type  == self.type
        #return self.G.nodes(data=True)[node]['type'] == 'seller'

    def inv_filter(self, node):
        return node.type  != self.type
        #return self.G.nodes(data=True)[node]['type'] == 'seller'

    def __invert__(self):
        self.demand *= -1
        if self.type == 'buyer':
            self.type = 'seller'
        elif self.type == 'seller':
            self.type = 'buyer'
        return (self)

    def __neq__(self, node):
        return self.type != node.type

    def __eq__(self, node):
        return self.type == node.type


    def __str__(self):
        return str(self.id)
     
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id


