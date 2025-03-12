import os
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, Filterbank, FdasScl, VectorPull, VHeader

# pylint: disable=W0621,W0212,C0116,C0103,C0301

scenarios("features/fdas_mid_vector.feature")

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data")

@pytest.fixture(scope="function")
def context():
    """
    Return dictionary containing variables
    to be shared between various test stages
    """
    return {}

@pytest.fixture(scope="function")
def config():
    """
    Select a config file template, whose values
    can be edited based on the test
    """
    template_path = os.path.join(
        DATA_DIR, "config_templates/mid_single_beam.xml"
    )
    assert os.path.isfile(template_path)
    tree = et.parse(template_path)
    root = tree.getroot()
    for sink in root.findall("beams/beam/sinks/channels/sps_events/"):
        if sink.tag == "sink":
            if sink.find("id").text == "candidate_files":
                # Disabling filterbank candidates outputs from SPS
                root.find("beams/beam/sinks/channels/sps_events").remove(sink)

    def _edit(tag,value):
        """
        Replace contents of tag with value
        """
        tree.find(tag).text = value
        return tree
    
    return _edit