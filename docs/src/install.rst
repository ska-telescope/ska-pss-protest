Installing ProTest
==================

A python>=3.10 virtual environment is recommended

Install with pip
----------------

.. code-block:: bash

   pip install --index-url https://artefact.skao.int/repository/pypi-internal/simple --extra-index-url https://pypi.org/simple ska-pss-protest

Verify that protest has successfully installed.

.. code-block:: bash

   protest -h

Install from source
-------------------

Ensure poetry is installed first

.. code-block:: bash

   which poetry

If so, proceed as follows. 

.. code-block:: bash

   git clone --recursive https://gitlab.com/ska-telescope/pss/ska-pss-protest.git
   cd ska-pss-protest
   export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
   poetry install --without dev

If you are planning to contribute to ProTest, clone as above and then run 

.. code-block:: bash

   poetry install

Start virtual environment

.. code-block::  bash

   poetry shell

Verify that protest has successfully installed.

.. code-block:: bash

   protest -h

If required, you can verify the install further by executing the unit tests

.. code-block:: bash

    make python-test

