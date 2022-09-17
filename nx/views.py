from collections.abc import Mapping, Set

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

    def __init__(self, graph, data=None):
        self._nodes = graph._node
        self._data = self._nodes.loc[:]

    # Mapping methods
    def __len__(self):
        return len(self._nodes.index)

    def __iter__(self):
        data = self._data
        return self._nodes.T.iteritems()

    def __getitem__(self, n):
        print("GETITEM", n)
        f = self._nodes.loc[n]
        data = self_data
        return f[data] if data in f else f

    def __getattr__(self, k):
        print("GETATTR", k)
        if k in self._nodes.columns:
            return self._nodes[k] 

    # Set methods
    def __contains__(self, n):
        try:
            node_in = n in self._nodes
        except TypeError:
            n, d = n
            return n in self._nodes and self.loc[n] == d
        if node_in is True:
            return node_in
        try:
            n, d = n
        except (TypeError, ValueError):
            return False
        return n in self._nodes and self.loc[n] == d

    def __setitem__(self, n, k, value):
        print("SETITEM")
        print(n, data, k)
        try:
            self._nodes.loc[n,k] = value
        except KeyError(f"Node {n} not found"):
            return

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    def __str__(self):
        return str(list(self))

    def __index__(self, n):
        print("INDEX")
        try:
            return self._nodes.loc[n]
        except:
            return self._nodes.loc

    def __repr__(self):
        return f"{self.__class__.__name__}({self._nodes.loc[:]})"


class AdjView(Mapping):

    __slots__ = ("_adj",)

    def __getstate__(self):
        return {"_adj": self._adj}

    def __setstate__(self, state):
        self._adj = state["_adj"]

    def __init__(self, f):
        self._adj = f

    def __len__(self):
        return len(self._adj.index)

    def __iter__(self):
        return self._adj.T.iteritems()

    def __getitem__(self, key):
        return self._adj.T[key]

    def __repr__(self):
        return f"{self._adj.loc[:]}"


class EdgeView(AdjView):

    __slots__ = ()

    def __contains__(self, e):
        try:
            u, v = e[:2]
            return (u,v) in self._adj.index
        except (KeyError, ValueError):
            return False


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


