"""
This product level test verifies the ingest and export
capability of the PSS pipeline. The test pulls a test vector
from the PSS test vector repository and prepares a config
file which configures cheetah to read in and export the test vector
as a "candidate" file that has the same duration. Cheetah will
then run an an "empty" pipeline (a pipeline which does not
conduct a search on the input data) and the properties of the
exported candidate are compared to the properties of the input
test vectors.
"""

import os
import shutil
import tempfile
from xml.etree import ElementTree as et

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from ska_pss_protest import Cheetah, Filterbank, VectorPull, VHeader

# pylint: disable=W0621,W0212

scenarios("features/ingest_export.feature")

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
        DATA_DIR, "config_templates/ingest_export.xml"
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


@given(parsers.parse("A PSS {test_vector}"))
def pull_test_vector(context, test_vector):
    """
    Get test vector and add path to it to the config file
    """
    vector = VectorPull()
    # vector.from_name("SPS-MID_747e95f_0.2_0.0002_2950.0_0.0_Gaussian_50.0_123123123.fil")
    vector.from_name(test_vector)
    context["vector_path"] = vector.local_path
    assert os.path.isfile(vector.local_path)


@given("A cheetah configuration to ingest the test vector")
def set_source(context, config):
    """
    Set test vector source in cheetah config
    """
    config("beams/beam/source/sigproc/file", context["vector_path"])


@given("A cheetah configuration to export filterbanked data")
def set_sink(config, context):
    spectra_per_file = str(VHeader(context["vector_path"]).nspectra())
    outdir = tempfile.mkdtemp()
    config_path = os.path.join("/tmp", next(tempfile._get_candidate_names()))
    config("beams/beam/sinks/sink_configs/sigproc/dir", outdir)
    config(
        "beams/beam/sinks/sink_configs/sigproc/spectra_per_file",
        spectra_per_file,
    ).write(config_path)
    context["config_path"] = config_path
    context["candidate_dir"] = outdir


@when("The cheetah pipeline runs")
def run_cheetah(context, pytestconfig):
    """
    Add SpCcl output directory to config and
    run cheetah
    """
    cheetah = Cheetah(
        "cheetah_pipeline",
        context["config_path"],
        "sigproc",
        "Empty",
        build_dir=pytestconfig.getoption("path"),
    )
    cheetah.run()
    assert cheetah.exit_code == 0

    # Clean up
    os.remove(context["config_path"])


@then(
    "The exported filterbank data is identical to the ingested filterbank data"
)
def validate_exported_data(context):
    candidates = Filterbank(context["candidate_dir"])

    # Check header parameters correspond
    # to those in the test vector
    candidates.get_headers()
    assert len(candidates.headers) == 1
    header = candidates.headers[0]
    input_header = VHeader(context["vector_path"])
    assert header.fch1() == input_header.fch1()
    assert header.nchans() == input_header.nchans()
    assert header.nbits() == input_header.nbits()
    assert header.chbw() == input_header.chbw()
    assert header.tsamp() == input_header.tsamp()
    assert header.nspectra() == input_header.nspectra()
    assert header.start_time() == input_header.start_time()
    assert header.duration() == input_header.duration()

    # Run bitwise search through filterbanks
    # and compare values
    candidates.compare_data(context["vector_path"], 4096)
    assert candidates.result is True

    # Clean up
    shutil.rmtree(context["candidate_dir"])
