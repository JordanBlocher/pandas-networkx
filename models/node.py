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

Point3d = namedtuple('Point3d', ['x', 'y', 'z'])


class Node(nxNode):
    name: int = 0
    demand: float
    value: float
    price: float
    color: float
    type: str
    pos: [int]
    names = []     
    index = ['name', 'demand', 'value', 'price', 'color', 'type', 'pos_x', 'pos_y', 'pos_z', 'ts'] # ts marks price changes

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
        self.color = self.price/params.max_price*params.flow
        if params.flow < 0: 
            self.type = 'buyer'
        else:
            self.type = 'seller'
        self.pos_x = self.price
        self.pos_y = self.name
        self.pos_z = 0#20*params.flow
        self.ts = pd.to_timedelta(0, unit='ms')
                    
        self.winner = False
        nxNode.__init__(self, 
                    name=self.name,
                    demand=self.demand,
                    value=self.value,
                    price=self.price,
                    color=self.color,
                    type=self.type,
                    pos_x=self.pos_x,
                    pos_y=self.pos_y,
                    pos_z=self.pos_z,
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
        return np.ndarray((10,),
                buffer=np.array([
                        int(self.name),
                        self.demand,
                        self.value,
                        self.price,
                        self.color,
                        self.type,
                        self.pos_x,
                        self.pos_y,
                        self.pos_z,
                        self.ts
                ], dtype=object),
                dtype=object)
    
    def __str__(self):
        return f"{self.__array__()}"

    def __repr__(self):
        return str(self.name)
    '''

    def __to_dict__(self):
         return {
                'name': self.name,
                'demand': self.demand,
                'value': self.value,
                'price': self.price,
                'type': self.type,
                'color': self.color,
                'pos': self.pos
            }
    '''
