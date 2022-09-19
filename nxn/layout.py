from networkx.utils import np_random_state
from .nxnode import nxNode
from .convert import to_numpy_array
import networkx as nx

def _process_params(G, center, dim):
    # Some boilerplate code.
    import numpy as np

    if not isinstance(G, nxNode):
        empty_node = nxNode()
        for node in G.nodes(data=True):
            empty_node.add_node(node)
        G = empty_node

    if center is None:
        center = np.zeros(dim)
    else:
        center = np.asarray(center)

    if len(center) != dim:
        msg = "length of center coordinates must match dimension of layout"
        raise ValueError(msg)

    return G, center



def spectral_layout(G, weight="capacity", scale=1, center=None, dim=3):
    # handle some special cases that break the eigensolvers
    import numpy as np

    G, center = _process_params(G, center, dim)

    if len(G) <= 2:
        if len(G) == 0:
            pos = np.array([])
        elif len(G) == 1:
            pos = np.array([center])
        else:
            pos = np.array([np.zeros(dim), np.array(center) * 2.0])
        return dict(zip(G, pos))
    '''
    try:
        # Sparse matrix
        if len(G) < 500:  # dense solver is faster for small nodes
            raise ValueError
        A = nx.to_scipy_sparse_array(G, weight=weight, dtype="d")
        pos = _sparse_spectral(A, dim)
    except (ImportError, ValueError):
        # Dense matrix
        A = nx.to_numpy_array(G, weight=weight)
        pos = _spectral(A, dim)
    '''
    A = to_numpy_array(G, weight=weight)
    pos = _spectral(A, dim)
    #pos = rescale_layout(pos, scale=scale) + center
    pos = dict(zip(G, pos))
    return pos


def _spectral(A, dim=2):
    # Input adjacency matrix A
    # Uses dense eigenvalue solver from numpy
    import numpy as np

    try:
        nnodes, _ = A.shape
    except AttributeError as err:
        msg = "spectral() takes an adjacency matrix as input"
        raise 

    # form Laplacian matrix where D is diagonal of degrees
    D = np.identity(nnodes, dtype=A.dtype) * np.sum(A, axis=1)
    L = D - A

    eigenvalues, eigenvectors = np.linalg.eig(L)
    # sort and keep smallest nonzero
    index = np.argsort(eigenvalues)[1 : dim + 1]  # 0 index is zero eigenvalue
    return np.real(eigenvectors[:, index])



