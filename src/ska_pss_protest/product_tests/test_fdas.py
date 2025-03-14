"""
Doc-string placeholder
"""

import os
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, FdasScl, VectorPull, VHeader

# pylint: disable=W0621,W0212,C0116,C0103,C0301

scenarios("features/fdas_mid_vector.feature")

DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


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

    def _edit(tag, value):
        """
        Replace contents of tag with value
        """
        tree.find(tag).text = value
        return tree

    return _edit


@given(
    parsers.parse("A 600 second duration {test_vector} containing a pulsar")
)
def pull_test_vector_using_name(context, pytestconfig, test_vector):
    """
    Get test vector and add path to it to the config file
    """
    request = VectorPull(cache_dir=pytestconfig.getoption("cache"))
    request.from_name(test_vector)

    vector_header = VHeader(request.local_path)

    # Pass parameter from vector to context
    context["test_vector"] = request
    context["vector_header"] = vector_header

    # Verify that the test vector downloaded
    assert os.path.isfile(request.local_path)


@given("A cheetah configuration to ingest the test vector")
def set_source(context, config, pytestconfig, conf, outdir):
    """
    Set test vector source in cheetah config
    """
    outdir = outdir(pytestconfig.getoption("outdir"))
    config_path = conf(outdir)

    config("beams/beam/source/sigproc/file", context["test_vector"].local_path)
    context["config_path"] = config_path
    context["candidate_dir"] = outdir


@given(
    "A cheetah configuration to configure SPS pipeline and export the SPS candidate metadata"
)
def set_sps_param(config, context):
    """
    Configure the config file to set SPS pipeline parameters
    """
    # Set output location for candidate metadata files
    config("beams/beam/sinks/channels/sps_events/active", "true")

    config(
        "beams/beam/sinks/sink_configs/spccl_files/dir",
        context["candidate_dir"],
    )

    # Configure DDTR and SPS parameters
    config("ddtr/klotski/active", "true")
    config("ddtr/klotski/precise", "false")
    config("sps/klotski/active", "true")
    config("sps/threshold", "6.0").write(context["config_path"])

    # Set SpCluster parameters
    config("sps_clustering/active", "true")
    config("sps_clustering/time_tolerance", "100.0")
    config("sps_clustering/dm_thresh", "5.0")
    config("sps_clustering/pulse_width_tolerance", "50.0")

    # Set SpSift parameters
    config("spsift/active", "true")
    config("spsift/sigma_thresh", "6.0")
    config("spsift/dm_thresh", "5.0")
    config("spsift/pulse_width_threshold", "1000.0")


@given(
    "A cheetah configuration to configure CPU-FDAS pipeline and export the FDAS candidate metadata"
)
def set_fdas_param(config, context):
    """
    Configure the config file to set FDAS pipeline parameters
    """
    # Set output location for candidate filterbanks
    config("beams/beam/sinks/channels/search_events/active", "true")

    # Set output location for candidate metadata files
    config(
        "beams/beam/sinks/sink_configs/scl_files/dir",
        context["candidate_dir"],
    )

    # Configure PSBC and FDAS parameters
    config("psbc/dump_time", "540")
    config("acceleration/fdas/active", "true")
    config("acceleration/fdas/labyrinth/active", "true")
    config("acceleration/fdas/labyrinth/threshold", "8.0")

    # Configure SIFT and FLDO parameters
    config("sift/simple_sift/active", "true")
    config("sift/simple_sift/num_candidate_harmonics", "8")
    config("sift/simple_sift/match_factor", "0.001")
    config("fldo/cpu/active", "true")


@when("A FDAS pipeline runs")
def run_cheetah(context, config, pytestconfig):
    """
    Set dedispersion buffer length and
    run cheetah pipeline
    """

    # Set number of samples in dedispersion buffer
    context["dd_samples"] = 131072
    config("ddtr/dedispersion_samples", str(context["dd_samples"]))

    # Launch cheetah with our configuration
    cheetah = Cheetah(
        "cheetah_pipeline",
        context["config_path"],
        "sigproc",
        "Fdas",
        build_dir=pytestconfig.getoption("path"),
    )
    cheetah.run(timeout=4800)
    assert cheetah.exit_code == 0


@then(
    "A FDAS candidates metadata file is produced wich contains detections of the input signals"
)
def validate_fdas_candidates(context, pytestconfig, teardown):
    """
    Load the candidate metadata and validate
    the results from cheetah pipeline
    """
    # Load candidate metadata
    scl = FdasScl(context["candidate_dir"])
    scl.from_vector(context["test_vector"].local_path)

    scl.search_dummy()

    assert scl.detected is True

    # Clean up
    if not pytestconfig.getoption("keep"):
        teardown(context["candidate_dir"])
