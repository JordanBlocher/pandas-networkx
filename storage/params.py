import random 
from termcolor import colored
import os

    
params = dict(
    buyer = dict(
                n = 25,
                nmax = 100,
                factor = random.uniform(.5, .8),
                max_price = 15,
                max_quantity = 10,
                flow = -1
                ),
    seller = dict(
                m = 15,
                mmax = 80,
                factor = random.uniform(1.2, 1.5),
                max_price = 15,
                max_quantity = 10,
                flow = 1
                ),
    option = False,
    noise = True,
    rounds = 25,
    max_network_size = 47,
    mingroupsize = 2,
    maxgroupsize = 12,
    )

# randomly shuffle a list
def SHUFFLE(x):
    y = [n for n in range(len(x))]
    random.shuffle(y)
    return [x[z] for z in y]

# randomly sample from a list 
def RANDOM(x,MINGROUPSIZE,MAXGROUPSIZE):
    y = [n for n in range(len(x))]
    u = random.sample(y, random.randint(MINGROUPSIZE,MAXGROUPSIZE))
    return [x[z] for z in u]

def SAMPLE(x, m):
    y = [n for n in range(len(x))]
    u = random.sample(y, m)
    return [x[z] for z in u]

def RD(x):
    return round(x, 2)

def cprintnode(node, end):
    print(colored(node, node.color), node.price, node.demand, end=end)



INCREASE_MAX = 1
INCREASE_MIN = .9
DECREASE_MAX = 0.9
DECREASE_MIN = 0.8

LOW = .2 #Note: try negative values
HIGH = 1.2

INCREASE_MAX = 1
INCREASE_MIN = .1
DECREASE_MAX = 1
DECREASE_MIN = .1


