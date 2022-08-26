import random 
from termcolor import colored
import os

NCURSES = False
WEIGHTED_EDGES = True
PRIVATE_VALUE = False

PIPE_PATH = "/home/frags/pipe"
if not os.path.exists(PIPE_PATH):
    os.mkfifo(PIPE_PATH)

ROUNDS = 20
ROW_DELAY=.0001

BUYER_FACTOR = .5
SELLER_FACTOR = 1.5

INCREASE_MAX = 1
INCREASE_MIN = .9
DECREASE_MAX = 0.9
DECREASE_MIN = 0.8

NBUYERS = 25
MSELLERS = 11
MAX_NETWORK_SIZE = 75

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
# randomly sample from a list 
def RANDOM(x):
    y = [n for n in range(len(x))]
    u = random.sample(y, random.randint(MINGROUPSIZE,len(x)))
    return [x[z] for z in u]

def SAMPLE(x, m):
    y = [n for n in range(len(x))]
    u = random.sample(y, m)
    return [x[z] for z in u]

def RD(x):
    return round(x, 2)

def cprintnode(node, end):
    print(colored(node, node.color), node.price, node.demand, end=end)



