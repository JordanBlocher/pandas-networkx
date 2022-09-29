import pytest 

@pytest.fixture
def params():
    params = make_params()
    return params

@pytest.fixture
def sim(): 
    sim = MarketSim(make_params)
    return sim


