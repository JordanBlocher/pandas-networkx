import random
import numpy as np
import networkx as nx
import seaborn as sns
import inspect
np.set_printoptions(precision=2)



class _CachedPropertyResetterNode:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node"] = value
        if "nodes" in od:
            del od["nodes"]

class Node(nx.Graph):
    
    id = 0
    ids = []

    '''
    _node = _CachedPropertyResetterNode()

    node_dict_factory = dict
    node_attr_dict_factory = dict
    adjlist_outer_dict_factory = dict
    adjlist_inner_dict_factory = dict
    edge_attr_dict_factory = dict
    graph_attr_dict_factory = dict

    def __init__(self):
        
        self.graph = self.graph_attr_dict_factory()  
        self._node = self.node_dict_factory()  
        self._adj = self.adjlist_outer_dict_factory()  
    '''

    def build(self, params):
        rng = nx.utils.create_random_state()
        if len(Node.ids) > 1:
            n_id = rng.choice(Node.ids)
            Node.ids.remove(self.id)
        else:
            Node.id +=1
            n_id = Node.id
        
        demand = rng.randint(1, 
                            params['max_quantity']
                            ) * params['flow']
        private_value = 0
        price = round(
                        params['init_factor'
                        ] * params['price'][n_id], 2)
        color = int(price)*params['flow']
        if params['flow'] < 0:
            n_type = 'buyer'
        else:
            n_type = 'seller'
        pos = [n_id*20, color*params['flow'], 0]
      #  nx.Graph().__init__(id=n_id, demand=demand, 
       #                     value=private_value, price=price, 
        #                    color=color, pos=pos, type=n_type
         #               )
        self.id = n_id
        self.demand = demand
        self.color = color
        self.private_value = private_value
        self.price = price
        self.pos = pos
        self.type = n_type

    def __to_dict__(self):
         return {
                'demand': self.demand, 
                'value': self.private_value,
                'price': self.price,
                'type': self.type,
                'color': self.color,
                'pos': self.pos
            }

    def filter(self, node):
        return self.type == node.type

    def inv_filter(self, node):
        return self.type != node.type


    def __str__(self):
        stack = inspect.stack()
        #for frame in stack:
        #    print('\n',frame.filename, frame.function)
        if stack[1].function == '<dictcomp>':
            return  str(self.__dict__())
        elif stack[1].function == 'plot':
            return  str(self.__dict__())
        elif stack[2].function == 'plot':
            return  str(self.__dict__())
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


