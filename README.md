        html.Div(
            [
                dcc.RadioItems(
                            ['Noise'], 
                            id='radio-items', 
                            inline=True,
                            value=params['noise']
                            )
            ],
          style={'display': 'grid', 'grid-template-columns': '10% 35% 10% 35%'}
        ),
        html.Div(
            [
                html.Label('nbuyers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-buyers',
                    min=0,
                    max=100,
                    value=params['nbuyers'], 
                    tooltip={'placement': 'bottom'}
                ),
                html.Label('nsellers', style={'text-align': 'right'}),
                dcc.Slider(
                    id='n-sellers',
                    min=0,
                    max=100,
                    value=params['nsellers'],
                    tooltip={'placement': 'bottom'}
                )
            ],
            style={'display': 'grid', 'grid-template-columns': '10% 35% 10% 35%'}
        ),
        html.Div(id='hidden-div')  
@app.callback(
    Output('hidden-div', 'children'),[
    Input('n-buyers', 'value'), Input('n-sellers', 'value'),
    Input('radio-items', 'value')
    ]
)
def update_output(n, m, x):
    global nbuyers, nsellers, noise
    nbuyers = n
    nsellers = m
    noise = x



def subgraph_view(G, filter_node=no_filter, filter_edge=no_filter):
    """View of `G` applying a filter on nodes and edges.

    `subgraph_view` provides a read-only view of the input graph that excludes
    nodes and edges based on the outcome of two filter functions `filter_node`
    and `filter_edge`.

    The `filter_node` function takes one argument --- the node --- and returns
    `True` if the node should be included in the subgraph, and `False` if it
    should not be included.

    The `filter_edge` function takes two (or three arguments if `G` is a
    multi-graph) --- the nodes describing an edge, plus the edge-key if
    parallel edges are possible --- and returns `True` if the edge should be
    included in the subgraph, and `False` if it should not be included.

    Both node and edge filter functions are called on graph elements as they
    are queried, meaning there is no up-front cost to creating the view.

    Parameters
    ----------
    G : networkx.Graph
        A directed/undirected graph/multigraph

    filter_node : callable, optional
        A function taking a node as input, which returns `True` if the node
        should appear in the view.

    filter_edge : callable, optional
        A function taking as input the two nodes describing an edge (plus the
        edge-key if `G` is a multi-graph), which returns `True` if the edge
        should appear in the view.

    Returns
    -------
    graph : networkx.Graph
        A read-only graph view of the input graph.

    Examples
    --------
    >>> G = nx.path_graph(6)

    Filter functions operate on the node, and return `True` if the node should
    appear in the view:

    >>> def filter_node(n1):
    ...     return n1 != 5
    ...
    >>> view = nx.subgraph_view(G, filter_node=filter_node)
    >>> view.nodes()
    NodeView((0, 1, 2, 3, 4))

    We can use a closure pattern to filter graph elements based on additional
    data --- for example, filtering on edge data attached to the graph:

    >>> G[3][4]["cross_me"] = False
    >>> def filter_edge(n1, n2):
    ...     return G[n1][n2].get("cross_me", True)
    ...
    >>> view = nx.subgraph_view(G, filter_edge=filter_edge)
    >>> view.edges()
    EdgeView([(0, 1), (1, 2), (2, 3), (4, 5)])

    >>> view = nx.subgraph_view(G, filter_node=filter_node, filter_edge=filter_edge,)
    >>> view.nodes()
    NodeView((0, 1, 2, 3, 4))
    >>> view.edges()
    EdgeView([(0, 1), (1, 2), (2, 3)])
    """
    newG = nx.freeze(G.__class__())
    newG._NODE_OK = filter_node
    newG._EDGE_OK = filter_edge

    # create view by assigning attributes from G
    newG._graph = G
    newG.graph = G.graph

    newG._node = FilterAtlas(G._node, filter_node)
    if G.is_multigraph():
        Adj = FilterMultiAdjacency

        def reverse_edge(u, v, k=None):
            return filter_edge(v, u, k)

    else:
        Adj = FilterAdjacency

        def reverse_edge(u, v, k=None):
            return filter_edge(v, u)

    if G.is_directed():
        newG._succ = Adj(G._succ, filter_node, filter_edge)
        newG._pred = Adj(G._pred, filter_node, reverse_edge)
        # newG._adj is synced with _succ
    else:
        newG._adj = Adj(G._adj, filter_node, filter_edge)
    return newG


