import pytest 

@pytest.fixture
def params():
    params = make_params()
    return params

def sim(): 
    sim = MarketSim(make_params)
    return sim


def test_params():
    nbuyers = params['nbuyers']
    nsellers = params['nsellers']

    if params['nnodes'] != nbuyers+nsellers:
        raise ValueError #'population mismatch'
    for i in range(100):
        x = params['g_max']
        if x < nbuyers or x < nsellers:
            raise ValueError# 'empty auction warning'

