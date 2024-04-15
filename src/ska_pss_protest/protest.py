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
    | usage: protest [-h] -p PATH [-m MARK]                                  |
    |                                                                        |
    | Run PSS Product Tests                                                  |
    |                                                                        |
    | optional arguments:                                                    |
    |  -h, --help show this help message and exit                            |
    |  -H --show_help Show list of available test markers                    |
    |  -p PATH, --path PATH  Path to cheetah build tree                      |
    |  -i  INCLUDE, --include INCLUDE  Test types to execute                 |
    |        e.g., -i type_a type_b (def=product)                            |
    |  -e EXCLUDE --exclude EXCLUDE  Test types to ignore                    |
    |        e.g., -e type_a type_b                                          |
    |  --outdir OUTDIR  Directory to store candidate data products (def=/tmp)|
    |  --cache CACHE  Directory to read/write local test vector cache        |
    |        (def=/home/<user>/.cache/SKA)                                   |
    |  --keep  Preserve the post-test data products                          |
    |          (e.g, candidates, cheetah logs, configs, etc)                 |
    |  --reduce Store only header information from SPS candidate filterbanks |
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

import pytest

import ska_pss_protest
from ska_pss_protest._config import set_markers


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
    ):

        self.path = path
        self.mark = mark
        self.exclude = exclude
        self.cache = cache
        self.reduce = reduce
        self.keep = keep

        # Obtain path of protest
        self.src = os.path.dirname(ska_pss_protest.__file__)

        # Set outputs directory
        if not os.path.isdir(outdir):
            raise FileNotFoundError("{} not found".format(outdir))
        set_dir = "protest-{}".format(time.strftime("%Y%m%d-%H%M%S"))
        self.outdir = os.path.join(outdir, set_dir)

        if show_help:
            pytest_args = [
                "-c",
                os.path.join(self.src, "pytest.ini"),
                "--markers",
            ]
            sys.exit(pytest.main(pytest_args))

        # Set up markers
        self.markers = set_markers(self.mark, self.exclude)

        self.run()

    def run(self):
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

        print("Running pytest", " ".join(pytest_args))
        sys.exit(pytest.main(pytest_args))


def main():
    """
    Entrypoint method
    """
    parser = argparse.ArgumentParser(description="Run PSS Product Tests")
    parser.add_argument(
        "-H",
        "--show_help",
        help="Show detailed help on test options",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="Path to cheetah build tree",
        required=False,
        default=None,
    )
    parser.add_argument(
        "-i",
        "--include",
        nargs="+",
        help="Include the following test types (def=product)",
        required=False,
    )

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        help="Exclude the following test types",
        required=False,
    )
    parser.add_argument(
        "--cache",
        help="Directory containing locally stored test vectors",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--outdir",
        help="Directory to store candidate data products",
        required=False,
        default="/tmp",
    )
    parser.add_argument(
        "--keep",
        help="Preserve the post-test data products (e.g, candidates, cheetah logs, configs, etc)",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--reduce",
        help="Store only header information from SPS candidate filterbanks",
        required=False,
        action="store_true",
    )
    args = parser.parse_args()

    protest = ProTest(
        args.path,
        args.cache,
        args.outdir,
        args.include,
        args.exclude,
        args.keep,
        args.reduce,
        args.show_help,
    )
    protest.run()


if __name__ == "__main__":
    main()
