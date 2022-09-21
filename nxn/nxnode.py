import random
import numpy as np
import networkx as nx
import inspect
import pandas as pd
np.set_printoptions(precision=2)
import inspect
from params import make_params
import time
from .views import AdjView, EdgeView, NodeView, AtlasView, EdgeSet
from termcolor import colored

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

def name(obj):
    n = None
    #stack = inspect.stack()
    #for frame in stack:
    #print('\n',frame.filename, frame.function) 
    #print('\n',stack[1].filename, stack[1].function) 
    if type(obj) == tuple:
        n = (name(obj[0]), name(obj[1]))
    elif type(obj) == int or type(obj) == float:
        n = obj
    elif obj.name != None:
        n = obj.name
    elif type(obj) == str:
        n = obj
    elif 'name' in obj.__dict__.keys():
        n = obj.name
    elif 'ts' in obj.__dict__.keys():
        n = obj.ts
    elif type(obj) == pd.Series:
        n = obj.name
    elif type(obj) == pd.DataFrame:
        print(obj)
        n = obj.name
    else:
        n = obj.__hash__()
    return n    
    
def TS():
    params=make_params()
    return round(time.time() - params.start_time,3)

class nxNode(nx.Graph):
    
    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()
    _graph = {}

    graph_attr_frame_factory = pd.Series
    node_attr_frame_factory = pd.DataFrame
    node_attr_frame_factory.name = '_node'
    edge_attr_frame_factory = pd.DataFrame
    edge_attr_frame_factory.name = '_adj' 

    G = None
    reserved_columns = []
    attr_columns = []

    def __init__(self, **attr):
        attr_columns = list(attr.keys())
        columns = pd.Index(self.__dict__.keys())
        self._node = self.node_attr_frame_factory(
                                            AtlasView(self.__dict__), 
                                            columns=columns
                                            )
        self._adj = self.edge_attr_frame_factory() 
        G = self.G()
        if len(self.reserved_columns) > 0:
            self._node.set_index(self.reserved_columns, inplace=True)
        print(self._graph)

    def G(self):
        return self


    def add_node(self, new_node, **attr):
        #print("ADDING", new_node.type, "NODE", name(new_node), type(new_node), TS())
        reserved_columns = ['name']
        attr_columns = ['demand', 'value', 'price', 'color', 'type', 'pos'] 
 
        columns = pd.Index(new_node.__dict__.keys())
        _node = self.node_attr_frame_factory(
                                        AtlasView(new_node.__dict__), 
                                        columns=attr_columns
                                        )
        _node.set_index(reserved_columns, inplace=True)
        if _node in self:
            self._node.loc[name(_node)] = _node
        else:  
            self._node=self._node.append(_node)
        self._graph[name(new_node)] = new_node

    def add_edge(self, u, v, **attr):
        self.add_node(u)
        self.add_node(v)
        columns = pd.Index(attr.keys())
        df = self.edge_attr_frame_factory(AtlasView(attr), columns=columns)
        df.set_index(['source', 'target'], inplace=True)
        key = (u,v)
        if key in self:
            self._adj.loc[name(key)]=df.loc[name(key)]
 
        else:
            self._adj = self._adj.append(df)
    
    def get_edge_data(self, u, v):
        idx = pd.IndexSlice
        if (u,v) in self:
            return self._adj.loc[idx[name(u,v)]]
        else:
            return pd.Series()
            
    def has_edge(self, u, v):
        return (u,v) in self._adj.index
 
    def remove_node(self, n):
        if n in self:
            for e in self[n].T:
                self._adj = self._adj.drop(e)
            self._node = self._node.drop(name(n))

    def nodes(self, data=False):
        return NodeView(self, data)

    def edges(self, data=False):
        return EdgeView(self, data)

    def neighbors(self, n):
        return self[n].iteritems()

    def subgraph_view(self, ntype=None, n=None):
        newg = self.__class__()
        newg._graph = self
        newg.graph = self.graph
        if ntype:
            newg._node = self._node.loc[ self._node.type == ntype ]
        else:
            newg._node = self._node
        if n:
            idx = pd.IndexSlice
            newg._adj = self[n]
        else:
            newg._adj = self._adj

        return newg
     
    def nnodes(self):
        return len(self._node.index)
    def nedges(self):
        return len(self._adj.index)

    def edge_map(self, weight=None):
        if weight:
            emap = [(u, v, df[weight])
                        for u,v,df in self.edges(data=True)]
        else:
            emap = [(u, v, dict(df)) 
                        for u,v,df in self.edges(data=True)]
        return emap

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

    def __getitem__(self, n):
        idx = pd.IndexSlice
        nbrs = pd.Series()
        if name(n) in self._node.loc[ self._node.type == 'seller'].index:
            nbrs = self._adj.loc[idx[:,name(n)],:]
            #print(self._adj.loc[idx[:,name(n)],:])
            return nbrs
        if name(n) in self._node.loc[ self._node.type == 'buyer'].index:
            #print(self._adj.loc[idx[name(n),:],:])
            nbrs = self._adj.loc[idx[name(n),:],:]
            try:
                #print(self._adj.loc[idx[:,name(n)],:])
                nbrs = nbrs.append(self._adj.loc[idx[:,name(n)],:])
            except KeyError:
                return nbrs
            return nbrs

    def __contains__(self, n):
        if type(n) == tuple:
            return name(n) in self._adj.index
        elif type(n) == str:
            return n in self._node.columns or n in self_node.index
        else:
            return name(n) in self._node.index
 
    def __setattr__(self, k, v):
        print(name(self), type(k), k, v, '\n')
        self.__dict__[k] = v
        if k in self.attr_columns:
            if type(k) == np.ndarray:
                self.graph[k] = v.round(2)
            else: 
                self.graph[k] = v

    def __getattr__(self, k):
        print(name(self), type(k), k, '\n')
        if k in self.attr_columns:
            return self.graph.loc[k]

    def name(self):
        return name(self)
    
    def __iter__(self):
        return iter(self._node.index)

    def __len__(self):
        return len(self._node.index)

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" {self.name}" if self.name else "{self.ts}",
                f" with {len(self._node)} nodes and {len(self._adj)} edges",
                f"{self.graph}",
            ]
        )

def nodes(G):
    return G.nodes()

def edges(G):
    return G.edges()


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
