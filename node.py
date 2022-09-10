import random
import numpy as np
import networkx as nx
import seaborn as sns
np.set_printoptions(precision=2)
    

class Node:
    
    ids = []
    #factor = np.random.uniform(0.09, 0.99, size=200)
    id = 0

    def __init__(self, params):
        rng = nx.utils.create_random_state()
        if len(Node.ids) > 1:
            self.id = rng.choice(Node.ids, replace=False)
        else:
            Node.id +=1
            self.id = Node.id
        self.demand = rng.randint(1, params['max_quantity']) * params['flow']
        self.private_value = None
        key = list(sns.palettes.xkcd_rgb.keys())[self.id] 
 
        self.color = sns.palettes.xkcd_rgb[key]
        self.price = round(params['init_factor'] * params['price'][self.id],2)
        if self.demand < 0:
            self.type = 'buyer'
        else:
            self.type = 'seller'

    def filter(self, node):
        return self.type ==  node.type

    def inv_filter(self, node):
        return self.type !=  node.type

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


