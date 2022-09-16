import random
import numpy as np
import networkx as nx
import inspect
import pandas as pd
np.set_printoptions(precision=2)

from nx import AdjView, EdgeView, NodeView, DataView
from collections.abc import Mapping, Set

class _CachedPropertyResetterAdj:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_adj"] = value
        if "adj" in od:
            del od["adj"]


class _CachedPropertyResetterNode:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node"] = value
        if "nodes" in od:
            del od["nodes"]

def id(obj):
    if 'id' in obj.__dict__.keys():
       return obj.id
    else:
        obj.__dict__['id'] = obj.__hash__()
        return obj.__hash__()

class nxNode(nx.Graph):
    
    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()

    graph_attr_frame_factory = pd.DataFrame
    node_attr_frame_factory = pd.DataFrame
    edge_attr_frame_factory = pd.DataFrame

    reserved_columns = set()
    attr_columns = set() 

    def __init__(self, **attr):
        attr_columns = set(attr.keys())
        columns = pd.Index(self.__dict__.keys())
        self.graph = self.graph_attr_frame_factory(
                                            DataView(self.__dict__), 
                                            columns=columns
                                            )
        self.reserved_columns=set(columns)-attr_columns
        if 'id' in self.reserved_columns:
            self.graph.set_index('id', inplace=True)
        self.attr_columns = attr_columns
        self._node = self.node_attr_frame_factory()  
        self._adj = self.edge_attr_frame_factory() 

    def add_node(self, new_node, **attr):
        if new_node not in self:
            self._node=self._node.append(new_node.graph.T[id(new_node)])
        else:  
            self._node.loc[id(new_node)] = new_node.graph.loc[id(new_node)]

    def add_edge(self, u, v, **attr):
        self.add_node(u)
        self.add_node(v)
        columns = pd.Index(['source', 'target', 'capacity', 'ts'])
        df = self.edge_attr_frame_factory(DataView(attr), columns=columns)
        df.set_index(['source', 'target'], inplace=True)
        print("DF", df)
        key = (id(u),id(v))
        if key in self._adj.index:
            self._adj.loc[key] = df.loc[key]
        else:
            self._adj = self._adj.append(df)
        print(self._adj)

    def get_edge_data(self, u, v):
        if (id(u),id(v)) in self._adj.index:
            return self._adj.loc[idx[id(u),id(v)]]
        else:
            return pd.Series()
            
    def remove_node(self, n):
        adj = self._adj
        try:
            nbrs = list(adj[n])  
            del self._node[n]
        except KeyError as err:  
            return 'NetworkXError: n not in self'
        for u in nbrs:
            del adj[u][n]  
        del adj[n] 

    def nodes(self, data=True):
        return NodeView(self).data
    
    def adj(self):
        return AdjView(self._adj)
        
    def edges(self, data=False):
        return EdgeView(self)

    '''
    def update(self, nodes=None, edges=None,):
        if edges is not None:
            if nodes is not None:
                [self.add_node(node) for node in nodes]
                [self.add_edge(edge) for edge in edges]
        elif nodes is not None:
            [self.add_node(node) for node in nodes]
        else:
            return 'NetworkXError: empty update'
    '''

    def __setattr__(self, v, k):
        self.__dict__[v] = k
        #print(id(self), type(k), k, v, '\n')
        if v in self.attr_columns:
            if type(k) == np.ndarray:
                self.graph.loc[:,v].values[0] = k.round(2)
            else: 
                self.graph.loc[:,v].values[0] = k

    def __get_item(self, n):
        idx = pd.IndexSlice
        return self._adj.loc[idx[n,:],:]

    def __contains__(self, n):
        try:
            return id(n) in self._node.index
        except TypeError:
            return false
  
    def __name__(self):
        return 'nxnode'

    def name(self):
        return self.__name__()
    
    def __iter__(self):
        return iter(self._node.index)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name!r}" if self.name else "",
                f" with {len(self)} nodes and {len(self)} edges",

            ]
        )


