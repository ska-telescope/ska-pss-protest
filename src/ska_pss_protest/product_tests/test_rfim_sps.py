"""
This is a product level Single-pulse search test which is used to
test efficacy of RFIM algorithms in Cheetah. It is carried out by
passing RFI-injected test vectors through Cheetah
SPS Pipeline with RFIM algorithms turned ON.
"""

import logging
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
        DATA_DIR, "config_templates/mid_single_beam.xml"
    )
    assert os.path.isfile(template_path)
    tree = et.parse(template_path)
    root = tree.getroot()
    for sink in root.findall("beams/beam/sinks/channels/sps_events/"):
        if sink.tag == "sink":
            if sink.find("id").text == "candidate_files":
                root.find("beams/beam/sinks/channels/sps_events").remove(sink)

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
def set_source_sink(context, config, pytestconfig, conf, outdir):
    """
    Sets up basic test vector source-sink as well as
    Clustering-sifting in cheetah config
    """
    config("beams/beam/source/sigproc/file", context["test_vector"].local_path)
    config("beams/beam/source/sigproc/chunk_samples", "16384")

    outdir = outdir(pytestconfig.getoption("outdir"))
    config_path = conf(outdir)
    context["config_path"] = config_path
    context["candidate_dir"] = outdir

    config("beams/beam/sinks/channels/sps_events/active", "true")
    config(
        "beams/beam/sinks/sink_configs/spccl_files/dir",
        context["candidate_dir"],
    )

    config("sps_clustering/active", "true")
    config("sps_clustering/fof_clustering/active", "true")
    config("sps_clustering/fof_clustering/time_tolerance", "100.0")
    config("sps_clustering/fof_clustering/dm_thresh", "5.0")
    config("sps_clustering/fof_clustering/pulse_width_tolerance", "50.0")

    config("spsift/active", "true")
    config("spsift/thresholding/active", "true")
    config("spsift/thresholding/sigma_thresh", "6.0")
    config("spsift/thresholding/dm_thresh", "5.0")
    config("spsift/thresholding/pulse_width_threshold", "1000.0")


@given(
    parsers.parse(
        "IQRM RFIM enabled with threshold of {threshold} and radius of {radius}"
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
        "Sum-Threshold RFIM enabled with cutoff of {cutoff} and window size of {window}"
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


@given(
    parsers.parse(
        "IQRM RFIM enabled with threshold of {threshold} and radius of {radius} with Zdot"
    )
)
def set_rfim_iqrm_zdot(config, threshold, radius):
    """
    Configuring IQRM algorithm using Threshold and Radius, and Z-dot from feature file
    """
    config("rfim/rfim_iqrmcpu/active", "true")
    config("rfim/rfim_iqrmcpu/threshold", str(threshold))
    config("rfim/rfim_iqrmcpu/radius", str(radius))
    config("rfim/rfim_zdot/active", "true")


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
    root_tree = config("ddtr/dedispersion_samples", str(context["dd_samples"]))
    # read the root tree for trial widths

    widths_element = root_tree.find("sps/klotski/widths")
    trial_widths = []
    if widths_element is not None:
        widths_string = widths_element.text.strip()
        for r in widths_string.split(","):
            trial_widths.append(int(r))
    else:
        logging.info("Search width not selected")

    context["trial_width"] = trial_widths

    # Get the dedispersion plan and downsampling from config
    dedispersion_elements = root_tree.findall("ddtr/dedispersion")
    dm_plan = []
    i = 0
    for element in dedispersion_elements:
        dm_plan.append(
            [
                float(element.find("start").text),
                float(element.find("end").text),
                2**i,
            ]
        )
        i = i + 1

    # read dedispersion plan

    context["dm_plan"] = dm_plan

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


@then(
    "all injected pulses are recovered according the candidate metadata produced"
)
def validate_candidate_metadate(context, pytestconfig, teardown):
    """
    Validating SPS Candidates
    """
    spccl = SpCcl(context["candidate_dir"])

    spccl.from_vector(context["test_vector"].local_path, context["dd_samples"])

    spccl.compare_widthstep(
        context["vector_header"].allpars(),
        context["trial_width"],
        context["dm_plan"],
    )
    if pytestconfig.getoption("keep"):
        spccl.summary_export(context["vector_header"].allpars())

    assert len(spccl.detections) == len(spccl.expected)
    assert len(spccl.non_detections) == 0

    # Clean up
    if not pytestconfig.getoption("keep"):
        teardown(context["candidate_dir"])
