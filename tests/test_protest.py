import ska_pss_protest
from ska_pss_protest._config import set_markers
import pytest
from pytest import mark

@mark.unit
class ProtestTests:

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
        assert set_markers(["sps", "low"], ["sps", "low"]) == "sps and low and not sps and not low" 

        # ProTest doesn't care if the tests requested/excluded do not represent valid markers.
        # It will pass them to pytest anyway. Pytest will simply not execute any tests for that
        # marker as there won't be any!
        assert set_markers(["foo", "bar"], ["sdfgh"]) == "foo and bar and not sdfgh" 

        # For sanity, test a negative scenario
        assert set_markers(["physhw"], ["container"]) != "container and not physhw"
        assert set_markers(["physhw"], ["container"]) == "physhw and not container"
