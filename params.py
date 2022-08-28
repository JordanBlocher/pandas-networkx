import random 
from termcolor import colored
import os

OPTION = False
NOISE = True

ROUNDS = 2
ROW_DELAY=.0001

BUYER_FACTOR = random.uniform(.5, .8)
SELLER_FACTOR = random.uniform(1.2, 1.5)

INCREASE_MAX = 1
INCREASE_MIN = .9
DECREASE_MAX = 0.9
DECREASE_MIN = 0.8

NBUYERS = 15
MSELLERS = 7
MAX_NETWORK_SIZE = 24

LOW = .2 #Note: try negative values
HIGH = 1.2

MINGROUPSIZE = 2

INCREASE_MAX = 1
INCREASE_MIN = .1
DECREASE_MAX = 1
DECREASE_MIN = .1

MAX_PRICE = 15
MAX_QUANTITY = 10

SELLERS= [m for m in range(MSELLERS)]
BUYERS = [n for n in range(NBUYERS)]
SHUFFLED_SELLERS = random.shuffle(SELLERS)
SHUFFLED_BUYERS = random.shuffle(BUYERS)
RANDOM_BUYERS = random.sample(BUYERS, random.randint(MINGROUPSIZE,NBUYERS))
RANDOM_SELLERS = random.sample(SELLERS, random.randint(2,MSELLERS))

# randomly shuffle a list
def SHUFFLE(x):
    y = [n for n in range(len(x))]
    random.shuffle(y)
    return [x[z] for z in y]

MINGROUPSIZE = 2
MAXGROUPSIZE = 3
# randomly sample from a list 
def RANDOM(x):
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



