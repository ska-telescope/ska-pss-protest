Installing ProTest
==================

A python>=3.6 virtual environment is recommended

Install with pip
----------------

.. code-block:: bash

   pip install --index-url https://artefact.skao.int/repository/pypi-internal/simple --extra-index-url https://pypi.org/simple ska-pss-protest

Verify that protest has successfully installed.

.. code-block:: bash

   protest -h

Install from source
-------------------

.. code-block:: bash

   git clone --recursive https://gitlab.com/ska-telescope/pss/ska-pss-protest.git
   pip install .

If you are planning to contribute to ProTest, install from source as above and then run 

.. code-block:: bash

   pip install .[dev]

Verify that protest has successfully installed.

.. code-block:: bash

   protest -h

If required, you can verify the install further by executing the unit tests

.. code-block:: bash

    make python-test

