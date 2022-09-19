import random
import numpy as np
np.set_printoptions(precision=2)
import networkx as nx
import seaborn as sns
import inspect
from nxn import nxNode, name

class Node(nxNode):
    
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
    
  
