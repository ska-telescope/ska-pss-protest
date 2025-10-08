"""
This product level test set verifies the single-pulse search
(SPS) capability of the PSS pipeline. The test pulls test vectors
from the PSS test vector repository and prepares a config
file which configures cheetah to read in time-frequency data
from the test vector, search it for single pulses, and produce
candidate filterbank files and a candidate metadata file for each
of the test vectors.

In some of the tests we enable and configure sifting and clustering
algorithms to reduce the number of candidates exported to SDP.
"""

import os
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, Filterbank, SpCcl, VectorPull, VHeader

# pylint: disable=W0621,W0212,C0116,C0103,C0301

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
def pull_test_vector(context, pytestconfig, vector_type, freq, dm, width, sn):
    """
    Get test vector and add path to it to the config file
    """
    test_vector = VectorPull(cache_dir=pytestconfig.getoption("cache"))
    test_vector.from_properties(
        vectype=vector_type, freq=freq, duty=width, disp=dm, sig=sn
    )

    vector_header = VHeader(test_vector.local_path)

    # Pass parameter from vector to context
    context["test_vector"] = test_vector
    context["vector_header"] = vector_header

    # Verify that the test vector downloaded
    assert os.path.isfile(test_vector.local_path)


@given(
    parsers.parse(
        "A 60 second duration {test_vector} containing single pulses"
    )
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
    config("beams/beam/source/sigproc/chunk_samples", "16384")
    context["config_path"] = config_path
    context["candidate_dir"] = outdir


@given(
    "A cheetah configuration to export SPS filterbanked candidate data and SPS candidate metadata"
)
def set_sink(config, context):
    # Set output location for candidate filterbanks
    config("beams/beam/sinks/channels/sps_events/active", "true")
    config(
        "beams/beam/sinks/sink_configs/spccl_sigproc_files/dir",
        context["candidate_dir"],
    )

    # Set output location for candidate metadata files
    config(
        "beams/beam/sinks/sink_configs/spccl_files/dir",
        context["candidate_dir"],
    )


@given(
    "A cheetah configuration to cluster SPS candidate metadata using FOF clustering algorithm"
)
def set_fof_clustering_config(config):
    # Set SpCluster parameters
    config("sps_clustering/active", "true")
    config("sps_clustering/fof_clustering/active", "true")
    config("sps_clustering/fof_clustering/time_tolerance", "100.0")
    config("sps_clustering/fof_clustering/dm_thresh", "50.0")
    config("sps_clustering/fof_clustering/pulse_width_tolerance", "5.0")


@given(
    "A cheetah configuration to cluster SPS candidate metadata using HDBScan clustering algorithm"
)
def set_hdbscan_clustering_config(config):
    # Set SpCluster parameters
    config("sps_clustering/active", "true")
    config("sps_clustering/hdbscan_clustering/active", "true")
    config("sps_clustering/hdbscan_clustering/minimum_cluster_size", "15")


@given(
    "A cheetah configuration to sift SPS candidate metadata using thresholding algorithm"
)
def set_thresholding_sift_config(config):
    # Set SpSift parameters
    config("spsift/active", "true")
    config("spsift/thresholding/active", "true")
    config("spsift/thresholding/sigma_thresh", "6.0")
    config("spsift/thresholding/dm_thresh", "5.0")
    config("spsift/thresholding/pulse_width_threshold", "1000.0")


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


@then(
    "Candidate filterbanks are exported to disk and their header properties are consistent with the test vector"
)
def validate_exported_candidates(context, pytestconfig):
    # Load candidates
    candidates = Filterbank(context["candidate_dir"])
    candidates.get_headers()

    # Get header info from test vector
    input_header = context["vector_header"]

    # Compare expected common properties candidate vectors with input vector
    for header in candidates.headers:
        assert isinstance(header, VHeader)
        assert header.fch1() == input_header.fch1()
        assert header.nspectra() <= input_header.nspectra()
        assert header.nchans() == input_header.nchans()
        assert header.nbits() == input_header.nbits()
        assert header.chbw() == input_header.chbw()
        assert header.tsamp() == input_header.tsamp()
        assert header.start_time() >= input_header.start_time()
        assert header.duration() <= input_header.duration()

    # Replace candidate files with header info only
    if pytestconfig.getoption("reduce"):
        candidates.reduce_headers()


@then(
    "A candidate metadata file is produced which contains detections of the input signals"
)
def validate_candidate_metadata(context, pytestconfig, teardown):
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

    # Clean up
    if not pytestconfig.getoption("keep"):
        teardown(context["candidate_dir"])
