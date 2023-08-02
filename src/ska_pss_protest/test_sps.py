"""
This product level test verifies the ingest and export
capability of the PSS pipeline. The test pulls a test vector
from the PSS test vector repository and prepares a config
file which configures cheetah to read in and export the test vector
as a "candidate" file that has the same duration. Cheetah will
then run an an "empty" pipeline (a pipeline which does not
conduct a search on the input data) and the properties of the
exported candidate are compared to the properties of the input
test vectors.
"""

import os
import shutil
import tempfile
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, Filterbank, VectorPull, VHeader

# pylint: disable=W0621,W0212

scenarios("features/sps_mid_vector_dm_width.feature")

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


@pytest.fixture(scope="function")
def context():
    """
    Return dictionary containing variables
    to be shared between test stages
    """
    return {}


@pytest.fixture(scope="function")
def config():
    """
    Select a config file template, the values of which
    can be edited for this specific test
    """
    template_path = os.path.join(
        DATA_DIR, "config_templates/ingest_export.xml"
    )
    assert os.path.isfile(template_path)
    tree = et.parse(template_path)

    def _edit(tag, value): 
        """
        Replace contents of tag with value
        """
        tree.find(tag).text = value
        return tree

    return _edit


@given(parsers.parse("A 60 second duration {vector_type} containing {freq} pulses per second, each with a dispersion measure of {dm}, a duty cycle of {width} and a combined S/N of {sn}"))
def pull_test_vector(context, vector_type, freq, dm, width, sn):
    """
    Get test vector and add path to it to the config file
    """
    test_vector = VectorPull(cache_dir="/skatvnas3/cache")
    test_vector.from_properties(vectype=vector_type, freq=freq, duty=width, disp=dm, sig=sn)

    vector_header = VHeader(test_vector.local_path)

    # Pass parameter from vector to context
    context["test_vector"] = test_vector 
    context["vector_header"] = vector_header

@given("A cheetah configuration to ingest the test vector")
def set_source(context, config):
    """
    Set test vector source in cheetah config
    """
    pass


@given("A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata")
def set_sink(config, context):
    pass


@when("An SPS pipeline runs")
def run_cheetah(context, pytestconfig):
    """
    Add SpCcl output directory to config and
    run cheetah
    """
    pass


@then(
    "Candidate filterbanks are exported to disk and their header properties are consistent with the test vector"
)
def validate_exported_data(context):
    pass

@then("A candidate metadata file is produced which contains detections of the input signals within tolerances")
def do_last_bit(context):
    pass
