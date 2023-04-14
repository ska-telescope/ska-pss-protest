#!/usr/bin/env python

"""
Helper class to pipeline.py which
will check the user's inputs are
correct for the pipeline they wish
to run and that the required files
exists and have permissions set
correctly.
"""
# pylint: disable=C0209

import os

# Cheetah build directory can be set here
BUILD_DIR = None

cheetah_pipeline = {
    "path": "pipeline/cheetah_pipeline",
    "sources": ["sigproc", "udp_low", "udp"],
    "pipelines": ["SinglePulse", "Empty", "Tdas", "RfiDetectionPipeline"],
}

cheetah_emulator = {
    "path": "emulator/cheetah_emulator",
}

cheetah_candidate_pipeline = {
    "path": "candidate_pipeline/cheetah_candidate_pipeline",
    "sources": ["spead"],
    "pipelines": ["empty"],
}

requirements = {
    "cheetah_pipeline": cheetah_pipeline,
    "cheetah_emulator": cheetah_emulator,
    "cheetah_candidate_pipeline": cheetah_candidate_pipeline,
}


def setup_pipeline(
    executable, config, source=None, pipeline=None, build_dir=None
) -> str:

    """
    Checks inputs provided by user make sense and
    are available
    """

    # Have we set the build directory for cheetah?
    if not build_dir:
        build_dir = set_build()

    # Does the executable exist?
    if executable in requirements.keys():
        args = requirements[executable]
        path = os.path.join(build_dir, args["path"])
        isfile(path)
        isexec(path)
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
    if not os.path.isfile(this_file):
        raise FileNotFoundError("{} not found".format(this_file))


def isexec(this_file):
    """
    Checks a file is executable,
    raises exception if not.
    """
    if not os.access(this_file, os.X_OK):
        raise PermissionError("{} not executable".format(this_file))


def set_build():
    """
    Sets the cheetah build directory if not
    provided as argument to pipeline
    """

    # Is the build directory set above?
    if BUILD_DIR:
        return BUILD_DIR
    try:
        # Is the build directory set in env?
        build_dir = os.environ["CHEETAH_BUILD"]
        return build_dir
    except KeyError:
        pass
    # Build dir isn't set anywhere so cheetah cannot
    # be found - raise exception.
    raise EnvironmentError("Cheetah build dir not found")
