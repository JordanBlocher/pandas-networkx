import numpy as np
import networkx as nx

rng = np.random.default_rng()

a = rng.integers(low=0, high=2, size=(10, 10))
print(a)

DG = nx.from_numpy_array(a, create_using=nx.DiGraph)
print(DG)
