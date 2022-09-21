import random
import numpy as np
np.set_printoptions(precision=2)
import networkx as nx
import seaborn as sns
import inspect
from nxn import nxNode, name
import time

class Node(nxNode):
    
    reserved_columns = ['name']
    attr_columns = ['demand', 'value', 'price', 'color', 'type', 'pos'] 
 
    name = 0
    names = []

    def __init__(self, params):
        rng = nx.utils.create_random_state()
        if len(Node.names) > 1:
            self.name = rng.choice(Node.names)
            Node.names.remove(self.name)
        else:
            Node.name +=1
            self.name = Node.name
        
        self.demand = rng.randint(1, 
                            params.max_quantity
                            ) * params.flow
        self.value = 0
        self.price = round(
                        params.init_factor*params.price[self.name], 
                      2
                      )
        self.color = int(self.price)*params.flow
        if params.flow < 0: 
            self.type = 'buyer'
        else:
            self.type = 'seller'
        self.pos = tuple(np.array([
                            self.name*20, 
                            self.color*params.flow,
                            0
                            ], dtype=int)
                        )
        nxNode.__init__(self,
                name=self.name,
                price=self.price,
                value=self.value, 
                color=self.color, 
                demand=self.demand,
                pos=self.pos,
                type=self.type,
                )
        print("GRAPH", self.graph)

    def __setattr__(self, k, v):
        print(name(self), type(k), k, v, '\n')
        self.__dict__[k] = v

    def __getattr__(self, k):
        print(name(self), type(k), k, '\n')


    def filter(self, node):
        return self.type == node.type

    def inv_filter(self, node):
        return self.type != node.type

    def add_edge(self, u, v, ts=None):
        super().add_edge(u ,v,
                    source=name(u),
                    target=name(v),
                    capacity=u.price, 
                    ts=ts
                    )

    def inv(self):
        if self.type == 'buyer':
            return 'seller'
        else:
            return 'buyer'
    
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
