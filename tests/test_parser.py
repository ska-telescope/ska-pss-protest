#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |               Unit tests for test vector provisioning                  |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Tests the functionality of the PSS testing framework backend           |
    | application logparser.py. The logparser's purpose is to check log      |
    | files as output by Cheetah and search them for strings of interest.    |
    **************************************************************************
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    |  pytest -m parsertests                                                 |
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
from ska_pss_protest import LogParse


# pylint: disable=R0201,E1123,C0114

with open('tests/data/parser_log.json', encoding="utf8") as this_file:
    parser_file = this_file.read()
this_file.close()

with open('tests/data/parser_log_error.json', encoding="utf8") as this_file:
    error_file = this_file.read()
this_file.close()

with open('tests/data/emulator_log.txt', encoding="utf8") as this_file:
    txt_file = this_file.read()
this_file.close()


@mark.unit
@mark.parsertests
class ParserTests:
    """
    Tests to test the test framework itself.
    ParserTests tests the Cheetah log parser
    in testapps/logparser.py
    """

    def test_not_json_exception(self):
        """
        Checks that excpetion raises when file is not valid JSON file
        """
        with pytest.raises(ValueError):
            LogParse(txt_file)

    def test_search_string(self):
        """
        Checks that expected string is found in messages
        and then that a random string is not found
        """
        logs = LogParse(parser_file)
        msg_ok = logs.search(item="Finished")
        assert msg_ok
        msg_fail = logs.search(item="abc123")
        assert msg_fail is False

    def test_no_errors_in_logfile(self):
        """
        Checks that error logs are empty if no errors
        """
        logs = LogParse(parser_file)
        no_error = logs.errors()
        assert no_error is False

    def test_errors_in_logfile(self):
        """
        Checks that errors are saved when present in log file
        """
        errors = LogParse(error_file)
        with_error = errors.errors()
        assert len(with_error) != 0
