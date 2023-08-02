"""
Fixtures defined here can be used by any test in the
protest package without the need to import them.
pytest will automatically discover them.
"""


def pytest_addoption(parser):
    """
    Add command line options for pytest
    """
    parser.addoption("--path", action="store", default=None)

@pytest.fixture(scope="session")
def get_vector():
    """
    Uses requester class to obtain test vector.
    """
    vector = VectorPull()
    vector.from_name(
        "SPS-MID_747e95f_0.2_0.0002_2950.0_0.0_Gaussian_50.0_123123123.fil"
    )
    yield vector
