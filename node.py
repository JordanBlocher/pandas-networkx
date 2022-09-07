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
    reids = []
    #factor = np.random.uniform(0.09, 0.99, size=200)
    id = 0

    def __init__(self, color, type, params):
        if len(self.reids) > 0:
            self.id = Node.reids.pop()
        else:
            self.id = Node.ids.pop()
        self.demand = int(
                        np.random.uniform(1, params['max_quantity'])
                         ) * params['flow']
        self.private_value = None
        self.color = color
        self.type = type
        self.price = round(np.random.uniform(1, 
                                            params['max_price']
                                            ) * params['factor'],
                                            2)
        self.sell_price = 0

    def filter(self, node):
        return node.type == self.type

    def inv_filter(self, node):
        return node.type != self.type

    def __repr__(self):
        return str(self.id)

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


