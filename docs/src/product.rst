Writing new product tests
=========================

Product tests can be written in any form that is understandable and executable by `pytest <http://www.pytest.org>`_. The current preferred approach is to adopt `pytest-bdd <http://pypi.org/project/pytest-bdd>`_. This is a pytest plugin which faciliates the use of the `Gherkin <https://cucumber.io/docs/gherkin/reference/>`_ standard to provide natural language descriptions of product tests. For general guidance for working with BDD tests for SKA projects see `this link <https://developer.skao.int/en/latest/tools/bdd-test-context.html>`_. 

The first step in the development of a product test is to encode the behaviour that we wish to test, using the Gherkin format, into a **feature file**. These files should be placed in the `src/ska-pss-protest/features <https://gitlab.com/ska-telescope/pss/ska-pss-protest/-/tree/main/src/ska_pss_protest/features?ref_type=heads>`_ directory, where currently implemeted examples can be found. 
