"""
Helper class to pipeline.py which
will check the user's inputs are
correct for the pipeline they wish
to run and that the required files
exists and have permissions set
correctly.
"""
# pylint: disable=C0209

from shutil import which
import os
import logging

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

# Cheetah build directory can be set here
BUILD_DIR = None

cheetah_pipeline = {
    "path": "pipelines/search_pipeline/cheetah_pipeline",
    "sources": ["sigproc", "udp_low", "udp"],
    "pipelines": ["SinglePulse", "Empty", "Tdas", "RfiDetectionPipeline"],
}

cheetah_emulator = {
    "path": "emulator/cheetah_emulator",
}

cheetah_candidate_pipeline = {
    "path": "pipelines/candidate_pipeline/cheetah_candidate_pipeline",
    "sources": ["spead"],
    "pipelines": ["empty"],
}

requirements = {
    "cheetah_pipeline": cheetah_pipeline,
    "cheetah_emulator": cheetah_emulator,
    "cheetah_candidate_pipeline": cheetah_candidate_pipeline,
}


def setup_pipeline(
    executable, config, source=None, pipeline=None, cheetah_dir=None
) -> str:

    """
    Checks inputs provided by user make sense and
    are available
    """

    if executable in requirements.keys():
        args = requirements[executable]
        if cheetah_dir:
            path = search_build(cheetah_dir, executable, args)
        else:
            path = search_path(executable)
    else:
        raise EnvironmentError("Pipeline not found")

    # Does the config file exist?
    isfile(config)

    # Is the source in the "allowed" list?
    if "sources" in args:
        if source not in args["sources"]:
            raise KeyError("Source {} not valid".format(source))

    # Is the pipeline in the "allowed" list?
    if "pipelines" in args:
        if pipeline not in args["pipelines"]:
            raise KeyError("Pipeline {} not valid".format(pipeline))

    return path

def isfile(this_file):
    """
    Checks a file exists,
    raises exception if not.
    """
    if os.path.isfile(this_file):
        return True


def isexec(this_file):
    """
    Checks a file is executable,
    raises exception if not.
    """
    if not os.access(this_file, os.X_OK):
        raise PermissionError("{} not executable".format(this_file))

def search_path(launcher):
    # Is the launcher (executable) in the $PATH?
    this_launcher = which(launcher)
    if this_launcher is not None:
        logging.info("Found cheetah launcher: {}".format(this_launcher))
        return this_launcher
    else:
        raise FileNotFoundError("No pipeline launcher in $PATH")

def search_build(cheetah_dir, launcher, launcher_dict):
    install_path = os.path.join(cheetah_dir, launcher)
    build_path = os.path.join(cheetah_dir, launcher_dict['path'])
    if isfile(build_path):
        logging.info("Located cheetah executable: {}".format(build_path))
        return build_path
    if isfile(install_path):
        logging.info("Located cheetah executable: {}".format(install_path))
        return install_path
    else:
        raise FileNotFoundError("Cannot find executable")
