Contributing to ProTest
=======================

ProTest comprises a number of libraries that are intended to facilitate the development of product tests. The libraries are located at `src/ska-pss-protest <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/tree/main/src/ska_pss_protest?ref_type=heads>`_ and each is repsonsible for a different piece of functionality that may be required by a test. Examples include

* The handling of test vectors - how they are provisioned from a remote server, and stored/accessed in the local cache.
* The preparation and execution of cheetah with all of its required input
* The extraction of header parameters from filterbank files
* The verification of candidate filterbanks
* The verification of candidate metadata

As ProTest (and cheetah) grows, more and more libraries will be required to verify PSS data products. New libraries can be added to ProTest by simply adding them to `src/ska-pss-protest <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/tree/main/src/ska_pss_protest?ref_type=heads>`_. New libraries and the classes within them should be added to `init.py <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/blob/main/src/ska_pss_protest/__init__.py?ref_type=heads>`_ as follows

.. code-block:: bash

    from ska_pss_protest.<new_library> import <new_class_a>, <new_class_b>

There are no specific naming conventions currently required of new libraries but they should at least succinctly describe what the library does. Each library must naturally be accompanied by a test of unit tests and these should be placed in `tests/ <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/tree/main/tests?ref_type=heads>`_. Like product tests, unit test are tagged with markers which describe the library that they are testing. This allows the developer to execute their own new tests during development of their library. New markers for unit tests should be declared in `pytest.ini <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/blob/main/pytest.ini?ref_type=heads>`_. To execute unit tests of a specific library, one can run

.. code-block:: bash

    pytest -m <marker> tests/

or to run all tests


.. code-block:: bash

    make python-test
