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
        print("NODEVIEW")
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
            return self._nodes.iteritems()
        return (
            (n, df[data] if data in df else None)
            for n, df in self._nodes.items()
        )

    def __getitem__(self, n):
        df = self._nodes.loc[n]
        data = self._data
        if data is False or data is True:
            return df
        return df[data] if data in df else None

    def __setitem__(self, n, k, v):
        try:
            self._nodes.loc[n,k] = v
        except KeyError(f"Node {n} not found"):
            return

    def __getattr__(self, k):
        if k in self._nodes:
            return self._nodes[k] 

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

    def __setitem__(self, n, k, value):
        try:
            self._nodes.loc[n,k] = value
        except KeyError(f"Node {n} not found"):
            return

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __str__(self):
        return str(list(self))

    def __index__(self):
        print("INDEX")
        return self._nodes.loc

    def __repr__(self):
        name = self.__class__.__name__
        if self._data is False:
            return f"{list(self._nodes.T)}"
        if self._data is True:
            return f"{self._nodes.loc[:]}"
        return f"{self}, data={self._data!r}"


class AdjView(AtlasView):

    __slots__ = ()

    def __getitem__(self, name):
        return AtlasView(self._atlas[name])


class EdgeView(Set, Mapping):

    __slots__ = ("_adjframe", "_graph", "_nodes_nbrs", "_data", "_report")

    def __getstate__(self):
        return {"_graph": self._graph, "_adjframe": self._adj, "_data": self._data}

    def __setstate__(self, state):
        self._graph = state["_graph"]
        self._adjframe = state["_adjframe"]
        self._data = state["_data"]
        self._nodes_nbrs = ((n, (v for u, v in self[n].T)) for n in self.nodes())

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __init__(self, G, data=False):
        self._graph = G
        out_nodes = set([u for u,v in G._adj.index])
        self._adjframe = pd.Series([
                               dict([(
                                        v,
                                        G._adj.loc[
                                               (u,v)
                                              ]
                                    ) for u, v in G[n].T
                                ]) for n in out_nodes
                            ], index=out_nodes
                            )
        print(self._adjframe)
        self._data = data
        self._nodes_nbrs = self._adjframe.items
        if data is True:
            self._report = lambda n, nbr, df: (n, nbr, df)
        elif data is False:
            self._report = lambda n, nbr, df: (n, nbr)
        else:  # data is attribute name
            self._report = (
                lambda n, nbr, df: (n, nbr, df[data])
                if data in df
                else (n, nbr, None)
            )

    # Set methods
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            print("n",n,'\n')
            print("nbrs", type(nbrs), nbrs, '\n')
            for nbr, df in nbrs.items():
                print("nbr", nbr,'\n')
                print("df", df,'\n')
                print("report", self._report(n, nbr, df),'\n')
        return (
            self._report(n, nbr, df)
            for n, nbrs in self._nodes_nbrs()
            for nbr, df in nbrs.items()
        )

    def __contains__(self, e):
        try:
            u, v = e
            return v in self._adjframe[u]
        except (KeyError, ValueError):
            return False

    # Mapping Methods
    def __getitem__(self, e):
        try:
            u, v = e
            return self._adjframe[u][v]
        except TypeError:
            try:
                return self._adjframe[e]
            except KeyError:
                return
    #[[df for nbr, df in nbrs()] for n, nbrs in self._nodes_nbrs()]

    # String Methods
    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return f"{list(self)}"


class FilterAdjacency(Mapping):  

    def __init__(self, d, NODE_OK, EDGE_OK):
        self._atlas = d
        self.NODE_OK = NODE_OK
        self.EDGE_OK = EDGE_OK

    def __len__(self):
        return sum(1 for n in self)

    def __iter__(self):
        try:  # check that NODE_OK has attr 'nodes'
            node_ok_shorter = 2 * len(self.NODE_OK.nodes) < len(self._atlas)
        except AttributeError:
            node_ok_shorter = False
        if node_ok_shorter:
            return (n for n in self.NODE_OK.nodes if n in self._atlas)
        return (n for n in self._atlas if self.NODE_OK(n))

    def __getitem__(self, node):
        if node in self._atlas and self.NODE_OK(node):

            def new_node_ok(nbr):
                return self.NODE_OK(nbr) and self.EDGE_OK(node, nbr)

            return FilterAtlas(self._atlas[node], new_node_ok)
        raise KeyError(f"Key {node} not found")

    def copy(self):
        try:  # check that NODE_OK has attr 'nodes'
            node_ok_shorter = 2 * len(self.NODE_OK.nodes) < len(self._atlas)
        except AttributeError:
            node_ok_shorter = False
        if node_ok_shorter:
            return {
                u: {
                    v: d
                    for v, d in self._atlas[u].items()
                    if self.NODE_OK(v)
                    if self.EDGE_OK(u, v)
                }
                for u in self.NODE_OK.nodes
                if u in self._atlas
            }
        return {
            u: {v: d for v, d in nbrs.items() if self.NODE_OK(v) if self.EDGE_OK(u, v)}
            for u, nbrs in self._atlas.items()
            if self.NODE_OK(u)
        }

    def __str__(self):
        return str({nbr: self[nbr] for nbr in self})

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}({self._atlas!r}, {self.NODE_OK!r}, {self.EDGE_OK!r})"


