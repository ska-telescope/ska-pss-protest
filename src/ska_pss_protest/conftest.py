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
    parser.addoption("--cache", action="store", default=None)
    parser.addoption("--outdir", action="store", default="/tmp")
