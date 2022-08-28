import random
import numpy as np
np.set_printoptions(precision=2)
from params import * 
import json

def Buyer():
    return Node('green', 'buyer', BUYER_FACTOR, -1)

def Seller():
    return Node('magenta', 'seller', SELLER_FACTOR, 1)

class Node:

    ids = [n for n in range(1, MAX_NETWORK_SIZE)]
    id = 0

    def __init__(self, color, ntype, factor, flow):
        self.id = Node.ids.pop(0)
        self.demand = int(np.random.uniform(1, MAX_QUANTITY))*flow
        self.private_value = RD(np.random.uniform(1, MAX_PRICE))
        self.color = color
        self.type = ntype
        self.price = RD(self.private_value*factor)

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

    def bid(self):
        return {"price": RD(self.price), "demand": self.demand}

    def __repr__(self):
        return str(self.id)

    def data(self):
        return {"price": RD(self.price), \
                "value": RD(self.private_value), \
                "color": self.color,\
                 "type": self.type}



