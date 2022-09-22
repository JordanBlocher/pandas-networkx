import pytest 
from params import make_params

@pytest.fixture
def params():
    params = make_params()
    return params

def sim(): 
    sim = MarketSim(make_params)
    return sim


