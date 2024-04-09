"""
Fixtures defined here can be used by any test in the
protest package without the need to import them.
pytest will automatically discover them.
"""
import logging
import pytest
import shutil
import tempfile
import os

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

def pytest_addoption(parser):
    """
    Add command line options for pytest
    """
    parser.addoption("--path", action="store", default=None)
    parser.addoption("--cache", action="store", default=None)
    parser.addoption("--outdir", action="store", default="/tmp")
    parser.addoption("--keep", action="store_true")

@pytest.fixture(scope="function")
def teardown():
    """
    Fixture to remove the directory into which
    data products from a test set are written
    """
    def _data_rm(directory):
        """
        Private fixture parameteriser
        """
        shutil.rmtree(directory)

    return _data_rm

@pytest.fixture(scope="function")
def outdir():
    """
    Fixture to set the output directory into which
    data products for a test set are written
    """
    def _outdir(parent):
        """
        Private fixture parameteriser
        """
        if not os.path.isdir(parent):
            os.mkdir(parent)
        this_outdir = tempfile.mkdtemp(dir=parent)
        return this_outdir

    return _outdir
        
@pytest.fixture(scope="function")
def conf():
    """
    Fixture to name the Cheetah config file
    """
    def _confpath(parent):
        """
        Private fixture parameteriser
        """
        if os.path.isdir(parent):
            this_confpath = os.path.join(parent, "config_" + next(tempfile._get_candidate_names()))
            return this_confpath
        raise FileNotFoundError("Directory {} not found".format(parent))

    return _confpath

@pytest.fixture(scope="session", autouse=True)
def cleanup(pytestconfig):
    """
    Remove parent directory of test result data. 
    The teardown() fixture above removes the data
    directories containing results for individual
    test sets. In a given run of ProTest, all of those
    data directorys are placed in a single parent directory. 
    This fixture removes the parent directory if the --keep
    option is not passed to ProTest.
    """
    yield 
    result_dir = pytestconfig.getoption("outdir")
    if not pytestconfig.getoption("keep"):
        logging.info("Removing directory {}".format(result_dir))
        shutil.rmtree(result_dir)
