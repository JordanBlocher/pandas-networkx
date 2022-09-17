import pytest

@pytest.fixture
def auction():
    auction = Auction()
    auction.make_params = make_params
    auction.make_graph()
    return auction

@pytest.fixture
def params():
    params = make_params()
    return params


def test_rsample(params):
    z = reversed(range(2,params['nnodes']))
    for n in z: 
        x = range(2,n)
        try:
            u = rsample(x, params['g_max'])
        except ValueError:
            raise 'distribution too small'
    x = range(2,params['nnodes'])
    z = range(2,params['nnodes'])
    for n in z: 
        try:
            u = rsample(x, n)
        except ValueError:
            raise 'g_max too big'
    for n in z: 
        x = range(n,params['nnodes'])
        try:
            u = rsample(x, params['g_max'])
        except ValueError:
            raise 'g_max too big'
 
    return 0
 

def test_add_node(auction, params):
 
    buyer = Node(params['buyer'])
    try: 
        auction.add_node(buyer)
    except ValueError: 
        raise 'add node to node failed'



