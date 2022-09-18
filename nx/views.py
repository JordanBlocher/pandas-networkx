from collections.abc import Mapping, Set

def nodes(G):
    return G.nodes()

def edges(G):
    return G.edges()


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
            return f"{[n for n in self._nodes.index]}"
        if self._data is True:
            return f"{self._nodes.loc[:]}"
        return f"{self}, data={self._data!r}"


class AdjView(AtlasView):

    __slots__ = ()

    def __getitem__(self, name):
        return AtlasView(self._atlas[name])


class OutEdgeDataView:

    __slots__ = (
        "_viewer",
        "_data",
        "_adjframe",
        "_nodes_nbrs",
        "_report",
    )

    def __getstate__(self):
        return {
            "viewer": self._viewer,
            "data": self._data,
        }

    def __setstate__(self, state):
        self.__init__(**state)

    def __init__(self, viewer, data=False):
        self._viewer = viewer
        adjframe = self._adjframe = viewer._adjframe
        self._nodes_nbrs = adjframe.items
        self._nbunch = nbunch
        self._data = data
        self._default = default
        # Set _report based on data and default
        if data is True:
            self._report = lambda n, nbr, dd: (n, nbr, dd)
        elif data is False:
            self._report = lambda n, nbr, dd: (n, nbr)
        else:  # data is attribute name
            self._report = (
                lambda n, nbr, dd: (n, nbr, dd[data])
                if data in dd
                else (n, nbr, default)
            )

    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())

    def __iter__(self):
        return (
            self._report(n, nbr, dd)
            for n, nbrs in self._nodes_nbrs()
            for nbr, dd in nbrs.items()
        )

    def __contains__(self, e):
        u, v = e[:2]
        try:
            dframe = self._adjframe[u][v]
        except KeyError:
            return False
        return e == self._report(u, v, dframe)

    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self)})"


class EdgeDataView(OutEdgeDataView):

    __slots__ = ()

    def __len__(self):
        return sum(1 for e in self)

    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr, dd in nbrs.items():
                if nbr not in seen:
                    yield self._report(n, nbr, dd)
            seen[n] = 1
        del seen

    def __contains__(self, e):
        u, v = e[:2]
        try:
            dframe = self._adjframe[u][v]
        except KeyError:
            return False
        return e == self._report(u, v, dframe)


class OutEdgeView(Set, Mapping):

    __slots__ = ("_adjframe", "_graph", "_nodes_nbrs")

    def __getstate__(self):
        return {"_graph": self._graph, "_adjframe": self._adjframe}

    def __setstate__(self, state):
        self._graph = state["_graph"]
        self._adjframe = state["_adjframe"]
        self._nodes_nbrs = self._adjframe.items

    @classmethod
    def _from_iterable(cls, it):
        return set(it)

    dataview = OutEdgeDataView

    def __init__(self, G):
        self._graph = G
        self._adjframe = G._succ if hasattr(G, "succ") else G._adj
        self._nodes_nbrs = self._adjframe.items

    # Set methods
    def __len__(self):
        return sum(len(nbrs) for n, nbrs in self._nodes_nbrs())

    def __iter__(self):
        for n, nbrs in self._nodes_nbrs():
            for nbr in nbrs:
                yield (n, nbr)

    def __contains__(self, e):
        try:
            u, v = e
            return v in self._adjframe[u]
        except KeyError:
            return False

    # Mapping Methods
    def __getitem__(self, e):
        u, v = e
        return self._adjframe[u][v]

    # EdgeDataView methods
    def __call__(self, data=False):
        if data is False:
            return self
        return self.dataview(self, data)

    def data(self, data=True):
        if data is False:
            return self
        return self.dataview(self, data)

    # String Methods
    def __str__(self):
        return str(list(self))

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self)})"


class EdgeView(OutEdgeView):
    
    __slots__ = ()

    dataview = EdgeDataView

    def __len__(self):
        num_nbrs = (len(nbrs) + (n in nbrs) for n, nbrs in self._nodes_nbrs())
        return sum(num_nbrs) // 2

    def __iter__(self):
        seen = {}
        for n, nbrs in self._nodes_nbrs():
            for nbr in list(nbrs):
                if nbr not in seen:
                    yield (n, nbr)
            seen[n] = 1
        del seen

    def __contains__(self, e):
        try:
            u, v = e[:2]
            return v in self._adjframe[u] or u in self._adjframe[v]
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


