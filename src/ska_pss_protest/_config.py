"""
Helper class to pipeline.py which
will check the user's inputs are
correct for the pipeline they wish
to run and that the required files
exists and have permissions set
correctly.
"""
# pylint: disable=C0209

import logging
import os
from shutil import which

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
    # Is the executable a valid pipeline launcher
    if executable in requirements.keys():
        # Obtain the necessary dict params for the launcher
        args = requirements[executable]

        # If a cheetah build/install directory has been supplied,
        # search it the the launcher
        if cheetah_dir:
            path = search_build(cheetah_dir, executable, args)
        # If no, assume the executable is in the user's $PATH
        else:
            path = search_path(executable)
    else:
        raise EnvironmentError("Pipeline not found")

    # Does the config file exist?
    if not os.path.isfile(config):
        raise FileNotFoundError("Config file {} not found".format(config))

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
    """
    Checks the user's system path to the executable they
    intend to run. If found, the full path is returned,
    else and Exception is raised. 
    """
    # Is the launcher (executable) in the $PATH?
    this_launcher = which(launcher)
    if this_launcher is not None:
        logging.info("Found cheetah launcher: {}".format(this_launcher))
        return this_launcher
    else:
        raise FileNotFoundError("No pipeline launcher in $PATH")


def search_build(cheetah_dir, launcher, launcher_dict):
    """
    If the user has supplied a build/install directory, this
    function will search these paths for the executable they
    wish to run. If found, the full path will be returned, else
    and exception will be raised. The function will first assume
    the path supplied represents a cheetah build tree. If this is
    not the case, the function will assume it is install/bin.
    """

    # Possible paths for the executable, given the launcher name supplied
    install_path = os.path.join(cheetah_dir, launcher)
    build_path = os.path.join(cheetah_dir, launcher_dict["path"])

    # Is a build tree found? If so, return a path to the launcher
    if isfile(build_path):
        isexec(build_path)
        logging.info("Located cheetah executable: {}".format(build_path))
        return build_path
    # Is a bin/ directory found? If so, return a path to the launcher
    elif isfile(install_path):
        isexec(install_path)
        logging.info("Located cheetah executable: {}".format(install_path))
        return install_path
    # Neither are found - raise Exception
    else:
        raise FileNotFoundError("Cannot find executable")
