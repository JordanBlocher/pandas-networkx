import random
import numpy as np
np.set_printoptions(precision=2)
import networkx as nx
import inspect
from nxn import nxNode
import time
import pandas as pd
import time
from collections import namedtuple


class Node(nxNode):
    name: int = 0
    demand: float
    value: float
    price: float
    color: float
    type: str
    names = []     
    index = ['name', 'demand', 'value', 'price', 'color', 'type', 'ts'] # ts marks price changes

    def __init__(self, params):
        rng = nx.utils.create_random_state()
        if len(Node.names) > 1:
            self.name = rng.choice(Node.names)
            Node.names.remove(self.name)
        else:
            Node.name +=1
            self.name = Node.name
        #print("ADDING NODE", self.name)
        
        self.demand = rng.randint(1, 
                            params.max_quantity
                            ) * params.flow
        self.value = -1
        self.price = round(
                        params.price[self.name], 
                      2
                      )
        self.color = self.price/params.max_price
        if params.flow < 0: 
            self.type = 'buyer'
        else:
            self.type = 'seller'
        self.ts = pd.to_timedelta(0, unit='ms')
                    
        self.winner = False
        nxNode.__init__(self, 
                    name=int(self.name),
                    demand=self.demand,
                    value=self.value,
                    price=self.price,
                    color=self.color,
                    type=self.type,
                    ts=self.ts
                    )         

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if k in self.index[1:]:
            self.__signal__(self)
            #print("NODE", self)
            #print("NODESETATTR", self.name, type(k), k, v, '\n')

    def inv(node):
        if node.type == 'buyer':
            return 'seller'
        else:
            return 'buyer'
    
    def __array__(self, dtype=np.dtype('object')):
        return np.ndarray((7,),
                buffer=np.array([
                        int(self.name),
                        self.demand,
                        self.value,
                        self.price,
                        self.color,
                        self.type,
                        self.ts
                ], dtype=object),
                dtype=object)
    
    def __str__(self):
        return f"{self.__array__()}"

    def __repr__(self):
        return str(int(self.name))
    '''

    def __to_dict__(self):
         return {
                'name': self.name,
                'demand': self.demand,
                'value': self.value,
                'price': self.price,
                'type': self.type,
                'color': self.color,
            }
    '''
