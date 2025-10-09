"""
Behavioural test of the SPS emulator class.

This test will pull a test vector, edit a
cheetah configuration file to set a candidate
generation rate, deploy a cheetah SPS emulator
pipeline, and verify that the correct number of
candidates are produced.
"""

import os
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, scenarios, then, when

from ska_pss_protest import Cheetah, SpCcl, VectorPull, VHeader

# pylint: disable=W0621,W0212

scenarios("features/sps_emulator.feature")

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


@pytest.fixture(scope="function")
def context():
    """
    Return dictionary containing variables
    to be shared between test stages
    """
    return {}


@pytest.fixture(scope="session")
def get_vector(pytestconfig):
    """
    Uses requester class to obtain test vector.
    """
    vector = VectorPull(cache_dir=pytestconfig.getoption("cache"))
    vector.from_name(
        "SPS-MID_747e95f_0.2_0.0002_2950.0_0.0_Gaussian_50.0_0000_0.0_0.0_123123123.fil"
    )
    yield vector


@pytest.fixture
def config():
    """
    Select a config file template, the values of which
    can be edited for this specific test
    """
    template_path = os.path.join(
        DATA_DIR, "config_templates/sps_pipeline_config_no_export.xml"
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


@given("A 60s test vector containing random noise")
def pull_test_vector(get_vector, config):
    """
    Get test vector and add path to it to the config file
    """
    assert os.path.isfile(get_vector.local_path)
    config("beams/beam/source/sigproc/file", get_vector.local_path)


@given("A candidate generation rate of 1 per second")
def set_rate(context, config):
    """
    Set candidate rate and other pipeline
    properties in cheetah config
    """
    rate = "1"
    context["rate"] = rate
    config("sps/emulator/candidate_rate", rate)
    config("ddtr/dedispersion_samples", "156250")


@when("The SPS pipeline runs")
def run_cheetah(config, outdir, pytestconfig, context, conf):
    """
    Add SpCcl output directory to config and
    run cheetah
    """
    # Set path to output directory
    outdir = outdir(pytestconfig.getoption("outdir"))
    config_path = conf(outdir)

    config("beams/beam/sinks/sink_configs/spccl_files/dir", outdir)
    config(
        "beams/beam/sinks/sink_configs/spccl_sigproc_files/dir", outdir
    ).write(config_path)

    context["candidate_dir"] = outdir

    # Run cheetah pipeline
    cheetah = Cheetah(
        "cheetah_pipeline",
        config_path,
        "sigproc",
        "SinglePulse",
        build_dir=pytestconfig.getoption("path"),
    )
    cheetah.run()
    assert cheetah.exit_code == 0


@then("60 candidates are written to SpCcl file")
def count_cands(context, get_vector):
    """
    Call candidate parser and check number of candidates
    """
    expected_ncands = (
        float(context["rate"]) * VHeader(get_vector.local_path).duration()
    )
    candidate = SpCcl(context["candidate_dir"])
    assert len(candidate.cands) == expected_ncands
