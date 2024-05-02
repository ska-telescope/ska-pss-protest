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
    | Copyright 2023 SKA Organisation                                        |
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

import ska_pss_protest.candlist as cand
from ska_pss_protest import VectorPull, VHeader

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
@mark.unit
class SpCclTests:
    """
    Tests to verify the functionality of the
    single pulse search (SPS) candidate metadata class
    """

    def test_non_existent_spccl_dir(self):
        """
        Test exception is raised when non-existent
        SpCcl directory is passed to constructor
        """
        spccl_dir = "/tmp/random_test_dir/ajd994jfma29"
        with pytest.raises(OSError):
            cand.SpCcl(spccl_dir)

    def test_load_detected_candidates(self):
        """
        Test that detected candidates files are loaded correctly.
        A directory containing the detected metadata file is provided
        and the candidate metadata file (.spccl) is parsed and the
        contents returned as a Nx4 array, where N is the number of
        candidates and 4 is the number of parameters per candidate.
        """
        # Set up directory containing "detected" candidates file
        spccl_dir = os.path.join(DATA_DIR, "spccl_1")

        # Instantiate candidate parser, passing directory as args
        # The directory contains a "detected" candidates file which will
        # be loaded into memory and the contents compared to
        # a list of expected candidates (next step)
        candidate = cand.SpCcl(spccl_dir)

        # Load in "expected" candidate metadata file
        known_file = os.path.join(DATA_DIR, "spccl_1/candidates.txt")
        known_cands = np.loadtxt(known_file, unpack=False, skiprows=1).tolist()
        known_cands.sort(key=lambda x: x[3], reverse=True)

        # Check that the two sets of candidates are the same
        assert np.all(known_cands == candidate.cands)

    def test_no_candidate_dir(self):
        """
        Tests that the correct exception is
        raised when no candidate directory is
        passed to the constructor.
        """
        with pytest.raises(OSError):
            cand.SpCcl()

    def test_no_cand_file_extension_in_valid_dir(self):
        """
        Tests that the correct exception is raised if
        a valid directory is passed to the contructor
        but files of a custom extension are not found
        there
        """
        # Create new directory with random name under /tmp
        spccl_dir = tempfile.mkdtemp()
        with pytest.raises(IOError):
            # Pass real dir but with random non-existent extension
            cand.SpCcl(spccl_dir, "sdfhjs")
        shutil.rmtree(spccl_dir)

    def test_no_cand_files_in_valid_dir(self):
        """
        Tests that the correct exception is raised if
        a valid directory is passed to the constructor
        but files of the default extension (.spccl) are
        not found there
        """
        # Create new directory with random name under /tmp
        spccl_dir = tempfile.mkdtemp()
        with pytest.raises(IOError):
            # Pass real (but empty) directory
            cand.SpCcl(spccl_dir)
        shutil.rmtree(spccl_dir)

    def test_wrong_number_of_cand_files(self):
        """
        We expect one candidate file per scan and therefore
        only one metadata file in each directory. This tests
        that the correct exception is raised if more than one
        candidate file is found.
        """
        # Create new directory with random name under /tmp
        spccl_dir = tempfile.mkdtemp()

        # Define two candidate metadata file paths
        file1 = os.path.join(spccl_dir, "cand1.spccl")
        file2 = os.path.join(spccl_dir, "cand2.spccl")

        with pytest.raises(IOError):
            # Generate empty files in directory
            open(file1, "a").close()
            open(file2, "a").close()
            cand.SpCcl(spccl_dir)
        shutil.rmtree(spccl_dir)

    def test_candidate_list_empty(self):
        """
        Tests that an exception is raised if attempting
        to validate an empty candidate file.
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_5")
        with pytest.raises(Exception):
            cand.SpCcl(spccl_dir)

    def test_from_vector_no_vector_provided(self):
        """
        Test that the correct exceptions are raise if
        we don't provide a valid test vector path to
        from_vector()
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2", "lowdm")
        cands = cand.SpCcl(spccl_dir)
        # Generate exception if no vector provided
        with pytest.raises(TypeError):
            cands.from_vector()
        # Generate exception if non-existent vector provided
        with pytest.raises(FileNotFoundError):
            cands.from_vector("/this/random/path.fil")

    def test_from_vector_exact(self, get_vector):
        """
        Tests that the from_vector() method generates
        the correct "expected" single pulse parameters.
        This uses a fixture candidate file generated
        from the vector.
        The test will pass if the from_vector() method
        returns the values contained in the fixture
        file

        The length of the candidate list is also tested here
        """
        # Load candidate list
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm")
        candidate = cand.SpCcl(spccl_dir)
        # Generate list of expected candidates
        candidate.from_vector(get_vector.local_path)
        exp = candidate.expected

        # Check from_vector() expects the corrected
        # number of candidates.
        assert len(exp) == len(candidate.cands)

        # Read parameters from filterbank
        fil = VHeader(get_vector.local_path)
        pars = fil.allpars()
        npulses = fil.duration() * pars["freq"]
        sn_pp = pars["sig"] / np.sqrt(npulses)

        # Comute the DM offset expected and use that to infer
        # the arrival time of the fiducial pulse in the test vector
        dm_offset = 4.15e6 * (1 / fil.fch1()) ** 2.0 * pars["disp"]
        arrival_time = (
            fil.start_time()
            + (((1 / pars["freq"]) / 86400) / 2)
            + (dm_offset / 1000 / 86400)
        )

        fiducial_detected = False

        # Go through each of the expected pulses and check that
        # they match the candidate pulses in the fixture file
        # AND that they match the candidate pulse parameters
        # as calculated from the header/signal parameters
        # directly
        for i in range(0, len(exp)):
            # Check S/N per pulse
            assert sn_pp == pytest.approx(exp[i][3], 1e-7)
            assert candidate.cands[i][3] == pytest.approx(exp[i][3], 1e-09)
            # Check the dispersion measure
            assert pars["disp"] == pytest.approx(exp[i][1], 1e-07)
            assert candidate.cands[i][1] == pytest.approx(exp[i][1], 1e-09)
            # Check the width
            assert pars["width"] / pars["freq"] * 1000 == pytest.approx(
                exp[i][2], 1e-04
            )
            assert candidate.cands[i][2] == pytest.approx(exp[i][2], 1e-09)
            # Check all the timestamps (compared with file)
            assert candidate.cands[i][0] == exp[i][0]
            # Check the fiducial pulse timestamp (compared with calculations)
            if arrival_time == pytest.approx(exp[i][0], fil.tsamp()):
                fiducial_detected = True
        assert fiducial_detected is True

    def test_from_vector_exact_highdm(self, get_high_dm_vector):
        """
        Tests that the from_vector() method generates
        the correct "expected" single pulse parameters.
        This uses a fixture candidate file generated
        from the vector.
        The test will pass if the from_vector() method
        returns the values contained in the fixture
        file

        The length of the candidate list is also tested here
        """
        # Load candidate list
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/highdm")
        candidate = cand.SpCcl(spccl_dir)
        # Generate list of expected candidates
        candidate.from_vector(get_high_dm_vector.local_path)
        exp = candidate.expected

        # Check from_vector() expects the corrected
        # number of candidates.
        assert len(exp) == len(candidate.cands)

        # Read parameters from filterbank
        fil = VHeader(get_high_dm_vector.local_path)
        pars = fil.allpars()
        npulses = fil.duration() * pars["freq"]
        sn_pp = pars["sig"] / np.sqrt(npulses)

        # Comute the DM offset expected and use that to infer
        # the arrival time of the fiducial pulse in the test vector
        dm_offset = 4.15e6 * (1 / fil.fch1()) ** 2.0 * pars["disp"]
        arrival_time = (
            fil.start_time()
            + (((1 / pars["freq"]) / 86400) / 2)
            + (dm_offset / 1000 / 86400)
        )

        fiducial_detected = False

        # Go through each of the expected pulses and check that
        # they match the candidate pulses in the fixture file
        # AND that they match the candidate pulse parameters
        # as calculated from the header/signal parameters
        # directly
        for i in range(0, len(exp)):
            # Check S/N per pulse
            assert sn_pp == pytest.approx(exp[i][3], 1e-7)
            assert candidate.cands[i][3] == pytest.approx(exp[i][3], 1e-09)
            # Check the dispersion measure
            assert pars["disp"] == pytest.approx(exp[i][1], 1e-07)
            assert candidate.cands[i][1] == pytest.approx(exp[i][1], 1e-09)
            # Check the width
            assert pars["width"] / pars["freq"] * 1000 == pytest.approx(
                exp[i][2], 1e-04
            )
            assert candidate.cands[i][2] == pytest.approx(exp[i][2], 1e-09)
            # Check all the timestamps (compared with file)
            assert candidate.cands[i][0] == exp[i][0]
            # Check the fiducial pulse timestamp (compared with calculations)
            if arrival_time == pytest.approx(exp[i][0], fil.tsamp()):
                fiducial_detected = True
        assert fiducial_detected is True

    def test_from_spccl_no_header(self):
        """
        Test that from_spccl() correctly parses a SpCcl metadata
        file that does not contain header/column information
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_3")
        candidate = cand.SpCcl(spccl_dir)

        expected_spccl = os.path.join(
            DATA_DIR, "spccl_3/candidates_noheader.txt"
        )
        candidate.from_spccl(expected_spccl)
        contents = np.loadtxt(expected_spccl, skiprows=0)
        assert np.all(contents == candidate.expected)

    def test_from_spccl_with_header(self):
        """
        Test that from_spccl() correctly parses a SpCcl metadata
        file that contains header/column information.
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_3")
        candidate = cand.SpCcl(spccl_dir)

        expected_spccl = os.path.join(
            DATA_DIR, "spccl_3/candidates_header.txt"
        )
        candidate.from_spccl(expected_spccl)
        contents = np.loadtxt(expected_spccl, skiprows=1)
        assert np.all(contents == candidate.expected)

    def test_from_spccl_corrupted(self):
        """
        Test that from_spccl() raises an exception if the SpCcl metadata
        file cannot be read correctly/is corrupted.
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_3")
        candidate = cand.SpCcl(spccl_dir)

        expected_spccl = os.path.join(
            DATA_DIR, "spccl_3/candidates_header2.txt"
        )
        with pytest.raises(ValueError):
            candidate.from_spccl(expected_spccl)

    def test_from_spccl_no_file(self):
        """
        Tests that from_spccl() raises an exception if no SpCcl file
        is provided to the function call.
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_3")
        candidate = cand.SpCcl(spccl_dir)
        expected_spccl = "/this/random/path.spccl"
        with pytest.raises(FileNotFoundError):
            candidate.from_spccl(expected_spccl)

    def test_compare_dm_within_tol_using_vector(self, get_vector):
        """
        Tests that candidates are recovered by compare_dm() using
        source properties computed using header reader VHeader().
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm")
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_vector(get_vector.local_path)

        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(
            VHeader(get_vector.local_path).allpars(), widths_list
        )

        assert len(candidate.detections) == len(candidate.expected)
        assert len(candidate.non_detections) == 0

    def test_compare_dm_within_tol_no_vector(self):
        """
        Tests that candidates are recovered by compare_dm() using
        manually specified source properties.
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm")
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.2,
        }
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_spccl(
            os.path.join(DATA_DIR, "spccl_2/lowdm/expected.spccl")
        )
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(source_properties, widths_list)
        assert len(candidate.detections) == len(candidate.expected)
        assert len(candidate.non_detections) == 0

    def test_compare_dm_tol_exceeded_no_vector(self):
        """
        Tests that compare_dm() correctly identifies
        missing candidates (i.e., signals present in the test
        vector that were not "detected" and written to the
        candidate metadata file).
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm_incorrect")
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.2,
        }
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_spccl(
            os.path.join(DATA_DIR, "spccl_2/lowdm/expected.spccl")
        )
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(source_properties, widths_list)
        assert len(candidate.detections) < len(candidate.expected)
        assert len(candidate.non_detections) > 0

    def test_compare_widthstep_within_tol_no_vector(self):
        """
        Tests that candidates are recovered by compare_widthstep() using
        manually specified source properties.
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm")
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.2,
        }
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_spccl(
            os.path.join(DATA_DIR, "spccl_2/lowdm/expected.spccl")
        )
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(source_properties, widths_list)
        assert len(candidate.detections) == len(candidate.expected)
        assert len(candidate.non_detections) == 0

    def test_compare_widthstep_within_tol_using_vector(self, get_vector):
        """
        Tests that candidates are recovered by compare_widthstep() using
        source properties computed using header reader VHeader().
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm")
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_vector(get_vector.local_path)
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(
            VHeader(get_vector.local_path).allpars(), widths_list
        )
        assert len(candidate.detections) == len(candidate.expected)
        assert len(candidate.non_detections) == 0

    def test_compare_widthstep_tol_exceeded_no_vector(self):
        """
        Tests that compare_widthstep() correctly identifies
        missing candidates (i.e., signals present in the test
        vector that were not "detected" and written to the
        candidate metadata file).
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm_incorrect")
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.2,
        }
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_spccl(
            os.path.join(DATA_DIR, "spccl_2/lowdm/expected.spccl")
        )
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(source_properties, widths_list)
        assert len(candidate.detections) < len(candidate.expected)
        assert len(candidate.non_detections) > 0

    def test_widthsteptol(self):
        """
        Tests that the class responsible for providing
        SpCcl metadata tolerance ranges, based on the DM step
        size, is returning the correct values.
        """
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]

        # Test a pulse width of 0.001 ms
        expected = [56000.00004631352, 1.0, 0.001, 18.257418583505537]
        vector_pars = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.125,
            "width": 1.25e-07,
            "disp": 1.0,
            "sig": 50.0,
        }

        tols = cand.WidthTol(expected, vector_pars, widths_list)
        assert tols.width_tol == [1.0, 128.0]
        assert tols.timestamp_tol == pytest.approx(4.91505e-12, abs=1e-17)
        assert tols.dm_tol == pytest.approx(0.002534, abs=1e-6)

        # Test a pulse width of 0.1 ms
        expected = [56000.00004631352, 1.0, 0.1, 18.257418583505537]
        vector_pars = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.125,
            "width": 1.25e-05,
            "disp": 1.0,
            "sig": 50.0,
        }

        tols = cand.WidthTol(expected, vector_pars, widths_list)
        assert tols.width_tol == [64.0, 256.0]
        assert tols.timestamp_tol == pytest.approx(4.91505e-10, abs=1e-15)
        assert tols.dm_tol == pytest.approx(0.2534, abs=1e-04)

        # Test a pulse width of 10 ms
        expected = [56000.00004631352, 1.0, 10.0, 18.257418583505537]
        vector_pars = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.00125,
            "width": 1.25e-05,
            "disp": 1.0,
            "sig": 50.0,
        }

        tols = cand.WidthTol(expected, vector_pars, widths_list)
        assert tols.width_tol == [4096.0, 32768.0]
        assert tols.timestamp_tol == pytest.approx(4.91505e-8, abs=1e-13)
        assert tols.dm_tol == pytest.approx(25.34, abs=0.01)

        # Test a pulse width of 10 ms
        expected = [56000.00004631352, 1.0, 1000.0, 18.257418583505537]
        vector_pars = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.125,
            "width": 1.25e-05,
            "disp": 1.0,
            "sig": 50.0,
        }

        tols = cand.WidthTol(expected, vector_pars, widths_list)
        assert tols.width_tol == [524288.0, 1000000.0]
        assert tols.timestamp_tol == pytest.approx(4.91505e-6, abs=1e-11)
        assert tols.dm_tol == pytest.approx(2534, abs=1)

    def test_summary_exporter_detections(self, get_vector):
        """
        This test is to make sure that summary_exporter()
        exports non-detection candidates to a summary.txt file
        by checking if it exists after the process has run
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm")
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_vector(get_vector.local_path)
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(
            VHeader(get_vector.local_path).allpars(), widths_list
        )
        candidate.summary_export(VHeader(get_vector.local_path).allpars())
        assert os.path.isfile(os.path.join(spccl_dir, "summary.txt"))
        with open(os.path.join(spccl_dir, "summary.txt"), "r") as fp:
            lines = len(fp.readlines())
        assert (
            len(candidate.detections) + len(candidate.non_detections)
            == lines - 1
        )

        os.remove(os.path.join(spccl_dir, "summary.txt"))

    def test_summary_exporter_non_detections(self):
        """
        This test is to make sure that summary_exporter()
        exports non-detection candidates to a summary.txt file
        by checking if it exists after the process has run
        """
        spccl_dir = os.path.join(DATA_DIR, "spccl_2/lowdm_incorrect")
        source_properties = {
            "fch1": 1670.0,
            "foff": -0.078125,
            "nchans": 4096,
            "tsamp": 6.4e-05,
            "freq": 0.2,
            "rfi_id": "0000",
            "width": 0.1,
            "sig": 100,
            "disp": 10,
        }
        candidate = cand.SpCcl(spccl_dir)
        candidate.from_spccl(
            os.path.join(DATA_DIR, "spccl_2/lowdm/expected.spccl")
        )
        widths_list = [
            1,
            2,
            4,
            8,
            16,
            32,
            64,
            128,
            512,
            1024,
            2048,
            4096,
            8192,
            15000,
        ]
        candidate.compare_widthstep(source_properties, widths_list)
        candidate.summary_export(source_properties)
        assert os.path.isfile(os.path.join(spccl_dir, "summary.txt"))
        with open(os.path.join(spccl_dir, "summary.txt"), "r") as fp:
            lines = len(fp.readlines())
        assert (
            len(candidate.detections) + len(candidate.non_detections)
            == lines - 1
        )

        os.remove(os.path.join(spccl_dir, "summary.txt"))


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
            cand.FdasScl(scl_dir)

    def test_load_detected_candidates(self):
        """
        Test that detected candidates files are loaded correctly.
        A directory containing the detected metadata file is provided
        and the candidate metadata file (.scl) is parsed and the
        contents returned as a Nx4 array, where N is the number of
        candidates and 5 is the number of parameters per candidate.
        """
        # Set up directory containing "detected" candidates file
        scl_dir = os.path.join(DATA_DIR, "scl_1")

        # Instantiate candidate parser, passing directory as args
        # The directory contains a "detected" candidates file which will
        # be loaded into memory and the contents compared to
        # a list of expected candidates (next step)
        candidate = cand.FdasScl(scl_dir)

        # Load in "expected" candidate metadata file
        known_file = os.path.join(DATA_DIR, "scl_1/test_candlist.scl")
        known_cands = pd.read_csv(known_file, sep=r"\s+")
        known_cands.columns = ["period", "pdot", "dm", "width", "sn"]
        known_cands = known_cands.sort_values("sn", ascending=False)

        assert np.all(candidate.cands == known_cands)

    def test_no_candidate_dir(self):
        """
        Tests that the correct exception is
        raised when no candidate directory is
        passed to the constructor.
        """
        with pytest.raises(OSError):
            cand.FdasScl()

    def test_no_cand_file_extension_in_valid_dir(self):
        """
        Tests that the correct exception is raised if
        a valid directory is passed to the contructor
        but files of a custom extension are not found
        there
        """
        # Create new directory with random name under /tmp
        scl_dir = tempfile.mkdtemp()
        with pytest.raises(IOError):
            # Pass real dir but with random non-existent extension
            cand.FdasScl(scl_dir, "sdfhjs")
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
            cand.FdasScl(scl_dir)
        shutil.rmtree(scl_dir)

    def test_from_vector(self):
        """
        Tests that we can extract the correct pulsar
        parameters from a FDAS test vector
        """
        vector_a = "FDAS-HSUM-MID_38d46df_500.0_0.2_1.0_0.0_Gaussian_50.0_0000_123123123.fil"
        vector_b = "FDAS-HSUM-MID_38d46df_500.00115818617536_0.05_1.0_0.0_Gaussian_50.0_0000_123123123.fil"
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = cand.FdasScl(scl_dir)

        period = 1.0 / 500.0
        width = 0.2 * period * 1000
        candidate.from_vector(vector_a)
        assert candidate.expected == [period, 1.0, width, 50.0]

        period = 1.0 / 500.00115818617536
        width = 0.05 * period * 1000
        candidate.from_vector(vector_b)
        assert candidate.expected == [period, 1.0, width, 50.0]
        assert candidate.expected != [period, 2.0, width, 500.0]

    def test_search_using_dummy_ruleset(self):
        """
        Test the dummy search method recovers the one
        candidate that falls within a set of tolerances.
        """
        vector = "FDAS-HSUM-MID_38d46df_500.0_0.2_1.0_0.0_Gaussian_50.0_0000_123123123.fil"
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = cand.FdasScl(scl_dir)
        candidate.from_vector(vector)
        candidate.search_dummy()
        assert candidate.detected is True
        assert candidate.recovered.shape[0] == 1
        true_candidate = [0.002, 1e-15, 0.999, 0.4, 49.999]
        true = pd.DataFrame([true_candidate], index=[500])
        true.columns = ["period", "pdot", "dm", "width", "sn"]
        assert np.all(true == candidate.recovered)

    def test_search_using_dummy_ruleset_no_detection(self):
        """
        Test the dummy search method filters all candidates
        """
        vector = "F_1_100000.0_0.2_1.0_0.0_G_500.0_0000_1.fil"
        scl_dir = os.path.join(DATA_DIR, "scl_1")
        candidate = cand.FdasScl(scl_dir)
        candidate.from_vector(vector)
        candidate.search_dummy()
        assert candidate.detected is False
        assert candidate.recovered is None

    def test_dummy_fdas_rules(self):
        """
        Test the dummy tolerance generator
        returns to expected ranges/limits
        """
        tols = cand.FdasTolDummy([1, 100, 100, 100])
        assert tols.period_tol == [0.9, 1.1]
        assert tols.dm_tol == [90, 110]
        assert tols.width_tol == [90, 110]
        assert tols.sn_tol == 85
