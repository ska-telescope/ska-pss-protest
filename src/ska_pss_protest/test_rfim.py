"""
This is a product level Single-pulse search test which is used to
test efficacy of RFIM algorithms in Cheetah. It is carried out by
passing RFI-injected test vectors through Cheetah
SPS Pipeline with RFIM algorithms turned ON.
"""

import os
import shutil
import tempfile
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
        "A 60 second duration {vtype} Test-vector containing {freq} single pulses per second, each with a dispersion measure of {dm}, a duty cycle of {width} and folded S/N of {sn} with RFI configuration {rfi}"
    )
)
def pull_test_vector(context, pytestconfig, vtype, freq, dm, width, sn, rfi):
    """
    Get test vector and add path to it to the config file
    """
    test_vector = VectorPull(cache_dir=pytestconfig.getoption("cache"))
    test_vector.from_properties(
        vectype=vtype, freq=freq, duty=width, disp=dm, sig=sn, rfi=rfi
    )

    vector_header = VHeader(test_vector.local_path)

    # Pass parameter from vector to context
    context["test_vector"] = test_vector
    context["vector_header"] = vector_header

    # Verify that the test vector downloaded
    assert os.path.isfile(test_vector.local_path)


@given(
    "A basic cheetah configuration to ingest test vector and export single pulse candidate metadata to file"
)
def set_source_sink(context, config, pytestconfig):
    """
    Sets up basic test vector source-sink as well as
    Clustering-sifting in cheetah config
    """
    config("beams/beam/source/sigproc/file", context["test_vector"].local_path)
    config_path = os.path.join("/tmp", next(tempfile._get_candidate_names()))
    context["config_path"] = config_path

    outdir = tempfile.mkdtemp(dir=pytestconfig.getoption("outdir"))
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


@given(
    parsers.parse(
        "IQRM RFIM enabled with threshold of {threshold} and radius of {radius}."
    )
)
def set_rfim_iqrm(config, threshold, radius):
    """
    Configuring IQRM algorithm using Threshold and Radius from feature file
    """
    config("rfim/rfim_iqrmcpu/active", "true")
    config("rfim/rfim_iqrmcpu/threshold", str(threshold))
    config("rfim/rfim_iqrmcpu/radius", str(radius))


@given(
    parsers.parse(
        "Sum-Threshold RFIM turned on with cutoff equal to {cutoff} and window of {window}."
    )
)
def set_rfim_sumthreshold(config, cutoff, window):
    """
    Configuring Sum-threshold algorithm using Cutoff value and
    Window size from feature file
    """
    config("rfim/rfim_sum_threshold/active", "true")
    config("rfim/rfim_sum_threshold/its_cutoff", str(cutoff))
    config("rfim/rfim_sum_threshold/window", str(window))


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
    cheetah.run(timeout=2000)
    assert cheetah.exit_code == 0

    # Clean up
    os.remove(context["config_path"])


@then("Validate the Candidate metadata file produced")
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

    shutil.rmtree(context["candidate_dir"])
