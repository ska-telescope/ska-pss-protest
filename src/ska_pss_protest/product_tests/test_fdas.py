"""
Doc-string placeholder
"""

import os
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from ska_pss_cand_reader import FilterbankFile

from ska_pss_protest import (
    Cheetah,
    DedispersionPlanSelect,
    FdasScl,
    VectorPull,
)

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

    vector_header = FilterbankFile.from_file(request.local_path)

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
    config("sps_clustering/fof_clustering/active", "true")
    config("sps_clustering/fof_clustering/time_tolerance", "10.0")
    config("sps_clustering/fof_clustering/dm_thresh", "10.0")
    config("sps_clustering/fof_clustering/width_matching_factor", "4.0")

    # Set SpSift parameters
    config("spsift/active", "true")
    config("spsift/thresholding/active", "true")
    config("spsift/thresholding/sigma_thresh", "6.0")
    config("spsift/thresholding/dm_thresh", "5.0")
    config("spsift/thresholding/pulse_width_threshold", "1000.0")


@given(
    "A cheetah configuration to configure FPGA-FDAS pipeline and export the FDAS candidate metadata"
)
def set_fpga_fdas_param(config, context):
    """
    Configure the config file to set FPGA-FDAS pipeline parameters
    """
    # Set output location for candidate filterbanks
    config("beams/beam/sinks/channels/search_events/active", "true")
    config("beams/beam/sinks/channels/ocld/active", "true")

    # Set output location for candidate metadata files
    config(
        "beams/beam/sinks/sink_configs/scl_files/dir",
        context["candidate_dir"],
    )
    config(
        "beams/beam/sinks/sink_configs/ocld_files/dir",
        context["candidate_dir"],
    )

    # Configure PSBC and FDAS parameters
    config("psbc/dump_time", "570")
    config("acceleration/fdas/active", "true")
    config("acceleration/fdas/intel_fpga/active", "true")
    config(
        "acceleration/fdas/intel_fpga/filters_filename",
        "/opt/pss-fdas-fpga/etc/template.dat",
    )
    config(
        "acceleration/fdas/intel_fpga/hsum_filename",
        "/opt/pss-fdas-fpga/etc/config_0.3Hz_start.txt",
    )
    # The HSUM config file and filters are stored in ds-psi-worker-1b for time being

    # Configure SIFT and FLDO parameters
    config("sift/strong_sift/active", "true")
    config("sift/strong_sift/num_candidate_harmonics", "8")
    config("sift/strong_sift/match_factor", "0.001")
    config("fldo/cpu/active", "true")


@given(
    "A cheetah configuration to configure CPU-FDAS pipeline and export the FDAS candidate metadata"
)
def set_cpu_fdas_param(config, context):
    """
    Configure the config file to set CPU-FDAS pipeline parameters
    """
    # Set output location for candidate filterbanks
    config("beams/beam/sinks/channels/search_events/active", "true")
    config("beams/beam/sinks/channels/ocld/active", "true")

    # Set output location for candidate metadata files
    config(
        "beams/beam/sinks/sink_configs/scl_files/dir",
        context["candidate_dir"],
    )
    config(
        "beams/beam/sinks/sink_configs/ocld_files/dir",
        context["candidate_dir"],
    )

    # Configure PSBC and FDAS parameters
    config("psbc/dump_time", "570")
    config("acceleration/fdas/active", "true")
    config("acceleration/fdas/labyrinth/active", "true")
    config("acceleration/fdas/labyrinth/threshold", "8.0")

    # Configure SIFT and FLDO parameters
    config("sift/strong_sift/active", "true")
    config("sift/strong_sift/num_candidate_harmonics", "8")
    config("sift/strong_sift/match_factor", "0.001")


def subband_calculator(nchan: int, ratio: int = 80) -> int:
    """
    Calculates the number of subbands to set up FLDO such a way that
    the number of subbands is ~ 80 times smaller than the number of channels
    but is also a factor of total number of channels.
    The number 80, was arbitrarily chosen based on the expected number of channels
    for the test vector and the typical number of subbands used in FDAS.
    This can be adjusted as needed for different test vectors or configurations.
    """

    if nchan <= 0:
        return 0

    target = nchan // ratio
    factors = [i for i in range(1, nchan + 1) if nchan % i == 0]
    best_fit = min(factors, key=lambda x: abs(x - target))

    return best_fit


@given("A cheetah configuration to set up FLDO module")
def set_fldo_parameters(config, context):
    """
    Function to set up FLDO parameters
    """

    config("fldo/cpu/active", "true")
    config(
        "fldo/cpu/number_of_frequency_channels",
        str(context["vector_header"].nchans),
    )
    config("fldo/cpu/number_of_subints", "16")
    config(
        "fldo/cpu/number_of_subbands",
        str(subband_calculator(context["vector_header"].nchans)),
    )
    config("fldo/cpu/number_of_phase_bins", "64")
    config("fldo/cpu/number_of_threads", "8")


@when(parsers.parse("A FDAS pipeline runs using {dedispersion_plan}"))
def run_cheetah(context, config, pytestconfig, dedispersion_plan):
    """
    Set dedispersion buffer length and
    run cheetah pipeline
    """

    # Set number of samples in dedispersion buffer
    context["dd_samples"] = 131072
    root_tree = config("ddtr/dedispersion_samples", str(context["dd_samples"]))

    dd_plan = DedispersionPlanSelect()

    for segment in dd_plan.select(dedispersion_plan):
        dedispersion = et.Element("dedispersion")

        for key, value in segment.items():
            child = et.SubElement(dedispersion, key)
            child.text = str(value)
        root_tree.find("ddtr").append(dedispersion)

    root_tree.write(context["config_path"])

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
    parsers.parse(
        "A FDAS candidates metadata file is produced which is validate using {tol_settings} tolerances"
    )
)
def validate_fdas_candidates(context, pytestconfig, teardown, tol_settings):
    """
    Load the candidate metadata and validate
    the results from cheetah pipeline
    """
    # Load candidate metadata
    scl = FdasScl(context["candidate_dir"])
    scl.from_vector(
        context["test_vector"].local_path,
        context["vector_header"].all_parameters(),
        injection_recovery_factor=0.72,
    )

    scl.search_tol(tol_settings)

    assert scl.detected is True

    # Clean up
    if not pytestconfig.getoption("keep"):
        teardown(context["candidate_dir"])
