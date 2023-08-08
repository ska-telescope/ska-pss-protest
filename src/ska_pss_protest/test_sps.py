"""
Module docstring placeholder
"""

import os
import tempfile
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, Filterbank, SpCcl, VectorPull, VHeader

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
        DATA_DIR, "config_templates/mid_single_beam.xml"
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


@given(
    parsers.parse(
        "A 60 second duration {vector_type} containing {freq} pulses per second, each with a dispersion measure of {dm}, a duty cycle of {width} and a combined S/N of {sn}"
    )
)
def pull_test_vector(context, vector_type, freq, dm, width, sn):
    """
    Get test vector and add path to it to the config file
    """
    test_vector = VectorPull(
        cache_dir="/home/benshaw/.cache/SKA/test_vectors/temp"
    )
    test_vector.from_properties(
        vectype=vector_type, freq=freq, duty=width, disp=dm, sig=sn
    )

    vector_header = VHeader(test_vector.local_path)

    # Pass parameter from vector to context
    context["test_vector"] = test_vector
    context["vector_header"] = vector_header

    # Verify that the test vector downloaded
    assert os.path.isfile(test_vector.local_path)


@given("A cheetah configuration to ingest the test vector")
def set_source(context, config):
    """
    Set test vector source in cheetah config
    """
    config("beams/beam/source/sigproc/file", context["test_vector"].local_path)
    config_path = os.path.join("/tmp", next(tempfile._get_candidate_names()))
    context["config_path"] = config_path


@given(
    "A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata"
)
def set_sink(config, context):

    # Set output location for candidate filterbanks
    outdir = tempfile.mkdtemp()
    config("beams/beam/sinks/sink_configs/sigproc/dir", outdir)

    # Set output location for candidate metdata files
    config("beams/beam/sinks/sink_configs/sp_candidate_data/dir", outdir)
    context["candidate_dir"] = outdir


@when("An SPS pipeline runs")
def run_cheetah(context, config, pytestconfig):
    """
    Add SpCcl output directory to config and
    run cheetah
    """
    # Set DDTR Algorithm
    config("ddtr/klotski_bruteforce/active", "true")
    config("sps/klotski_bruteforce/active", "true").write(
        context["config_path"]
    )

    # Launch cheetah with our configuration
    cheetah = Cheetah(
        "cheetah_pipeline",
        context["config_path"],
        "sigproc",
        "SinglePulse",
        build_dir=pytestconfig.getoption("path"),
    )
    cheetah.run()
    assert cheetah.exit_code == 0

    # Clean up
    os.remove(context["config_path"])


@then(
    "Candidate filterbanks are exported to disk and their header properties are consistent with the test vector"
)
def validate_exported_candidates(context):
    # Load candidates
    candidates = Filterbank(context["candidate_dir"])
    candidates.get_headers()

    # Get header info from test vector
    input_header = context["vector_header"]

    # Compare expected common properties candidate vectors with input vector
    for header in candidates.headers:
        assert isinstance(header, VHeader)
        assert header.fch1() == input_header.fch1()
        assert header.nchans() == input_header.nchans()
        assert header.nbits() == input_header.nbits()
        assert header.chbw() == input_header.chbw()
        assert header.tsamp() == input_header.tsamp()
        assert header.start_time() >= input_header.start_time()


@then(
    "A candidate metadata file is produced which contains detections of the input signals within tolerances"
)
def validate_candidate_metadata(context):
    cand_metadata = SpCcl(context["candidate_dir"])
    assert cand_metadata
