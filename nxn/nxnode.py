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
from collections import namedtuple

__all__ = ["nxNode"]


class _CachedPropertyResetterAdj:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_adj"] = value
        if "adj" in od:
            print("USINGTHISFUNCTIOIN!!!!!!!\n\n\n\n\n\n")
            del od["adj"]


class _CachedPropertyResetterNode:
    def __set__(self, obj, value):
        od = obj.__dict__
        od["_node"] = value
        if "nodes" in od:
            del od["nodes"]


def name(obj):
    if type(obj) == tuple:
        return (obj[0].name, obj[1].name)
    elif type(obj) == int or type(obj) == float:
        return obj
    elif obj.name != None:
        return obj.name
    elif type(obj) == str:
        return obj
    elif type(obj) == pd.DataFrame:
        print("INDEXIS NAMEOF DF", obj.index)
        return obj.index[0]
    else:
        raise ValueError(f"{self.__class__} is missing a name")


def TS():
    params=make_params()
    return round(time.time() - params.start_time,3)

class nxNode(nx.Graph):
    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()

    graph_attr_frame_factory = pd.DataFrame
    graph_frame_factory = pd.Index
    node_attr_frame_factory = pd.DataFrame
    node_frame_factory = pd.Index
    edge_attr_frame_factory = pd.DataFrame
    edge_frame_factory = pd.Index

    def __init__(self, **attr):
        try:
            self.graph = self.graph_attr_frame_factory(
                                                [attr],
                                                columns=attr.keys()
                                                )
        except:
            self.graph = self.graph_attr_frame_factory([np.array(self)],
                                                    columns=attr.keys()
                                                    )
        idx = self.graph_frame_factory({self})
        self.graph.set_index(idx, inplace=True)
        self._adj = self.edge_attr_frame_factory() 
        self._node = self.node_attr_frame_factory() 

    def add_node(self, new_node, **attr):
        new_node.__signal__ = self.__setattr_node__
        _idx = self.node_frame_factory({new_node})
        #print("INDEX", index)
        
        #print('\n-------------------\n')
        #print("NODE", new_node, '\n-------------\n')
        #print("ARRAY",np.array(new_node), '\n----------------\n')
        
        _node = self.node_attr_frame_factory(
                                        [np.array(new_node)],
                                        columns=new_node.index
                                        )
        _node.set_index(_idx, inplace=True)
        if new_node in self:
            #self._node.loc[name(_node)] = _node
            self._node.update(_node)
        else:  
            #print("ADDING", new_node.type, "NODE", new_node.name, type(new_node), "at",  TS())
            self._node = self._node.append(_node)
        #self._graph[name(new_node)] = new_node

    def add_edge(self, u, v, **attr):
        #print("ADDINGEDGE")
        self.add_node(u)
        self.add_node(v)
        columns = pd.Index(attr.keys())
        index = pd.Index({(u.name, v.name)})
        df = self.edge_attr_frame_factory([attr], columns=columns)
        #print("DF",df)
        df.set_index(index, inplace=True)
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
            self._node.drop(n.name)
            self._graph.drop(n)

    def nodes(self, data=False):
        return NodeView(self, data)

    def adj(self):
        return AdjView(self._adj)

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
        if n in self._node.loc[ self._node.type == 'seller'].index:
            nbrs = self._adj.loc[idx[:,name(n)],:]
            #print(self._adj.loc[idx[:,name(n)],:])
            return nbrs
        if n in self._node.loc[ self._node.type == 'buyer'].index:
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
            u,v = n
            #print("\n\ncheckin if (",  u.name, v.name ,") in self, type", type(n), "index", u.graph.index[0], v.graph.index[0])
            return (u.name, v.name) in self._adj.index
        else:
            #print("\n\ncheckin if", n.name,"in self, type", type(n), "index", n.graph.index[0])
            try:
                return n in self._node.index
            except:
                return False
        
    def __setattr__(self, k, v):
        #print("SET", type(k), k, v, '\n')
        self.__dict__[k] = v

    def __signal__(self, node):
        pass

    def __setattr_node__(self, node):
        if node in self:
            #print("SELF", self.name, type(self), '\n')
            #print("CHILD", node.name, type(node), node, '\n')
            #print(self._node.index.get_loc(node))
            #idx = self._node.index.get_loc(node)
            #print(self._node.index[idx])
            self._node.index.drop(node)
            self.add_node(node)

    def __iter__(self):
        return iter(self._node.index)

    def __len__(self):
        return len(self._node.index)

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" with {len(self._node)} nodes and {len(self._adj)} edges",
                f"{self.graph.values}",
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
