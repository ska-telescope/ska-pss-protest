"""
    **************************************************************************
    |                                                                        |
    |               Unit tests for candidate parser                          |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Tests the functionality of the PSS testing framework backend           |
    | application candlist.py. Candlists's purpose is to compare            |
    | candidates detected by the pulsar and single pulse search pipelines    |
    | to known values in order to test their end-to-end functionality        |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    |  pytest -m candlisttests                                               |
    |          <or>                                                          |
    |  make test MARK="candlisttests"                                        |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2024 SKA Observatory                                         |
    |                                                                        |
    |Redistribution and use in source and binary forms, with or without      |
    |modification, are permitted provided that the following conditions are  |
    |met:                                                                    |
    |                                                                        |
    |1. Redistributions of source code must retain the above copyright       |
    |notice,                                                                 |
    |this list of conditions and the following disclaimer.                   |
    |                                                                        |
    |2. Redistributions in binary form must reproduce the above copyright    |
    |notice, this list of conditions and the following disclaimer in the     |
    |documentation and/or other materials provided with the distribution.    |
    |                                                                        |
    |3. Neither the name of the copyright holder nor the names of its        |
    |contributors may be used to endorse or promote products derived from    |
    |this                                                                    |
    |software without specific prior written permission.                     |
    **************************************************************************
"""

import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pytest import mark

from ska_pss_protest import FdasScl, FdasTolBasic, FdasTolDummy, VectorPull

# pylint: disable=R1732,W1514,E1120,W0621

DATA_DIR = os.path.join(
    Path(os.path.abspath(__file__)).parents[1], "tests/data/candidate_lists"
)


@pytest.fixture(scope="function")
def get_vector():
    """
    Uses requester class to obtain test vector
    for header checking.

    Vector is cleared from disk after tests have run.
    """
    vector = VectorPull()
    vector.from_name(
        "SPS-MID_747e95f_0.2_0.2_1.0_0.0_Gaussian_20.0_0000_123123123.fil"
    )
    yield vector


@pytest.fixture(scope="function")
def get_high_dm_vector():
    """
    Uses requester class to obtain test vector
    for header checking.

    Vector is cleared from disk after tests have run.
    """
    vector = VectorPull()
    vector.from_name(
        "SPS-MID_747e95f_0.2_0.0002_1480.0_0.0_Gaussian_50.0_0000_123123123.fil"
    )
    yield vector


@mark.candlisttests
@mark.scltests
@mark.unit
class SclTests:
    """
    Tests of the FDAS candidate metadata file parser(s)
    """

    def test_non_existent_spccl_dir(self):
        """
        Test exception is raised when non-existent
        scl directory is passed to constructor
        """
        scl_dir = "/tmp/random_test_dir/ajd994jfma29"
        with pytest.raises(OSError):
            FdasScl(scl_dir)

    def test_load_detected_candidates(self):
        """
        Test that detected candidates files are loaded correctly.
        A directory containing the detected metadata file is provided
        and the candidate metadata file (.scl) is parsed and the
        contents returned as a Nx5 array, where N is the number of
        candidates and 5 is the number of parameters per candidate.
        """
        # Set up directory containing "detected" candidates file
        scl_dir = os.path.join(DATA_DIR, "scl_1")

        # Instantiate candidate parser, passing directory as args
        # The directory contains a "detected" candidates file which will
        # be loaded into memory and the contents compared to
        # a list of expected candidates (next step)
        candidate = FdasScl(scl_dir)

        # Load in "expected" candidate metadata file
        known_file = os.path.join(DATA_DIR, "scl_1/test_candlist.scl")
        known_cands = pd.read_csv(known_file, sep="\t")
        known_cands.columns = [
            "period",
            "pdot",
            "dm",
            "harmonic",
            "width",
            "sn",
        ]
        known_cands = known_cands.sort_values("sn", ascending=False)

        assert np.all(candidate.cands == known_cands)

    def test_no_candidate_dir(self):
        """
        Tests that the correct exception is
        raised when no candidate directory is
        passed to the constructor.
        """
        with pytest.raises(OSError):
            FdasScl()

    def test_empty_candidate_list(self):
        """
        Tests that the correct exception is raised
        when an empty candidate list is passed to
        the constructor.
        """
        scl_dir = os.path.join(DATA_DIR, "scl_2")

        # Instantiate candidate parser, passing directory as args
        # The directory contains a "detected" candidates file which will
        # be loaded into memory and the contents compared to
        # a list of expected candidates (next step)

        with pytest.raises(EOFError):
            # Pass empty directory to constructor
            FdasScl(scl_dir)

    def test_no_cand_file_extension_in_valid_dir(self):
        """
        Tests that the correct exception is raised if
        a valid directory is passed to the constructor
        but files of a custom extension are not found
        there
        """
        # Create new directory with random name under /tmp
        scl_dir = tempfile.mkdtemp()
        with pytest.raises(IOError):
            # Pass real dir but with random non-existent extension
            FdasScl(scl_dir, "sdfhjs")
        shutil.rmtree(scl_dir)

    def test_wrong_number_of_cand_files(self):
        """
        We expect one candidate file per scan and therefore
        only one metadata file in each directory. This tests
        that the correct exception is raised if more than one
        candidate file is found.
        """
        # Create new directory with random name under /tmp
        scl_dir = tempfile.mkdtemp()

        # Define two candidate metadata file paths
        file1 = os.path.join(scl_dir, "cand1.scl")
        file2 = os.path.join(scl_dir, "cand2.scl")

        with pytest.raises(IOError):
            # Generate empty files in directory
            open(file1, "a").close()
            open(file2, "a").close()
            FdasScl(scl_dir)
        shutil.rmtree(scl_dir)

    def test_from_vector(self):
        """
        Tests that we can extract the correct pulsar
        parameters from a FDAS test vector
        """
        vector_a = "FDAS-HSUM-MID_38d46df_500.0_0.2_1.0_0.0_Gaussian_50.0_0000_123123123.fil"
        vector_b = "FDAS-HSUM-MID_38d46df_500.00115818617536_0.05_1.0_0.0_Gaussian_50.0_0000_123123123.fil"
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "duration": 600,
        }
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = FdasScl(scl_dir)

        period = 1.0 / 500.0 * 1000
        width = 0.2 * period
        candidate.from_vector(vector_a, source_properties)
        assert candidate.expected == [period, 0, 1.0, width, 50.0]

        period = 1.0 / 500.00115818617536 * 1000
        width = 0.05 * period
        candidate.from_vector(vector_b, source_properties)
        assert candidate.expected == [period, 0, 1.0, width, 50.0]
        assert candidate.expected != [period, 0, 2.0, width, 500.0]

    def test_search_using_dummy_ruleset(self):
        """
        Test the dummy search method recovers the one
        candidate that falls within a set of tolerances.
        """
        vector = (
            "FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil"
        )
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "duration": 600,
        }
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = FdasScl(scl_dir)
        candidate.from_vector(vector, source_properties)
        candidate.search_tol("dummy")
        assert candidate.detected is True
        assert candidate.recovered.shape[0] == 1
        true_candidate = [18.5179, 0, 99.7, 9, 2.05754, 463.76]
        true = pd.DataFrame([true_candidate], index=[2])
        true.columns = ["period", "pdot", "dm", "harmonic", "width", "sn"]
        assert np.all(true == candidate.recovered)

    def test_search_using_dummy_ruleset_no_detection(self):
        """
        Test the dummy search method filters all candidates
        """
        vector = (
            "FLDO-MID_336a2a6_48.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil"
        )
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "duration": 600,
        }
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = FdasScl(scl_dir)
        candidate.from_vector(vector, source_properties)
        candidate.search_tol("dummy")
        assert candidate.detected is False
        assert candidate.recovered is None

    def test_dummy_fdas_rules(self):
        """
        Test the dummy tolerance generator
        returns to expected ranges/limits
        """
        tols = FdasTolDummy([1, 1e-15, 100, 100, 100])
        assert tols.period_tol == [0.9, 1.1]
        assert tols.dm_tol == [90, 110]
        assert tols.width_tol == [90, 110]
        assert tols.sn_tol == 85
        assert tols.pdot_tol == [pytest.approx(1e-16), pytest.approx(1e-14)]

    def test_search_using_basic_ruleset(self):
        """
        Test the basic search method recovers the one
        candidate that falls within a set of tolerances.
        """
        vector = (
            "FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil"
        )
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "duration": 600,
        }
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = FdasScl(scl_dir)
        candidate.from_vector(vector, source_properties)
        candidate.search_tol("basic")
        assert candidate.detected is True
        assert candidate.recovered.shape[0] == 1
        true_candidate = [18.5179, 0, 99.7, 9, 2.05754, 463.76]
        true = pd.DataFrame([true_candidate], index=[2])
        true.columns = ["period", "pdot", "dm", "harmonic", "width", "sn"]
        assert np.all(true == candidate.recovered)

    def test_search_using_basic_ruleset_no_detection(self):
        """
        Test the basic search method filters all candidates
        """
        vector = (
            "FLDO-MID_336a2a6_48.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil"
        )
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.2,
            "duration": 600,
        }
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = FdasScl(scl_dir)
        candidate.from_vector(vector, source_properties)
        candidate.search_tol("basic")
        assert candidate.detected is False
        assert candidate.recovered is None

    def test_basic_fdas_rules(self):
        """
        Test the basic tolerance generator
        returns to expected ranges/limits
        """
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "duration": 600,
        }

        tols = FdasTolBasic([1, 0, 100, 0.1, 50], source_properties)
        assert tols.period_tol == [0.9981408178473872, 1.001866121070591]
        assert tols.dm_tol == [99.746530646593, 100.253469353407]
        assert tols.sn_tol == 42.5
        assert tols.pdot_tol == [pytest.approx(1e-16), pytest.approx(1e-14)]

    def test_wrong_ruleset_error(self):
        """
        Test that the correct exception is raised
        when an invalid ruleset is passed to the
        constructor.
        """
        vector = (
            "FLDO-MID_336a2a6_54.0_0.1_100_0.0_Gaussian_50.0_0000_123123.fil"
        )
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "duration": 600,
        }
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = FdasScl(scl_dir)
        candidate.from_vector(vector, source_properties)
        with pytest.raises(ValueError):
            candidate.search_tol("invalid_ruleset")
