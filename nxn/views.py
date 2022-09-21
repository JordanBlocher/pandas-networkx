from collections.abc import Mapping, Set
import numpy as np
import pandas as pd


class AtlasView(Mapping):

    __slots__ = ("_atlas",)

    def __getstate__(self):
        return {"_atlas": self._atlas}

    def __setstate__(self, state):
        self._atlas = state["_atlas"]

    def __init__(self, f):
        self._atlas = f

    def __len__(self):
        return len(self._atlas)

    def __iter__(self):
        values = (self._atlas,)
        return iter(values)

    def __getitem__(self, n):
        return self._atlas[n]

    def __str__(self):
        return str(self._atlas)  # {nbr: self[nbr] for nbr in self})

    def __repr__(self):
        return f"{self.__class__.__name__}({self._atlas!r})"



class NodeView(Mapping, Set):

    __slots__ = ("_nodes", "_data",)

    def __getstate__(self):
        return {"_nodes": self._nodes, "_data": self._data}

    def __setstate__(self, state):
        self._nodes = state["_nodes"]
        self._data = state["_data"]

    def __init__(self, graph, data=False):
        self._nodes = graph._node
        self._data = data

    # Mapping methods
    def __len__(self):
        return len(self._nodes.index)

    def __iter__(self):
        data = self._data
        if data is False:
            return iter(self._nodes.index)
        if data is True:
            return iter(self._nodes.items())
        return (
            (n, df[data] if data in df else None)
            for n, df in self._nodes.items()
        )

    def __getitem__(self, n):
        df = self._nodes.loc[n]
        data = self._data
        if data is False or data is True:
            return self._nodes.loc[n]
        return self._nodes[data] if data in self else None

    def __setitem__(self, n, k, v):
        try:
            self._nodes.loc[n,k] = v
        except KeyError(f"Node {n} not found"):
            return

    def __getattr__(self, k):
        try:
            return self._nodes[k] 
        except KeyError:
            return

    # Set methods
    def __contains__(self, n):
        try:
            node_in = n in self._nodes.index
        except TypeError:
            try:
                n, d = n.name, n
                return n in self._nodes.index and self[n].all() == d.all()
            except (TypeError, ValueError):
                return False
        try:
            n, d = n, self._nodes.loc[n]
        except (TypeError, ValueError):
            return False
        return n in self._nodes.index and self[n].all() == d.all()


    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __str__(self):
        return str(list(self))

    def __index__(self):
        return self._nodes.loc

    def __repr__(self):
        name = self.__class__.__name__
        if self._data is False:
            return f"{list(self._nodes.index)}"
        if self._data is True:
            return f"{self._nodes.loc[:]}"
        return f"{list(self._nodes.index)}"


class AdjView(AtlasView):

    __slots__ = ()

    def __getitem__(self, name):
        return AtlasView(self._atlas[name])


class EdgeView(Set, Mapping):

    __slots__ = (
        "_nodes", 
        "_graph", 
        "_data", 
        "_adjframe", 
        "_report")

    def __getstate__(self):
        return {
                "_graph": self._graph, 
                "_adjframe": self._adjframe, 
                "_nodes": self._nodes,
                "_data": self._data
                }

    def __setstate__(self, state):
        self._graph = state["_graph"]
        self._adjframe = state["_adjframe"]
        self._data = state["_data"]
        self._nodes = state["_nodes"]

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __init__(self, G, data=False):
        self._graph = G
        self._adjframe = self._graph._adj.loc
        out_nodes = set([u for u,v in G._adj.index])
        in_nodes = set([v for u,v in G._adj.index])
        #buyers = set(G._node.loc[G.node.type == 'buyer'])
        #out_nodes.append(in_nodes.intersection(buyers))
        #in_nodes = in_nodes.difference(buyers)
        #self._nodes = [out_nodes, in_nodes]
        self._nodes = out_nodes
        self._data = data
        if data is True:
            self._report = lambda n,nbr,df: (n,nbr,self._adjframe[n].T[nbr])
        elif data is False:
            self._report = lambda n,nbr,df: (n,nbr)
            #self._report = lambda n, nbr, df: (n, list(self._adjframe[n].index))
        else:  # data is attribute name
            self._report = (
                lambda n,nbr,df: (n,nbr,df[n].T[nbr][data])
                if data in df
                else (n, nbr, 1.0)
            )

    # Set methods
    def __len__(self):
        return sum(len(self._adjframe[n].index) for n in self._nodes)

    def __iter__(self):
        return (
            self._report(n, nbr, None)
            for n in self._nodes
            for nbr in self._adjframe[n].index
            )

    def __contains__(self, e):
        try:
            u, v = e
            return v in list(self._adjframe[u].index)
        except (KeyError, ValueError):
            return False

    def __getattr__(self, a):
        try:
            self._adjframe=self._graph._adj[str(a)]
            return self._adjframe
        except KeyError:
            return

    # Mapping Methods
    def __getitem__(self, e):
        try:
            u, v = e
            return self._adjframe[u].T[v]
        except TypeError:
            try:
                return self._adjframe[e].T
            except KeyError:
                return

    # String Methods
    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return f"{list(self)}"


class EdgeSet(EdgeView):
    
    __slots__ = ()

    def __setitem__(self, k, v):
        print("SET ITEM", k, v)
        if type(v) == np.ndarray:
            v = v.round(2)
        try:
            u, v = k
            self._adjframe[u].T[v] = v
        except TypeError:
            try:
                self._adjframe[k] = v
            except KeyError:
                return
 


