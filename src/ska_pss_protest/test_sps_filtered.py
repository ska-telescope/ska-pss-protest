"""
This product level test and verifies the single-pulse search
(SPS) capability of the PSS pipeline. The test pulls 30 test vectors
from the PSS test vector repository and prepares a config
file which configures cheetah to read in time-frequency data
from the test vector, search it for single pulses, and produce
candidate filterbank files and a candidate metadata file for each
of the 30 test vectors.
"""

import os
import shutil
import tempfile
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, Filterbank, SpCcl, VectorPull, VHeader

# pylint: disable=W0621,W0212,C0116,C0103,C0301

scenarios("features/sps_mid_vector_dm_width_filtered.feature")

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
        "A 60 second duration {test_vector} containing single pulses"
    )
)
def pull_test_vector(context, pytestconfig, test_vector):
    """
    Get test vector and add path to it to the config file
    """
    request = VectorPull(cache_dir=pytestconfig.getoption("cache"))
    request.from_name(test_vector, check_remote=False)

    vector_header = VHeader(request.local_path)

    # Pass parameter from vector to context
    context["test_vector"] = request
    context["vector_header"] = vector_header

    # Verify that the test vector downloaded
    assert os.path.isfile(request.local_path)


@given("A cheetah configuration to ingest the test vector")
def set_source(context, config):
    """
    Set test vector source in cheetah config
    """
    config("beams/beam/source/sigproc/file", context["test_vector"].local_path)
    config_path = os.path.join("/tmp", next(tempfile._get_candidate_names()))
    context["config_path"] = config_path



@given(
    "A cheetah configuration to sift and cluster SPS candidate metadata"
)
def set_config(config, context, pytestconfig):
    # Set location of output files
    outdir = tempfile.mkdtemp(dir=pytestconfig.getoption("outdir"))

    # Set output location for candidate metadata files
    config("beams/beam/sinks/channels/sps_events/active", "true")
    config("beams/beam/sinks/sink_configs/spccl_files/dir", outdir)
    config("beams/beam/sinks/sink_configs/spccl_sigproc_files/dir", outdir)
    context["candidate_dir"] = outdir

    # Set SpCluster parameters
    config("sps_clustering/active", "true")
    config("sps_clustering/time_tolerance", "10.0")

    # Set SpSift parameters
    config("spsift/active", "true")
    config("spsift/sigma_thresh", "6.0")
    config("spsift/dm_thresh", "5.0")
    config("spsift/pulse_width_threshold", "1000.0")


@when("An SPS pipeline runs")
def run_cheetah(context, config, pytestconfig):
    """
    Add SpCcl output directory to config and
    run cheetah
    """
    # Set DDTR Algorithm
    config("ddtr/klotski/active", "true")
    config("ddtr/klotski/precise", "false")
    config("sps/klotski/active", "true")

    # Set number of samples in dedispersion buffer
    context["dd_samples"] = 131072
    config("ddtr/dedispersion_samples", str(context["dd_samples"]))

    # Set SPS S/N threshold
    config("sps/threshold", "6.0").write(context["config_path"])

    # Launch cheetah with our configuration
    cheetah = Cheetah(
        "cheetah_pipeline",
        context["config_path"],
        "sigproc",
        "SinglePulse",
        build_dir=pytestconfig.getoption("path"),
    )
    cheetah.run(timeout=600)
    assert cheetah.exit_code == 0

    # Clean up
    os.remove(context["config_path"])


@then(
    "A candidate metadata file is produced which contains detections of the input signals"
)
def validate_candidate_metadata(context):
    spccl = SpCcl(context["candidate_dir"])

    # Generate list of expected candidates
    spccl.from_vector(context["test_vector"].local_path, context["dd_samples"])
    widths_list = [
        1,
        2,
        4,
        8,
        16,
        32,
        64,
        128,
        512,
        1024,
        2048,
        4096,
        8192,
        15000,
    ]
    spccl.compare_widthstep(context["vector_header"].allpars(), widths_list)

    assert len(spccl.detections) == len(spccl.expected)
    assert len(spccl.non_detections) == 0

    # shutil.rmtree(context["candidate_dir"])
