"""
This is a product level Single-pulse search test which is used to 
test efficacy of already implemented RFIM algorithms in Cheetah. 
It is carried out by passing RFI-injected test vectors through Cheetah
SPS Pipeline with RFIM algorithms turned ON.
"""
import os
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, SpCcl, VectorPull, VHeader

# pylint: disable=W0621,W0212,C0116,C0103,C0301

scenarios("features/sps_mid_rfim.feature")
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
        DATA_DIR, "config_templates/mid_single_rfim.xml"
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
    parsers.parse("Given A 60 second {test_vector} containing single pulses")
)
def pull_test_vector_using_name(context, pytestconfig, test_vector):
    """
    Get test vector and add path to it to the config file
    """
    request = VectorPull(cache_dir=pytestconfig.getoption("cache"))
    request.from_name(test_vector)

    vector_header = VHeader(request.local_path)

    context["test_vector"] = request
    context["vector_header"] = vector_header

    assert os.path.isfile(request.local_path)


@given(
    "A basic cheetah configuration to ingest test vector and write single pulses candidate file"
)
def set_source_sink(context, config, pytestconfig):
    """
    Sets up basic test vector source-sink as well as 
    Clustering-sifting in cheetah config
    """
    config("beams/beam/source/sigproc/file", context["test_vector"].local_path)
    config_path = "tmp/"
    context["config_path"] = config_path

    os.mkdir(pytestconfig.getoption("outdir"))
    outdir = pytestconfig.getoption("outdir")
    config("beams/beam/sinks/channels/sps_events/active", "true")
    config("beams/beam/sinks/sink_configs/spccl_files/dir", outdir)
    context["candidate_dir"] = outdir

    config("sps_clustering/active", "true")
    config("sps_clustering/time_tolerance", "100.0")
    config("sps_clustering/dm_thresh", "5.0")
    config("sps_clustering/pulse_width_tolerance", "50.0")

    config("spsift/active", "true")
    config("spsift/sigma_thresh", "6.0")
    config("spsift/dm_thresh", "5.0")
    config("spsift/pulse_width_threshold", "1000.0")


@given("IQRM RFIM turned on with some threshold 3.0")
def set_rfim_iqrm(config):
    """
    Configuring IQRM algorithm
    """
    config("rfim/rfim_iqrmcpu/active", "true")
    config("rfim/rfim_iqrmcpu/threshold", "3.0")


@when("An SPS pipeline runs")
def run_cheetah(context, config, pytestconfig):
    """
    Add SpCcl output directory to config and
    run cheetah
    """
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


@then(
    "Candidate metadata file is produced which contains detections of input signals"
)
def validate_candidate_metadate(context):
    """
    Validating SPS Candidates
    """
    spccl = SpCcl(context["candidate_dir"])

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
        256,
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
