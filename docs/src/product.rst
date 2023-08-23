Writing new product tests
=========================

Product tests can be written in any form that is understandable and executable by `pytest <http://www.pytest.org>`_. The current preferred approach is to adopt `pytest-bdd <http://pypi.org/project/pytest-bdd>`_. This is a pytest plugin which faciliates the use of the `Gherkin <https://cucumber.io/docs/gherkin/reference/>`_ standard to provide natural language descriptions of product tests. For general guidance for working with BDD tests for SKA projects see `this link <https://developer.skao.int/en/latest/tools/bdd-test-context.html>`_. 

The first step in the development of a product test is to encode the behaviour that we wish to test, using the Gherkin format, into a **feature file**. These files should be placed in the `src/ska-pss-protest/features <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/tree/main/src/ska_pss_protest/features?ref_type=heads>`_ directory, where currently implemented examples can be found. Tests should be marked on the first line using as many markers as are required to describe the test type. For example, a product test which executes a SPS pipeline which requires cuda would be tagged as follows:

.. code-block:: bash

   @product @cuda @sps

A list of valid markers can be found in `pytest.ini <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/blob/main/src/ska_pss_protest/pytest.ini>`_. New markers may be declared in this file as required.

The test itself should be written in a separate file in `src/ska-pss-protest <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/tree/main/src/ska_pss_protest?ref_type=heads>`_. In order for the test to be discovered by ProTest, the file name must be in the form **test_<some_description>.py**. Should any new naming conventions be required, these too must be declared in pytest.ini.

To import the required BDD functionality required to write the test, import the following.

.. code-block:: bash

    import pytest
    from pytest_bdd import given, parsers, scenarios, then, when

To import ProTest, do

.. code-block:: bash

    import ska_pss_protest

The test must then be linked to the feature file that was written in the previous step using the **scenarios** method as follows:

.. code-block:: bash

    scenarios("path/to/feature/ticket.feature")

Following this, each Gherkin step described in the feature ticket can be implemented as a test function. An example of the first *given* step might look like this...

.. code-block:: bash

    @given(parsers.parse("Some initial condition"))
    def some_function():
         """
         Write test code
         """

As variables cannot automatically be passed between test stages (i.e., a variable declared in the *given* function cannot be accessed in any other functions), it is useful to define a context *fixture* that contains a dictionary of variables we wish to pass around the different stages, e.g.,

.. code-block:: bash

    @pytest.fixture(scope="function")
    def context():
        """
        Return dictionary containing variables
        to be shared between test stages
        """
        return {}

This dictionary can then be accessed for the purpose of added or extracting shared variables in the function declaration of the step that wishes to use it, for example,

.. code-block:: bash

    @given(parsers.parse("Some initial condition"))
    def some_function(context):
         """
         shared_variable = context["<key>"] # access existing variable

         context["<key>"] = new_variable # Create a new shared variable
         """

Accessing command line arguments
--------------------------------

ProTest allows a number of command line arguments to provide inputs that should be shared amongst all tests that it will execute. For example, to instruct ProTest to use a set of locally stored test vectors, the user would run,


.. code-block:: bash

    protest --cache <path/to/cache/dir> .....

ProTest passes these to the tests, where required, via `conftest.py <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/blob/main/src/ska_pss_protest/conftest.py>`_  which provides a pytestconfig fixture that contains the value of the argument. This is passed to a test function in the same way as the fixture described above. For example, to access the cache directory that we pass in at the command line, we would write...


.. code-block:: bash

    @given(parsers.parse("Some initial condition"))
    def some_function(pytestconfig):
         """
         cache_dir = pytestconfig.getoption("cache")
         """

Test execution
--------------

Tests can be executed as part of test development, assuming no default parameters are overridden (i.e., that the command line arguments are set to their default values, see *conftest.py*) simply by running


.. code-block:: bash

    pytest /path/to/test.py

but to ensure that they run as part of ProTest, it's safest to update your local install of ProTest, using pip, to include your new tests.  From the package root directory, run


.. code-block:: bash

    pip install . --upgrade

and then ProTest can be executed in the usual way


.. code-block:: bash

    protest -m <marker> --cache </path/to/cache> --path </path/to/cheetah/build> --outdir </path/to/output/directory>

Detailed instruction on how to run ProTest product tests can be found in :doc:`run`
