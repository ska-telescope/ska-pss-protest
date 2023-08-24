ProTest - The PSS Product Testing Framework
===========================================

This repository is the home of ProTest - A suite of high-level tests and supporting libraries for testing the SKA Pulsar Searching Sub-system (PSS).

Documentation
-------------

The documentation for this project, including how to get started with it, can be found in the `docs` directory.


Installing ProTest for development
----------------------------------

Fuller installation instructions for both users and developers of ProTest can be found in `docs`.

In brief, to develop ProTest code, it is recommended a virtual environment providing python>=3.6 is used. Once this is created and activated, run

        git clone --recursive http://gitlab.com/ska-telescope/pss/ska-pss-protest.git

        cd ska-pss-protest

        pip install .[dev] --no-cache-dir

This will install ProTest and all of its project dependencies. Verify the installation by running the unit tests (this can take some time)

        make python-test
