Help on function __getitem__ in module networkx.classes.graph:

____ggeettiitteemm____(self, n)
    Returns a dict of neighbors of node n.  Use: 'G[n]'.
    
    Parameters
    ----------
    n : node
       A node in the graph.
    
    Returns
    -------
    adj_dict : dictionary
       The adjacency dictionary for nodes connected to n.
    
    Notes
    -----
    G[n] is the same as G.adj[n] and similar to G.neighbors(n)
    (which is an iterator over G.adj[n])
    
    Examples
    --------
    >>> G = nx.path_graph(4)  # or DiGraph, MultiGraph, MultiDiGraph, etc
    >>> G[0]
    AtlasView({1: {}})
