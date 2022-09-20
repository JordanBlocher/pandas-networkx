import random
import numpy as np
import networkx as nx
import inspect
import pandas as pd
np.set_printoptions(precision=2)
import inspect

from .views import AdjView, EdgeView, NodeView, AtlasView, EdgeSet

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
    print("NAME", obj, "TYPE", type(obj))
    stack = inspect.stack()
    for frame in stack.frames():
        
    if type(obj) == int or type(obj) == np.int64: 
        return obj
    elif type(obj) == tuple:
        return (name(obj[0]), name(obj[1]))
    elif type(obj) == str:
        print("KEY", obj)
        return obj
    elif obj.name != None:
        return obj.name
    elif 'name' in obj.__dict__.keys():
       return obj.name
    elif 'ts' in obj.__dict__.keys():
       return obj.ts
    else:
        return obj.__hash__()

class nxNode(nx.Graph):
    
    _adj = _CachedPropertyResetterAdj()
    _node = _CachedPropertyResetterNode()

    graph_attr_frame_factory = pd.DataFrame
    node_attr_frame_factory = pd.DataFrame
    edge_attr_frame_factory = pd.DataFrame

    reserved_columns = [] 
    attr_columns = [] 
    G = None

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
        G = self.G()

    def G(self):
        return self


    def add_node(self, new_node, **attr):
        print("ADDING", new_node.type, "NODE", new_node.name, type(new_node),type(self))
        if 'graph' in new_node.__dict__.keys():
            print("ISNXNODE")
            new_node = new_node.graph.T[name(new_node)]
        if new_node not in self:
            print("ADDING")
            self._node=self._node.append(new_node)
        else:  
            print("UPDATING")
            self._node.loc[name(new_node)] = new_node

    def add_edge(self, u, v, **attr):
        self.add_node(u)
        self.add_node(v)
        columns = pd.Index(attr.keys())
        df = self.edge_attr_frame_factory(AtlasView(attr), columns=columns)
        df.set_index(['source', 'target'], inplace=True)
        key = (u,v)
        if key in self:
            self._adj.loc[name(key)] = df.loc[name(key)]
        else:
            self._adj = self._adj.append(df)
    
    def add_star(self, nodes_for_star, **attr):
        #print("FOR STAR", list(nodes_for_star), '\n')
        nlist = iter(nodes_for_star)
        try:
            v = next(nlist)
        except StopIteration:
            return
        self.add_node(v)
        #print("CENTER", v, '\n')
        edges = ((v, n) for n in nlist)
        for v, n in edges:
            #print("HERE",n)
            self.add_edge(v, n, 
                    source=name(v),
                    target=name(n),
                    capacity=v.price, 
                    ts=None
                    )

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
                print("DROPPING EDGE",e)
                self._adj = self._adj.drop(e)
            print("DROPPING NODE",name(n))
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
        print("Nodes", newg.nodes({'type': 'buyer'}))
        if ntype:
            newg._node = self._node.loc[ self._node.type == ntype ]
        else:
            newg._node = self._node
        print("Nodes", newg.nodes())
        if n:
            idx = pd.IndexSlice
            newg._adj = self[n]
        else:
            newg._adj = self._adj
        #print("adj", newg._adj)

        return newg
     
    def nnodes(self, data=False):
        return len(self.nodes(data))

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

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if k in self.attr_columns:
            if type(k) == np.ndarray:
                self.graph[k] = v.round(2)
            else: 
                self.graph[k] = v

    def __getattr__(self, k):
        #print(name(self), type(k), k, v, '\n')
        if k in self.attr_columns:
            return self.graph.loc[k]

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
            return n in self._node.columns
        else:
            return name(n) in self._node.index
  
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
