#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |                  Unit tests for filterbank reader                      |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    |  pytest -m filtests                                                    |
    |      <or>                                                              |
    | make test MARK="filtests" (recommended)                                |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2022 University of Manchester                                |
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
    |                                                                        |
    |THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS     |
    |"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       |
    |LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A |
    |PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT      |
    |HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  |
    |SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT        |
    |LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   |
    |DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON       |
    |ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR      |
    |TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE  |
    |USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH        |
    |DAMAGE.                                                                 |
    **************************************************************************
"""

import pytest
from pytest import mark

from ska_pss_protest import VectorPull, VHeader

# pylint: disable=R0201,E1101,W0621


@pytest.fixture(scope="session")
def get_vector():
    """
    Uses requester class to obtain test vector
    for header checking.

    Vector is cleared from disk after tests have run.
    """
    vector = VectorPull()
    vector.from_name(
        "FDAS-HSUM-MID_38d46df_500.0_0.4_1.0_0.0_Gaussian_50.0_123123123.fil"
    )
    yield vector


@mark.unit
@mark.filtests
class FilterbankTests:
    """
    Tests filterbank reader correctly parses
    header parameters
    """

    def test_synthetic_header_read(self, get_vector):
        """
        Tests synthetic test vector header is
        being read correctly.
        """
        header = VHeader(get_vector.local_path)
        assert header.fch1() == 1670.0
        assert header.machine_id() == 10
        assert header.chbw() == -20.0
        assert header.nchans() == 16
        assert header.source_name() == "noise"
        assert header.nbits() == 8
        assert header.start_time() == 56000.0
        assert header.tsamp() == 6.4e-05
        assert header.header_size() == 242
        assert header.duration() == pytest.approx(600, 0.1)
        assert header.data_size() == 150000000
        # No position info in header
        with pytest.raises(KeyError):
            header.raj()
            header.decj()

    def test_real_header_read(self):
        """
        Tests header information from real JBO pulsar
        observation is being read correctly
        """
        path = "tests/data/sigproc/56352_54818_B1929+10_test.fil"
        header = VHeader(path)
        assert header.fch1() == 1732.0
        assert header.machine_id() == 0
        assert header.chbw() == -0.50
        assert header.nchans() == 800
        assert header.source_name() == "B1929+10"
        assert header.nbits() == 8
        assert header.start_time() == 56352.634479166663
        assert header.tsamp() == 256e-06
        assert header.header_size() == 296
        assert header.duration() == pytest.approx(10, 0.1)
        assert header.data_size() == 31250400
        assert header.raj() == 193213.86803807662
        assert header.decj() == 105931.84868432973
        assert header.tel() == 0

    def test_invalid_parameter(self, get_vector):
        """
        Tests the correct exception is raised when an
        invalid parameter is requested
        """
        header = VHeader(get_vector.local_path)
        with pytest.raises(AttributeError):
            header.get_sfjksdfjskl()

    def test_non_existent_filterbank(self):
        """
        Tests that the correct exception is
        raised when a non-existent filterbank is
        provided
        """
        with pytest.raises(FileNotFoundError):
            VHeader("jflsfjlsdkdfj.fil")

    def test_signal_par_extraction_synthetic_vector(self, get_vector):
        """
        Tests that the correct signal parameters
        can be extracted from a PSS test vector filename
        """
        pars = VHeader(get_vector.local_path).allpars()
        assert pars["freq"] == 500.0
        assert pars["disp"] == 1.0
        assert pars["width"] == 0.4
        assert pars["sig"] == 50.0
        assert pars["sig"] != 100.0
        with pytest.raises(KeyError):
            pars["bad_key"]

    def test_signal_par_extraction_real_vector(self):
        """
        Tests that signal parameters are not extracted
        from a vector that is not an official PSS test vector
        """
        vector_path = "tests/data/sigproc/56352_54818_B1929+10_test.fil"
        pars = VHeader(vector_path).allpars()
        with pytest.raises(KeyError):
            assert pars["freq"] == 500.0