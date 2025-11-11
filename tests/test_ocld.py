"""
**************************************************************************
|                                                                        |
|                  Unit tests for OCLD reader                            |
|                                                                        |
**************************************************************************
| Author: Raghuttam Hombal                                               |
| Email : raghuttamshreepadraj.hombal@manchester.ac.uk                   |
**************************************************************************
| Usage:                                                                 |
|                                                                        |
|  pytest -m ocldtests                                                   |
|      <or>                                                              |
| make test MARK="ocldtests" (recommended)                               |
**************************************************************************
| License:                                                               |
|                                                                        |
| Copyright 2025 SKA Observatory                                         |
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

import numpy as np
import pandas as pd
import pytest
from pytest import mark

from ska_pss_protest import OcldReader

# pylint: disable=E1101,W0621,W0104


@mark.unit
@mark.ocldtests
class OcldReaderTests:
    """
    Unit tests for OcldReader class
    """

    def test_ocld_file_read(self):
        """
        Test reading OCLD file header
        """
        path = "tests/data/ocld/test.ocld"
        reader = OcldReader(path)
        reader.load_metadata()

        assert reader is not None

    def test_ocld_file_not_found(self):
        """
        Test OCLD file not found scenario
        """
        with pytest.raises(expected_exception=FileNotFoundError):
            reader = OcldReader("niefiuweb.ocld")
            reader.load_metadata()

        with pytest.raises(expected_exception=FileNotFoundError):
            filename = "niefiuweb.ocld"
            reader._parse(filename, 512)

        with pytest.raises(expected_exception=FileNotFoundError):
            filename = "niefiuweb.ocld"
            reader._get_candidate_data(filename, 0, 512, 131072)

    def test_ocld_runtime_errors(self):
        """
        Test OCLD runtime errors for not loading metadata
        """
        with pytest.raises(expected_exception=RuntimeError):
            reader = OcldReader("tests/data/ocld/test.ocld")
            reader.get_metadata_df()

        with pytest.raises(expected_exception=RuntimeError):
            reader = OcldReader("tests/data/ocld/test.ocld")
            reader.get_candidate_fpp(0)

        with pytest.raises(expected_exception=RuntimeError):
            reader = OcldReader("tests/data/ocld/test.ocld")
            reader.get_candidate_pulse_profile(0)

    def test_ocld_metadata_header_content(self):
        """
        Test OCLD metadata content
        """
        path = "tests/data/ocld/test.ocld"
        reader = OcldReader(path)
        reader.load_metadata()

        expected_metadata = {
            "nsubints": 16,
            "nbands": 64,
            "nphase": 128,
        }

        for key, value in expected_metadata.items():
            assert reader.metadata.get(key) == value

    def test_ocld_metadata_dataframe(self):
        """
        Test OCLD metadata as DataFrame
        """
        path = "tests/data/ocld/test.ocld"
        reader = OcldReader(path)
        reader.load_metadata()

        df = reader.get_metadata_df()

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "period" in df.columns
        assert "pdot" in df.columns
        assert "dm" in df.columns
        assert "COUNT" not in df.columns
        assert "NSUBINT" not in df.columns
        assert "NPHASE" not in df.columns
        assert "NSUBBAND" not in df.columns
        assert len(df) == 1  # Assuming test.ocld has one candidate

    def test_ocld_get_candidate_fpp(self):
        """
        Test retrieving candidate FPP data
        """
        path = "tests/data/ocld/test.ocld"
        reader = OcldReader(path)
        reader.load_metadata()

        candidate_index = 0
        fpp_data = reader.get_candidate_fpp(candidate_index)

        assert isinstance(fpp_data, np.ndarray)
        assert fpp_data.shape == (
            int(reader.metadata["nsubints"]),
            int(reader.metadata["nbands"]),
            int(reader.metadata["nphase"]),
        )

    def test_ocld_get_candidate_pulse_profile(self):
        """
        Test retrieving candidate pulse profile data
        """
        path = "tests/data/ocld/test.ocld"
        reader = OcldReader(path)
        reader.load_metadata()

        candidate_index = 0
        pulse_profile = reader.get_candidate_pulse_profile(candidate_index)

        assert isinstance(pulse_profile, np.ndarray)
        assert pulse_profile.shape == (int(reader.metadata["nphase"]),)
