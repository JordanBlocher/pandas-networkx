import random
import numpy as np
import networkx as nx
import inspect
import pandas as pd
np.set_printoptions(precision=2)

from .views import AdjView, EdgeView, NodeView, AtlasView
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
    if type(obj) == int:
        return obj
    elif type(obj) == tuple:
        return (id(obj[0]), id(obj[1]))
    elif 'id' in obj.__dict__.keys():
       return obj.id
    elif 'ts' in obj.__dict__.keys():
       return obj.ts
    else:
        obj.__dict__['id'] = obj.__hash__()
        return obj.__hash__()

def nodes(n):
    return n.nodes()

def edges(n):
    return n.edges()

class nxNode(nx.Graph):
    
    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()

    graph_attr_frame_factory = pd.DataFrame
    node_attr_frame_factory = pd.DataFrame
    edge_attr_frame_factory = pd.DataFrame

    reserved_columns = [] 
    attr_columns = [] 

    def __init__(self, **attr):
        attr_columns = list(attr.keys())
        columns = pd.Index(self.__dict__.keys())
        self.graph = self.graph_attr_frame_factory(
                                            AtlasView(self.__dict__), 
                                            columns=columns
                                            )
        self.reserved_columns=pd.Index(set(columns)-set(attr_columns))
        if not self.reserved_columns.empty:
            self.graph.set_index(list(self.reserved_columns), inplace=True)
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
        columns = pd.Index(attr.keys())
        df = self.edge_attr_frame_factory(AtlasView(attr), columns=columns)
        df.set_index(['source', 'target'], inplace=True)
        if (u,v) in self:
            self._adj.loc[key] = df.loc[key]
        else:
            self._adj = self._adj.append(df)
    
    def add_star(self, nodes_for_star, **attr):
        nlist = iter(nodes_for_star)
        try:
            v = next(nlist)
        except StopIteration:
            return
        self.add_node(v)
        edges = ((v, n) for n in nlist)
        for u, v in edges:
            nxnode.add_edge(u, v, **attr)

    def get_edge_data(self, u, v):
        idx = pd.IndexSlice
        if (u,v) in self:
            return self._adj.loc[idx[id(u,v)]]
        else:
            return pd.Series()
            
    def has_edge(self, u, v):
        return (u,v) in self._adj.index
 
    def remove_node(self, n):
        if type(n) == Node:
            Node.ids.append(n.id)
        if n in self:
            for e in self[n].T:
                self._adj = self._adj.drop(e)
            self._node = self._node.drop(id(n))

    def nodes(self):
        return NodeView(self)
 
    def adj(self):
        return AdjView(self._adj)
        
    def edges(self):
        return EdgeView(self)

    def subgraph(self, nodes):
        induced_nodes = [n for n in self.nodes]
        # if already a subgraph, don't make a chain
        subgraph = self.subgraph_view
        if hasattr(self, "_NODE_OK"):
            return subgraph(self._graph, induced_nodes)
        return subgraph(self, induced_nodes)

    def neighbors(self, n):
        return self[n].iteritems()

    def subgraph_view(self, ntype=None, n=None):
        newg = self.__class__()
        newg._graph = self
        newg.graph = self.graph
        newg._NODE_OK = ntype
        if ntype:
            newg._node = self._node.loc[ self._node.type == ntype ]
        else:
            newg._node = self._node
        if n:
            idx = pd.IndexSlice
            newg._adj = self._adj.loc[ (idx[id(n),:] or idx[:,id(n)]), : ]
        else:
            newg._adj = self._adj

        return newg

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

    def __setattr__(self, k, v):
        print("SETATTR", k, v)
        self.__dict__[k] = v
        if k in self.attr_columns:
            if type(k) == np.ndarray:
                self.graph[k] = v.round(2)
            else: 
                self.graph[k] = v

    def __getattr__(self, k):
        print("GETATTR", k)
        #print(id(self), type(k), k, v, '\n')
        if k in self.attr_columns:
            return self.graph.loc[k]

    def __getitem__(self, n):
        idx = pd.IndexSlice
        if n in self:
            return self._adj.loc[ [self._adj.loc[idx[id(n),:]] & self._adj.loc[idx[:,id(n)]]], : ]

    def __contains__(self, n):
        if type(n) == tuple:
            return id(n) in self._adj.index
        else:
            return id(n) in self._node.index
  
    def __name__(self):
        return 'nxnode'

    def name(self):
        return self.__name__()
    
    def __iter__(self):
        return iter(self._node.index)

    def __len__(self):
        return len(self._node.index)

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" {self.id}" if self.id else "{self.ts}",
                f" with {len(self._node)} nodes and {len(self._adj)} edges",
                f"{self.graph}",
            ]
        )


# distance = capacity
def ego_graph(nxNode, n, radius=1, center=True, distance=None):
    if distance is not None:
        sp, _ = nx.single_source_dijkstra(G, n, cutoff=radius, weight=distance)
    else:
        sp = dict(nx.single_source_shortest_path_length(G, n, cutoff=radius))

    H = G.subgraph(sp).copy()
    if not center:
        H.remove_node(n)
    return H
