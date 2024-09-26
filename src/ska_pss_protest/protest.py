#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |                   PSS ProTest entrypoint script                        |
    |                                                                        |
    **************************************************************************
    | Description: This file is a command line entrypoint to ProTest -       |
    | the PSS end-to-end product testing framework.                          |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | usage: protest -h                                                      |
    |                                                                        |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2024 SKA Organisation                                        |
    |                                                                        |
    |Redistribution and use in source and binary forms, with or without      |
    |modification, are permitted provided that the following conditions are  |
    |met:                                                                    |
    |                                                                        |
    |1. Redistributions of source code must retain the above copyright       |
    |notice,                                                                 |
    |this list of conditions and the following disclaimer.                   |
    |                                                                        |
    |2. Redistributions in binary form must reproduce the above copyright    |
    |notice, this list of conditions and the following disclaimer in the     |
    |documentation and/or other materials provided with the distribution.    |
    |                                                                        |
    |3. Neither the name of the copyright holder nor the names of its        |
    |contributors may be used to endorse or promote products derived from    |
    |this                                                                    |
    |software without specific prior written permission.                     |
    **************************************************************************
"""

import argparse
import os
import sys
import time
from importlib.metadata import version

import pytest

import ska_pss_protest
from ska_pss_protest.executors._config import set_markers


class ProTest:
    """
    Class to call pytest in order to launch
    PSS product tests
    """

    def __init__(
        self,
        path,
        cache,
        outdir,
        mark=None,
        exclude=None,
        keep=False,
        reduce=False,
        show_help=False,
        show_pytest=False,
        pytest_options=None,
    ):

        self.path = path
        self.mark = mark
        self.exclude = exclude
        self.cache = cache
        self.reduce = reduce
        self.keep = keep
        self.pytest_options = pytest_options

        # Obtain path of protest
        self.src = os.path.dirname(ska_pss_protest.__file__)

        # Show all available markers
        if show_help:
            pytest_args = [
                "-c",
                os.path.join(self.src, "pytest.ini"),
                "--markers",
            ]
            sys.exit(pytest.main(pytest_args))

        # Show all pytest options (runs pytest -h)
        if show_pytest:
            pytest_args = ["-h"]
            sys.exit(pytest.main(pytest_args))

        # Set outputs directory
        if not os.path.isdir(outdir):
            raise FileNotFoundError("{} not found".format(outdir))
        set_dir = "protest-{}".format(time.strftime("%Y%m%d-%H%M%S"))
        self.outdir = os.path.join(outdir, set_dir)

        # Set up markers
        self.markers = set_markers(self.mark, self.exclude)

        self.run()

    def run(self) -> None:
        """
        Main method
        """
        # Get path to pytest.ini
        ini_path = os.path.join(self.src, "pytest.ini")

        marker_string = self.markers

        # Set up path to PSS
        try:
            pss_path = "--path=" + self.path
            pytest_args = [
                "-m",
                f"{marker_string}",
                "-c",
                ini_path,
                pss_path,
                self.src,
            ]
        except TypeError:
            pytest_args = ["-m", f"{marker_string}", "-c", ini_path, self.src]
        if self.cache:
            cache_arg = ["--cache=" + self.cache]
            pytest_args = cache_arg + pytest_args
        if self.outdir:
            outdir_arg = ["--outdir=" + self.outdir]
            pytest_args = outdir_arg + pytest_args
        if self.keep:
            keep_arg = ["--keep"]
            pytest_args = keep_arg + pytest_args
        if self.reduce:
            reduce_arg = ["--reduce"]
            pytest_args = reduce_arg + pytest_args
        if self.pytest_options:
            pytest_args = self.pytest_options + pytest_args
        
        print("Running pytest", " ".join(pytest_args))
        sys.exit(pytest.main(pytest_args))


def main() -> None:
    """
    Entrypoint method
    """
    parser = argparse.ArgumentParser(
        description=f"ProTest - the PSS Product Testing Framework. version: {version('ska_pss_protest')}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    group = parser.add_argument_group("General test settings")
    group.add_argument(
        "--path",
        help="Path to cheetah build tree",
        required=False,
        default=None,
    )
    group.add_argument(
        "--cache",
        help="Directory containing locally stored test vectors (def=~/.cache/SKA/test_vectors)",
        required=False,
        default=None,
    )
    group.add_argument(
        "--outdir",
        help="Directory to store output data products and test results (def=/tmp)",
        required=False,
        default="/tmp",
    )
    group.add_argument(
        "--keep",
        help="Preserve the post-test data products (e.g, candidates, cheetah logs, configs, etc)",
        required=False,
        action="store_true",
    )
    group = parser.add_argument_group("Test selection settings")
    group.add_argument(
        "-i",
        "--include",
        nargs="+",
        help="Include the following test types (def=product)",
        required=False,
    )
    group.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        help="Exclude the following test types",
        required=False,
    )
    group = parser.add_argument_group(
        "Single-pulse search specific test settings"
    )
    group.add_argument(
        "--reduce",
        help="Store only header information from SPS candidate filterbanks",
        required=False,
        action="store_true",
    )
    group = parser.add_argument_group("Help and version info")
    group.add_argument(
        "-H",
        "--show_help",
        help="Show detailed help on test options",
        required=False,
        action="store_true",
    )
    group.add_argument(
        "-P",
        "--show_pytest",
        help="Show help on pytest options (prints output of pytest -h). User can pass any pytest option to protest (use with care!).",
        required=False,
        action="store_true",
    )

    # Allow argparse to handle all the known arguments
    # and set the rest as a list to pass directly to the
    # class
    parsed, unknown = parser.parse_known_args()
    extra_args = [this_arg for this_arg in unknown]

    protest = ProTest(
        parsed.path,
        parsed.cache,
        parsed.outdir,
        parsed.include,
        parsed.exclude,
        parsed.keep,
        parsed.reduce,
        parsed.show_help,
        parsed.show_pytest,
        extra_args,
    )
    protest.run()


if __name__ == "__main__":
    main()
