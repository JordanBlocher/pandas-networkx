import random
import numpy as np
np.set_printoptions(precision=2)
import networkx as nx
import seaborn as sns
import inspect
from nxn import nxNode, AtlasView
import time
import pandas as pd
from collections import namedtuple
from typing import NamedTuple
from pandas import (
    Categorical,
    CategoricalIndex,
    Timestamp,
)
from pandas.api.types import CategoricalDtype
from pandas._typing import (
    Dtype,
    PositionalIndexer,
)

from pandas.core.dtypes.dtypes import register_extension_dtype

from pandas.api.extensions import (
    ExtensionArray,
    ExtensionDtype,
)
from pandas.api.types import pandas_dtype


class Node(nxNode):
   
    index = ['name', 'demand', 'value', 'price', 'color', 'type', 'pos'] 
 
    name = 0
    names = []
    __slots__ = () 
    graph = None

    class node(NamedTuple):
        name: int
        demand: float
        value: float
        price: float
        color: float
        type: str
        pos: tuple
                

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
        self.graph = self.node_attr_frame_factory(
                                            AtlasView(self.__to_dict__()), 
                                            columns=self.index
                                            )
        self.graph.set_index(pd.Index({self.name}), inplace=True)
        self.graph.index.name = 'name'
        nxNode.__setstate__({'_graph': self.graph}, self.name)


    def __setattr__(self, k, v):
        #print("NODE", self.name, type(k), k, v, '\n')
        self.__dict__[k] = v
        #self.beacon()



    def add_edge(self, u, v, ts=None):
        super().add_edge(u ,v,
                    source=u.name,
                    target=v.name,
                    capacity=u.price, 
                    ts=pd.to_timedelta(ts, unit='ms')
                    )

    def inv(node):
        if node.type == 'buyer':
            return 'seller'
        else:
            return 'buyer'
    
    def __str__(self):
        return f"{self.name}"

    def __array__(self):
        return np.array([
                self.name,
                self.demand,
                self.value,
                self.price,
                self.color,
                self.type,
                self.pos
                ], dtype=object)

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
