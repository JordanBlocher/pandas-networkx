import random
import numpy as np
import networkx as nx
import inspect
import pandas as pd
np.set_printoptions(precision=2)
from .array import NXDtype, NXArray

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


class nxNode(nx.Graph):
    
    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()

    
    graph_attr_frame_factory = pd.DataFrame
    node_frame_factory = pd.DataFrame
    edge_attr_frame_factory = pd.DataFrame
    adjlist_outer_frame_factory = pd.DataFrame
    adjlist_inner_frame_factory = pd.DataFrame

    reserved_columns = ['id']
    attr_columns = [] 

    def __init__(self, **attr):
        self.attr_columns = list(attr.keys())
        self._node = self.node_frame_factory()  
        self._adj = self.adjlist_outer_frame_factory()  
        self.graph = self.graph_attr_frame_factory(
                                            DataView(attr), 
                                            columns=self.attr_columns,
                                            )
        print(self.graph.columns)
        if self.reserved_columns[0] in self.graph.columns:
            self.graph.set_index('id', inplace=True)

    def add_node(self, new_node, **attr):
        print(attr)
        if new_node.id not in self._node.index:
            self._node=self._node.append(new_node.graph.T[new_node.id])
        else:  
            self._node[new_node.id]

    def add_edge(self, u, v, **attr):
        if u not in self._node:
            self._adj[u] = self.adjlist_inner_frame_factory()
            self._node[u] = self.node_attr_frame_factory()
        if v not in self._node:
            self._adj[v] = self.adjlist_inner_frame_factory()
            self._node[v] = self.node_attr_frame_factory()

        dataframe = self._adj[u].get(v, self.edge_attr_frame_factory())
        dataframe.update(attr)
        self._adj[u][v] = dataframe
        self._adj[v][u] = dataframe

    def get_edge_data(self, u, v):
        try:
            return self._adj[u][v]
        except KeyError:
            return default
    
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
        return NodeView(self)
    
    def adj(self):
        return AdjView(self._adj)
        
    def edges(self, data=False):
        return EdgeView(self)

    def add_edge(self, u_of_edge, v_of_edge, **attr):
        u, v = u_of_edge, v_of_edge
        if u not in self._node:
            self._adj[u] = self.adjlist_inner_frame_factory()
            self._node[u] = self.node_attr_frame_factory()
        if v not in self._node:
            self._adj[v] = self.adjlist_inner_frame_factory()
            self._node[v] = self.node_attr_frame_factory()
        dataframe = self._adj[u].get(v, self.edge_attr_frame_factory())
        dataframe.update(attr)
        self._adj[u][v] = dataframe
        self._adj[v][u] = dataframe

    def update(self, edges=None, nodes=None):
        if edges is not None:
            if nodes is not None:
                [self.add_node(node) for node in nodes]
                [self.add_edge(edge) for edge in edges]
        elif nodes is not None:
            [self.add_node(node) for node in nodes]
        else:
            return 'NetworkXError: empty update'

    def __setattr__(self, v, k):
        print("HERE")
        self.__dict__[v] = k
        self.__node[v][self.id] = k

    def __get_item(self, n):


    def __name__(self):
        return 'nxnode'

    def __iter__(self):
        return iter(self._node)

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name!r}" if self.name else "",
                f" with {self.number_of_nodes()} nodes and {self.number_of_edges()} edges",

            ]
        )


