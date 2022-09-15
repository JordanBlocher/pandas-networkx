import random
import numpy as np
import networkx as nx
import seaborn as sns
import inspect
from nxnode import nxNode
np.set_printoptions(precision=2)

import pandas as pd
from pandas.core.dtypes.base import ExtensionDtype
from pandas.api.extensions import register_extension_dtype
from pandas.core.arrays import ExtensionArray, ExtensionScalarOpsMixin



class Node(nxNode):
    
    id = 0
    ids = []

    def __init__(self, params):
        super().__init__()
        rng = nx.utils.create_random_state()
        if len(Node.ids) > 1:
            self.id = rng.choice(Node.ids)
            Node.ids.remove(self.id)
        else:
            Node.id +=1
            self.id = Node.id
        
        self.demand = rng.randint(1, 
                            params['max_quantity']
                            ) * params['flow']
        self.private_value = 0
        self.price = round(
                        params['init_factor'
                        ] * params['price'][self.id], 2)
        self.color = int(self.price)*params['flow']
        if params['flow'] < 0: # negative flow wants to send out 
            self.type = 'buyer'
        else:
            self.type = 'seller'
        self.pos = [self.id*20, self.color*params['flow'], 0]


    def filter(self, node):
        return self.type == node.type

    def inv_filter(self, node):
        return self.type != node.type

    def add_node(self, node):
        super().add_node(node,
                price=node.price,
                value=node.private_value, 
                color=node.color, 
                demand=node.demand,
                pos=node.pos,
                type=node.type
                )

    def add_edge(self, source, target, ts=None):
        super().add_edge(
                    source,
                    target,
                    capacity = source.price,
                    weight = source.demand,
                    ts=ts
                    )
    
    '''
    def __to_dict__(self):
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
            return  str(self.__to_dict__())+'\n'
        elif stack[1].function == 'plot':
            return  str(self.__to_dict__())+'\n'
        elif stack[2].function == 'plot':
            return  str(self.__to_dict__())+'\n'
        elif 'print' in stack[2].function:
            return  str(self.__to_dict__())+'\n'
        else:
            return str(self.id)
            
    def __repr__(self):
        stack = inspect.stack()
        #for frame in stack:
        #    print('\n',frame.filename, frame.function)
        if stack[-1].filename == '<stdin>':
            return str(self.id)
        elif stack[1].function == '_object_format':
            return str(self.id)
        elif stack[1].function == 'plot':
            return str(self.id)
        elif stack[1].function == 'save_frame':
            return str(self.id)
        elif stack[1].function == '__str__':
            return str(self.id)
        elif stack[2].function == 'plot':
            return str(self.id)
        else:
            return self

    def __index__(self):
        return int(self.id)
   
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id

    '''
