"""
    **************************************************************************
    |                                                                        |
    |                  Unit tests for filterbank reader                      |
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
