"""
    **************************************************************************
    |                                                                        |
    |               Unit tests for candidate parser                          |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Tests the functionality of the PSS testing framework backend           |
    | application candidate.py. Candidate's purpose is to parse and inspect  |
    | candidate filterbanks exported by the PSS search pipelines             |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    |  pytest -m candtests                                                   |
    |          <or>                                                          |
    |  make test MARK="candtests"                                            |
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

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest
from pytest import mark

from ska_pss_protest import Filterbank, VHeader

# pylint: disable=R1732,W1514,E1120,W0621

DATA_DIR = os.path.join(
    Path(os.path.abspath(__file__)).parents[1], "tests/data/sigproc"
)


@mark.candtests
@mark.unit
class CandidateTests:
    """
    Tests of the Filterbank() class in
    candidate.py
    """

    def test_non_existent_cand_dir(self):
        """
        Test exception is raised when non-existent
        candidate directory is passed to constructor
        """
        cand_dir = "/tmp/random_test_dir/ajd994jfma29"
        with pytest.raises(OSError):
            Filterbank(cand_dir)

    def test_no_candidate_dir(self):
        """
        Tests that the correct exception is
        raised when no candidate directory is
        passed to the constructor.
        """
        with pytest.raises(OSError):
            Filterbank()

    def test_no_cand_file_extension_in_valid_dir(self):
        """
        Tests that the correct exception is raised if
        a valid directory is passed to the contructor
        but files of a custom extension are not found
        there
        """
        # Create new directory with random name under /tmp
        cand_dir = tempfile.mkdtemp()
        with pytest.raises(IOError):
            # Pass real dir but with random non-existent extension
            Filterbank(cand_dir, "sdfhjs")
        shutil.rmtree(cand_dir)

    def test_no_cand_files_in_valid_dir(self):
        """
        Tests that the correct exception is raised if
        a valid directory is passed to the constructor
        but files of the default extension (.spccl) are
        not found there
        """
        # Create new directory with random name under /tmp
        cand_dir = tempfile.mkdtemp()
        with pytest.raises(IOError):
            # Pass real (but empty) directory
            Filterbank(cand_dir)
        shutil.rmtree(cand_dir)

    def test_get_header(self):
        """
        Tests that the get_header() method returns a list of
        VHeader objects each corresponding to one of several
        (in this test, two) candidate filterbank files.

        Note: Some header parameters that exist in an input
        test vector  (e.g, telescope_id, accessed by VHeader
        method telescope_id()), are not set by the cheetah
        pipeline when it exports the candidate filterbanks.
        """
        cand_dir = os.path.join(DATA_DIR, "multiple_candidates")
        parser = Filterbank(cand_dir)
        parser.get_headers()
        assert len(parser.headers) == 2
        for header in parser.headers:
            assert isinstance(header, VHeader)
            assert header.fch1() == 1670.0
            assert header.nchans() == 16
            assert header.nbits() == 8
            assert header.chbw() == -20.0
            assert header.tsamp() == 6.4e-05

    def test_compare_data_chunk_size(self):
        """
        Tests that the correct exception is raised if
        the chunk_size value is invalid.
        """
        cand_dir = os.path.join(DATA_DIR, "candidate_1")
        parser = Filterbank(cand_dir)
        with pytest.raises(ValueError):
            parser.compare_data(os.path.join(cand_dir, "candidate_1.fil"), 0)
        with pytest.raises(TypeError):
            parser.compare_data(
                os.path.join(cand_dir, "candidate_1.fil"), "sdfsf"
            )

    def test_compare_data_number_of_files(self):
        """
        Tests that the correct exception is raised if
        multiple candidates are passed to compare_data()
        for comparison to a single test vector.
        """
        cand_dir = os.path.join(DATA_DIR, "multiple_candidates")
        parser = Filterbank(cand_dir)
        with pytest.raises(IOError):
            parser.compare_data(os.path.join(cand_dir, "candidate_1.fil"))

    def test_compare_data_match(self):
        """
        Tests that a bitwise comparison between two identical
        filterbank files returns a match=True result.
        """
        cand_dir = os.path.join(DATA_DIR, "candidate_1")
        parser = Filterbank(cand_dir)
        parser.compare_data(
            os.path.join(cand_dir, "2012_03_14_00:00:00.fil"), 1024
        )
        assert parser.result is True

    def test_compare_data_mismatch(self):
        """
        Tests that a bitwise comparison between two different
        filterbank files returns a match=False result.
        """
        cand_dir = os.path.join(DATA_DIR, "candidate_1")
        parser = Filterbank(cand_dir)
        parser.compare_data(
            os.path.join(
                DATA_DIR, "multiple_candidates/2012_03_14_00:00:00_1.fil"
            ),
            1024,
        )
        assert parser.result is False

    def test_json_dump(self):
        """
        Tests that a JSON dump containing candidate
        header info is correctly executed
        """
        cand_dir = os.path.join(DATA_DIR, "candidate_1")
        parser = Filterbank(cand_dir)
        parser.reduce_headers(remove_fils=False)

        # We should now have a json file - check
        json_path = os.path.join(cand_dir, "candidate_headers.json")
        assert os.path.isfile(json_path)

        # Is it valid json?
        with open(json_path, "r") as jfile:
            json.load(jfile)
        jfile.close()

        # Clean up
        os.remove(json_path)
