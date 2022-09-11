import random
import numpy as np
import networkx as nx
import seaborn as sns
import inspect
np.set_printoptions(precision=2)
    

class Node:
    
    ids = []
    id = 0

    def __init__(self, params):
        rng = nx.utils.create_random_state()
        if len(Node.ids) > 1:
            self.id = rng.choice(Node.ids)
            self.ids.remove(self.id)
        else:
            Node.id +=1
            self.id = Node.id
        self.demand = rng.randint(1, params['max_quantity']) * params['flow']
        self.private_value = 0
        self.price = round(params['init_factor'] * params['price'][self.id], 2)
        if params['flow'] < 0:
            self.type = 'buyer'
        else:
            self.type = 'seller'
        self.color = (0,0,self.id)
        self.pos = (0,0,0)

    def filter(self, node):
        return self.type == node.type

    def inv_filter(self, node):
        return self.type != node.type

    def __dict__(self):
         return {
                'demand': self.demand, 
                'value': self.private_value,
                'price': self.price,
                'type': self.type,
                'color': self.color,
                'pos': self.pos
            }

    def __str__(self):
        stack = inspect.stack()
        #for frame in stack:
        #    print('\n',frame.filename, frame.function)
        if stack[1].function == '<dictcomp>':
            return  str(self.__dict__())
        else:
            return str(self.id)
            
    def __repr__(self):
        stack = inspect.stack()
        if stack[-1].filename == '<stdin>':
            return str(self.id)
        else:
            return self
   
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id


