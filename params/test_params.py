import pytest

@pytest.fixture
def params():
    params = make_params()
    return params

def test_params(params):
    nbuyers = params['nbuyers']
    nsellers = params['nsellers']

    if params['nnodes'] != nbuyers+nsellers:
        raise ValueError #'population mismatch'
    for i in range(100):
        x = params['g_max']
        if x < nbuyers or x < nsellers:
            raise ValueError# 'empty auction warning'

