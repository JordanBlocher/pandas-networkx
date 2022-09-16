import random
import numpy as np
np.set_printoptions(precision=2)
import networkx as nx
import seaborn as sns
import inspect
from nx import nxNode, id

class Node(nxNode):
    
    id = 0
    ids = []

    def __init__(self, params):
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
        self.value = 0
        self.price = round(
                        params['init_factor'
                     ] * params['price'][self.id], 2)
        self.color = int(self.price)*params['flow']
        if params['flow'] < 0: 
            self.type = 'buyer'
        else:
            self.type = 'seller'
        self.pos = tuple(np.array([self.id*20, self.color*params['flow'], 0], dtype=int))
        nxNode.__init__(self,
                price=self.price,
                value=self.value, 
                color=self.color, 
                demand=self.demand,
                pos=self.pos,
                type=self.type
                )

    def filter(self, node):
        return self.type == node.type

    def inv_filter(self, node):
        return self.type != node.type

    def add_edge(self, u, v, ts=None):
        super().add_edge(u ,v,
                    source=id(u),
                    target=id(v),
                    capacity=u.price, 
                    ts=ts
                    )
    
    '''
    def add_node(self, node):
        super().add_node(node,
                id=node.id,
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

    '''

