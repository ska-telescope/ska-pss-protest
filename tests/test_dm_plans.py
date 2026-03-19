"""
**************************************************************************
|                                                                        |
|                  Unit tests for Dedispersion Plan Selector             |
|                                                                        |
**************************************************************************
| Author: Raghuttam Hombal                                               |
| Email : raghuttamshreepadraj.hombal@manchester.ac.uk                   |
**************************************************************************
| Usage:                                                                 |
|                                                                        |
|  pytest -m ddplantest                                                  |
|      <or>                                                              |
| make test MARK="ddplantest" (recommended)                              |
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

import os

import pytest
from pytest import mark

from ska_pss_protest import DedispersionPlanSelect

# pylint: disable=E1101,W0621,W0104


@mark.unit
@mark.ddplantests
class DDPlanTests:
    """
    Unit tests for Dedispersion Plan Select class
    """

    def test_ddplan_default_file_read(self):
        """
        Test reading OCLD file header
        """
        dd_plan = DedispersionPlanSelect()
        assert dd_plan is not None

    def test_ddplan_no_file(self):
        """
        Test reading non existing file
        """
        filename = "non_existing_file"
        with pytest.raises(expected_exception=FileNotFoundError):
            DedispersionPlanSelect(ddplan_file=filename)

    def test_ddplan_different_file(self):
        """
        Test reading different file
        """
        filename = "tests/data/dummy_dd_plan.json"
        dd_plan = DedispersionPlanSelect(filename)
        assert dd_plan is not None
        assert dd_plan.ddplan_file == filename

    def test_verify_default_ddplan_file(self):
        """
        Checking if default DD plan exist
        """
        dd_plan = DedispersionPlanSelect()
        assert os.path.exists(dd_plan.ddplan_file)

    def test_add_ddplan(self):
        """
        Testing functionality to add ddplan
        """

        dummy_file = "tests/data/dummy_dd_plan.json"
        dd_plan = DedispersionPlanSelect(dummy_file)

        wrong_plan = [{"start": 0, "end": 10, "step": 1}]
        with pytest.raises(ValueError):
            dd_plan.add("dummy", wrong_plan)

        wrong_plan = {"new": [{"start": 0, "end": 10, "step": 1}]}
        with pytest.raises(ValueError):
            dd_plan.add("dummy", wrong_plan)

    def test_get_labels(self):
        """
        Testing the list_label functionality
        """

        dd_plan = DedispersionPlanSelect()

        assert isinstance(dd_plan.list_labels(), list)

    def test_json_to_xml(self):
        """
        Test functionality to get a xml
        """
        plan = [{"start": 0, "end": 10, "step": 1}]
        xml_returned = DedispersionPlanSelect.list_to_xml(plan)

        assert xml_returned is not None

    def test_select_method(self):
        """
        Testing the selection functionality
        """

        dd_plan = DedispersionPlanSelect()
        label = dd_plan.list_labels()[0]

        assert isinstance(dd_plan.select(label), list)
        with pytest.raises(KeyError):
            dd_plan.select("perfect")

    def test_load_from_file(self):
        """
        Testing correct load from file
        """

        dd_plan = DedispersionPlanSelect()
        dd_plan.load_from_file()

    def test_load_from_wrong_file(self):
        """
        Testing loading from incorrect file
        """

        dummy_file = "tests/data/incorrect_json.json"
        with pytest.raises(IOError):
            DedispersionPlanSelect(dummy_file)
