import random
import numpy as np
import networkx as nx
import pandas as pd

import itertools
import warnings
from collections import defaultdict

from networkx.utils import not_implemented_for

def to_numpy_array(
    G,
    dtype=None,
    weight="capacity",
    nonedge=0.0,
):
    import numpy as np

    nodelist = list(G)
    nlen = len(nodelist)

    # Input validation
    nodeset = set(nodelist)
    if nodeset - set(G):
        raise "Nodes {nodeset - set(G)} in nodelist is not in G"
    if len(nodeset) < nlen:
        raise "nodelist contains duplicates."

    A = np.full((nlen, nlen), fill_value=nonedge, dtype=dtype)

    # Corner cases: empty nodelist or graph without any edges
    if nlen == 0 or len(G._adj.index) == 0:
        return A

    # If dtype is structured and weight is None, use dtype field names as
    # edge attributes
    edge_attrs = None  # Only single edge attribute by default
    if A.dtype.names:
        if weight is None:
            edge_attrs = dtype.names
        else:
            raise ValueError

    # Map nodes to row/col in matrix
    idx = dict(zip(nodelist, range(nlen)))
    #if len(nodelist) < len(G):
    #    G = G.subgraph(nodelist).copy()

    # Collect all edge weights and reduce with `multigraph_weights`
    i, j, wts = [], [], []

    # Special branch: multi-attr adjacency from structured dtypes
    if edge_attrs:

        # Extract edges with all data
        for u, v, data in G.edge_map():
            i.append(idx[u])
            j.append(idx[v])
            wts.append(data)
        # Map each attribute to the appropriate named field in the
        # structured dtype
        for attr in edge_attrs:
            attr_data = [wt.get(attr) for wt in wts]
            A[attr][i, j] = attr_data
            A[attr][j, i] = attr_data
        return A
    #print(G.edge_map(weight=weight))
    for u, v, wt in G.edge_map(weight=weight):
        i.append(idx[u])
        j.append(idx[v])
        wts.append(wt)

    # Set array values with advanced indexing
    A[i, j] = wts
    A[j, i] = wts

    return A



def from_pandas_edgelist(
    df,
    source="source",
    target="target",
    edge_attr=None,
    create_using=None,
    edge_key=None,
):
    g = nx.empty_graph(0, create_using)

    if edge_attr is None:
        g.add_edges_from(zip(df[source], df[target]))
        return g

    reserved_columns = [source, target]

    # Additional columns requested
    attr_col_headings = []
    attribute_data = []
    if edge_attr is True:
        attr_col_headings = [c for c in df.columns if c not in reserved_columns]
    elif isinstance(edge_attr, (list, tuple)):
        attr_col_headings = edge_attr
    else:
        attr_col_headings = [edge_attr]
    if len(attr_col_headings) == 0:
        raise nx.NetworkXError(
            f"Invalid edge_attr argument: No columns found with name: {attr_col_headings}"
        )

    try:
        attribute_data = zip(*[df[col] for col in attr_col_headings])
    except (KeyError, TypeError) as err:
        msg = f"Invalid edge_attr argument: {edge_attr}"
        raise nx.NetworkXError(msg) from err

    if g.is_multigraph():
        # => append the edge keys from the df to the bundled data
        if edge_key is not None:
            try:
                multigraph_edge_keys = df[edge_key]
                attribute_data = zip(attribute_data, multigraph_edge_keys)
            except (KeyError, TypeError) as err:
                msg = f"Invalid edge_key argument: {edge_key}"
                raise nx.NetworkXError(msg) from err

        for s, t, attrs in zip(df[source], df[target], attribute_data):
            if edge_key is not None:
                attrs, multigraph_edge_key = attrs
                key = g.add_edge(s, t, key=multigraph_edge_key)
            else:
                key = g.add_edge(s, t)

            g[s][t][key].update(zip(attr_col_headings, attrs))
    else:
        for s, t, attrs in zip(df[source], df[target], attribute_data):
            g.add_edge(s, t)
            g[s][t].update(zip(attr_col_headings, attrs))

    return g



def from_pandas_adjacency(df, create_using=None):
    try:
        df = df[df.index]
    except Exception as err:
        missing = list(set(df.index).difference(set(df.columns)))
        msg = f"{missing} not in columns"
        raise nx.NetworkXError("Columns must match Indices.", msg) from err

    A = df.values
    G = from_numpy_array(A, create_using=create_using)

    nx.relabel.relabel_nodes(G, dict(enumerate(df.columns)), copy=False)
    return G

def make_frame(nxnode, source="buyer", target="seller", nodelist=None, dtype=None):
    if nodelist is None:
        edgelist = nxnode.edges(data=True)
    else:
        edgelist = nxnode.edges(nodelist, data=True)
    source_nodes = [s for s, _, _ in edgelist]
    target_nodes = [t for _, t, _ in edgelist]

    all_attrs = set().union(*(d.keys() for _, _, d in edgelist))
    nan = float("nan")
    edge_attr = {k: [d.get(k, nan) for _, _, d in edgelist] for k in all_attrs}
    edgelistframe = {source: source_nodes, target: target_nodes}

    edgelistframe.update(edge_attr)
    return pd.DataFrame(edgelistframe, dtype=dtype)


def make_frame_from_dict(nxnode, nodelist=None, dtype=None):
    dod = {}
    if nodelist is None:
        if edge_data is None:
            for u, nbrdict in nxnode.adjacency():
                dod[u] = nbrdict.copy()
        else:  # edge_data is not None
            for u, nbrdict in nxnode.adjacency():
                dod[u] = dod.fromkeys(nbrdict, edge_data)
    else:  # nodelist is not None
        if edge_data is None:
            for u in nodelist:
                dod[u] = {}
                for v, data in ((v, data) for v, data in nxnode[u].items() if v in nodelist):
                    dod[u][v] = data
        else:  # nodelist and edge_data are not None
            for u in nodelist:
                dod[u] = {}
                for v in (v for v in G[u] if v in nodelist):
                    dod[u][v] = edge_data
    return pd.DataFrame(dod, dtype=dtype)


