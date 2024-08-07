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

Ensure `poetry is installed <https://python-poetry.org/docs/#installation>`_ first

.. code-block:: bash

   which poetry

If so, proceed as follows. 

.. code-block:: bash

   git clone --recursive https://gitlab.com/ska-telescope/pss/ska-pss-protest.git
   cd ska-pss-protest
   export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
   poetry install --without dev


Install from source (for developers)
------------------------------------

If you are planning to contribute to ProTest, run the git clone command above. If you have an existing clone, you can check whether you have the correct submodules (made available by --recursive) by running

.. code-block:: bash

   git submodule status

and if nothing is returned, use

.. code-block:: bash

   git submodule init
   git submodule update

To install a developer version of ProTest, run

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

