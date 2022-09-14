import random
import numpy as np
import networkx as nx
import seaborn as sns
import inspect
import pandas as pd
np.set_printoptions(precision=2)

import networkx.convert as convert


class nxNode(nx.Graph):
    
    id = 0
    node_frame_factory = pd.DataFrame
    node_attr_frame_factory = pd.DataFrame
    edge_attr_frame_factory = pd.DataFrame
    graph_attr_frame_factory = pd.DataFrame
    adjlist_outer_frame_factory = pd.DataFrame
    adjlist_inner_frame_factory = pd.DataFrame
   

    def __init__(self, incoming_graph_data=None, **attr):
        nxNode.id += 1
        self.id = nxNode.id
        self.graph = self.graph_attr_frame_factory()  
        self._node = self.node_frame_factory()  
        self._adj = self.adjlist_outer_frame_factory()  
        if incoming_graph_data is not None:
            convert.to_networkx_graph(incoming_graph_data, create_using=self)
        self.graph.update(attr)


    def make_frame(self, source="buyer", target="seller", nodelist=None, dtype=nxNode):
        if nodelist is None:
            edgelist = self.edges(data=True)
        else:
            edgelist = self.edges(nodelist, data=True)
        source_nodes = [s for s, _, _ in edgelist]
        target_nodes = [t for _, t, _ in edgelist]

        all_attrs = set().union(*(d.keys() for _, _, d in edgelist))
        nan = float("nan")
        edge_attr = {k: [d.get(k, nan) for _, _, d in edgelist] for k in all_attrs}
        edgelistdict = {source: source_nodes, target: target_nodes}

        edgelistdict.update(edge_attr)
        return pd.DataFrame(edgelistdict, dtype=dtype)


    def make_frame_from_dict(self, nodelist=None, dtype=nxNode):
        dod = {}
        if nodelist is None:
            if edge_data is None:
                for u, nbrdict in self.adjacency():
                    dod[u] = nbrdict.copy()
            else:  # edge_data is not None
                for u, nbrdict in self.adjacency():
                    dod[u] = dod.fromkeys(nbrdict, edge_data)
        else:  # nodelist is not None
            if edge_data is None:
                for u in nodelist:
                    dod[u] = {}
                    for v, data in ((v, data) for v, data in self[u].items() if v in nodelist):
                        dod[u][v] = data
            else:  # nodelist and edge_data are not None
                for u in nodelist:
                    dod[u] = {}
                    for v in (v for v in G[u] if v in nodelist):
                        dod[u][v] = edge_data
        return pd.DataFrame(dod, dtype=dtype)


    
    def add_node(self, node, **attr):
        if node_for_adding not in self._node:
            if node_for_adding is None:
                raise ValueError("None cannot be a node")
            self._adj[node_for_adding] = self.adjlist_inner_frame_factory()
            attr_frame = self._node[node_for_adding] = self.node_attr_frame_factory()
            attr_frame.update(attr)
        else:  # update attr even if node already exists
            self._node[node_for_adding].update(attr)

    def edges(self):
        return EdgeView(self)

    def get_edge_data(self, u, v):
        try:
            return self._adj[u][v]
        except KeyError:
            return default
    
    def __str__(self):
        stack = inspect.stack()
        #for frame in stack:
        #    print('\n',frame.filename, frame.function)
        if stack[1].function == '<dictcomp>':
            return  str(self.__dict__())
        elif stack[1].function == 'plot':
            return  str(self.__dict__())
        elif stack[2].function == 'plot':
            return  str(self.__dict__())
        else:
            return str(self.id)
            
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

    def nodes(self):
        return NodeView(self)
    
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

    def __repr__(self):
        stack = inspect.stack()
        #for frame in stack:
        #    print('\n',frame.filename, frame.function)
        if stack[-1].filename == '<stdin>':
            return str(self.id)
        elif stack[1].function == '__str__':
            return str(self.id)
        else:
            return self

    def __index__(self):
        return int(self.id)
   
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id


