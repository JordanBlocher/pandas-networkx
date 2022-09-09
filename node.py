import random
import numpy as np
import networkx as nx
import seaborn as sns
np.set_printoptions(precision=2)
    
MAX_NETWORK_SIZE = 200


class Node:
    
    ids = [n for n in reversed(range(1, MAX_NETWORK_SIZE))]
    #factor = np.random.uniform(0.09, 0.99, size=200)
    id = 0

    def __init__(self, params):
        rng = nx.utils.create_random_state()
        self.id = rng.choice(Node.ids, replace=False)
        self.demand = rng.randint(1, params['max_quantity']) * params['flow']
        self.private_value = None
        key = rng.choice(
                    list(sns.palettes.xkcd_rgb.keys())) 
 
        self.color = sns.palettes.xkcd_rgb[key]
        self.price = params['init_factor']

    def filter(self, node):
        return self.type() ==  node.type()

    def inv_filter(self, node):
        return self.type() !=  node.type()

    def type(self):
        if self.demand < 0:
            return 'buyer'
        else:
            return 'seller'
        
    def __repr__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)
     
    def __lt__(self, other):
        return self.id < other.id

    def __le__(self, other):
        return self.id <= other.id

    def __gt__(self, other):
        return self.id > other.id

    def __ge__(self, other):
        return self.id >= other.id


