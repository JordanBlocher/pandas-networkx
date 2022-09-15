import random
import numpy as np
import networkx as nx
import seaborn as sns
import inspect
np.set_printoptions(precision=2)
    

class Node:
    
    ids = []
    id = 0

    def __init__(self):
        rng = nx.utils.create_random_state()
        Node.id +=1
        self.id = Node.id
        self.demand = rng.randint(1, 15)
        self.private_value = 0
        self.price = rng.randint(1, 15)
        self.type = 'seller'
        self.color = (0,0,self.id)
        self.pos = (0,0,0)

    def filter(self, node):
        return self.type == node.type

    def inv_filter(self, node):
        return self.type != node.type

    def __str__(self):
        stack = inspect.stack()
        return str({
                'id': self.id, 
                'demand': self.demand, 
                'value': self.private_value,
                'price': self.price,
                'type': self.type,
                'color': self.color,
                'pos': self.pos
                })

    def __repr__(self):
        stack = inspect.stack()
        return {
                'id': self.id, 
                'demand': self.demand, 
                'value': self.private_value,
                'price': self.price,
                'type': self.type,
                'color': self.color,
                'pos': self.pos
                }

    def stack(self):
        return inspect.stack()
  
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

