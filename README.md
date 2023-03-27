# PSS Testing Framework (protest)

## A suite of applications for supporting end-to-end tests of the PSS pipeline

### Testing the PSS pipeline using ProTest

The PSS Product testing framework (ProTest) consists of a set of "product" tests, supported by a number of python-based backend applications, for verifying that the PSS pipeline conforms to SKA requirements. ProTest can be installed and launched on any machine on which python3 is available. A set of unit tests are also including to test the functionality of ProTest itself. The underlying testing framework is pytest.

In order to install ProTest, a ./launch\_protest script is provided which will

* check that a compatible version of python is available
* ensure that a suitable virtual environment exists (under /home/<user>/.venvs/protest)
* install the required python packages using pip
* install the testing framework into the virtual environment's site-packages/ directory
* Activate the ProTest environment
* Run the required tests
* Close the ProTest environment

Tests are broadly divided into two types which can be executed separately by utilising pytest markers. Each test is marked according to its test type, e.g., "unit" (to run ProTest's unit tests) or product (to run the end-to-end product tests). Addtional markers are set according to the particular test set. For example, unit tests which test the functionality of the test vector requester are marked with 'reqtests' and could be called using that marker. Alternatively, to run the full suite of unit tests, one can simple use the 'unit' marker.  A full list of markers can be found in pytest.ini, or by passing "-h" to the launcher scripts.

```bash
./launch_protest -h

Usage is ./launch_protest <test_type> <path to cheetah>
<test_type> options are:'
    'product' (requires <path>)
    'unit'
    'reqtests'
    'parsertests'
    'filtests'
    'pipeline'
    'candtests'
    'all' (requires <path>)
```

To execute all of ProTest's unit tests, we run

```bash
./launch_protest unit
```

which runs all tests marked with "unit" producing the output something like the following (some lines not shown for brevity)

```bash
TEST TYPE: unit is valid
Creating virtual env
Starting virtual env
Upgrading pip
Cache entry deserialization failed, entry ignored
Collecting pip
Installing dependencies
unit/test_candidate.py::SpCclTests::test_non_existent_spccl_dir PASSED                                                                                                                                      [  2%]
unit/test_fil.py::FilterbankTests::test_invalid_parameter PASSED                                                                                                                                            [ 44%]
unit/test_parser.py::ParserTests::test_not_json_exception PASSED                                                                                                                                            [ 53%]
unit/test_requester.py::RequesterTests::test_from_name_with_cache_env PASSED                                                                                                                                [ 61%]
unit/test_runner.py::RunnerTests::test_subprocess_call_to_cheetah_candidate_pipeline PASSED                                                                                                                 [ 95%]
```

All of the unit tests have run and passed. A subset of them (e.g., those which test the candidate parser application) could be executed using

```bash
./launch_protest candtests
```

To run the end-to-end product tests (those which actually launch a PSS pipeline, the path to the directory containing the cheetah "pipelines" directory must be supplied in addition to the test type. This directory is the top level of the build tree which contains sub-directories containing the executables corresponding to the systems under test. Currently these executables are pipelines/cheetah\_pipeline, emulators/cheetah\_emulator and candidate\_pipeline/cheetah\_candidate\_pipeline.

```bash
./launch_protest product /path/to/cheetah/dir
```

which will produce output of the form...

```bash
TEST TYPE: product is valid
Starting virtual env for ProTest
Running PSS product tests
========= test session starts ===============
platform linux -- Python 3.6.8, pytest-7.0.1, pluggy-1.0.0
rootdir: tests, configfile: pytest.ini
plugins: metadata-1.11.0, repeat-0.9.1, mock-3.6.1, html-3.1.1, cov-4.0.0, bdd-5.0.0
collected 50 items / 49 deselected / 1 selected

product/test_sps_emulator.py::test_detecting_fake_single_pulses PASSED                                                                                                                                      [100%]

========= 1 passed, 49 deselected in 92.69s (0:01:32) =============
Tests completed - deactivating PROTEST
```

### Manually installing ProTest

A python3.6 or later, virtualenv is recommended.

Install dependencies

```bash
pip install -r requirements.txt --no-cache-dir
```

Install ProTest

```bash
pip install .
```

Execute unit tests, calling pytest directly. Test markers can be specified using the "-m" flag. 

```bash
pytest -m unit
```

Execute product tests, calling pytest directly. To pass a path to the cheetah build tree, use the "--path=<path\_to\_cheetah>" argument, e.g., 

```bash
pytest -m "product" --path=/home/cheetah_build/cheetah"
```
