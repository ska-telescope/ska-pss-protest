"""
    **************************************************************************
    |                                                                        |
    |               Unit tests for ProTest inferface                         |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Tests the functionality of the PSS testing framework frontend          |
    | application protest.py. protest.py's purpose is to parse CLI input     |
    | in order to configure pytest.                                          |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2024 University of Manchester                                |
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

from pytest import mark

from ska_pss_protest.executors._config import set_markers

# pylint: disable=R0903


@mark.unit
class ProtestTests:
    """
    Tests of the ProTest executable
    """

    def test_protest_marker_setter(self):
        """
        Test that the marker setter correctly
        parses the included and excluded tests
        and returns the correct string to pytest
        """

        # Do we correctly set test types?
        # Note that argparse passes in lists of requested test types to a variable
        # that is initialised as False
        assert set_markers() == "product"
        assert set_markers(["product"]) == "product"
        assert set_markers(False, ["product"]) == "not product"
        assert set_markers(["nasm"], ["container"]) == "nasm and not container"
        assert set_markers(False, ["sps"]) == "not sps"
        assert set_markers(False, ["sps", "mid"]) == "not sps and not mid"
        assert set_markers(["sps", "low"]) == "sps and low"
        assert set_markers(["sps", "low"], False) == "sps and low"

        # In the following scenario, pytest will execute no tests
        assert (
            set_markers(["sps", "low"], ["sps", "low"])
            == "sps and low and not sps and not low"
        )

        # ProTest doesn't care if the tests requested/excluded do not represent valid markers.
        # It will pass them to pytest anyway. Pytest will simply not execute any tests for that
        # marker as there won't be any!
        assert (
            set_markers(["foo", "bar"], ["sdfgh"])
            == "foo and bar and not sdfgh"
        )

        # For sanity, test a negative scenario
        assert (
            set_markers(["physhw"], ["container"])
            != "container and not physhw"
        )
        assert (
            set_markers(["physhw"], ["container"])
            == "physhw and not container"
        )
