import random
import numpy as np
import networkx as nx
import pandas as pd

from collections.abc import Collection, Generator, Iterator
from collections.abc import Mapping

from nx import AdjView, EdgeView, NodeView


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


