#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |                   PSS Candidate Filterbank parser                      |
    |                                                                        |
    **************************************************************************
    | Description: This is a PSS testing framework backend application that  |
    | handles the parsing and verification of candidate filterbank data from |
    | the SPS search pipelines.                                              |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    | from candidate import Filterbank                                       |
    | candidates = Filterbank(<candidate_directory>, extension=<extension>)  |
    |                                                                        |
    | where <candidate_directory> is the path to the directory containing    |
    | candidate filterbanks that have been exported by the PSS pipeline, and |
    | <extension> is the file extension of the files in <candidate_directory>|
    | (default is .fil).                                                     |
    |                                                                        |
    | candidates.get_header() will return a list of VHeader objects.         |
    | see protest/fil.py for information on the VHeader class (its basic     |
    | purpose is to explore the header (and other) properties of a           |
    | filterbank file). The header properties of all of the candidate        |
    | filterbanks can be compared with those associated with the input data  |
    | (typically a PSS test vector).                                         |
    |                                                                        |
    | candidates.compare_data(<test_vector>, chunk_samples=<chunk_samples>)  |
    | will conduct a bitwise comparison of the data in a candidate           |
    | filterbank and compare the values, in chunks of <chunk_samples> to     |
    | the data in the input data (typically a PSS test vector). If a         |
    | difference is found in any chunk, the method will return False.        |
    | As this is a direct comparison (basically a diff), an exception will   |
    | be raised if multiple (> 1) candidates are found in <candidate_dir>.   |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2023 SKA Organisation                                        |
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

import logging
import os

import numpy as np

from ska_pss_protest.fil import VHeader

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

# pylint: disable=C0301,W1202,C0209,W0703,W0631,C0103,R0914


class Filterbank:
    """
    Parses candidate data products from PSS pipelines

    Parameters
    ----------
    cand_dir : str
        Directory containing candidate filterbanks

    extension : str
        File extention of candidate filterbanks
    """

    def __init__(self, cand_dir=None, extension=".fil"):

        self.cand_dir = cand_dir
        self.extension = extension
        self.headers = None
        self.result = False

        # Have we set a cand dir?
        if not self.cand_dir:
            raise OSError("No candidate directory specified")
        # Does the candidate dir exist on the filesystem?
        if not os.path.isdir(self.cand_dir):
            raise OSError("No such directory: {}".format(self.cand_dir))

        self.files = self._get_files(self.cand_dir, self.extension)

    @staticmethod
    def _get_files(location, ext) -> list:
        """
        Returns a list of files in a directory
        with a particular extension

        Parameters
        ----------
        location : str
            path to directory containing candidate filterbanks

        ext : str
            extension of files to return
        """
        files = []
        for this_file in os.listdir(location):
            if this_file.endswith(ext):
                files.append(os.path.join(location, this_file))
        if len(files) == 0:
            raise FileNotFoundError(
                "No candidates found in {}".format(location)
            )
        logging.info("Detected {} candidate filterbanks".format(len(files)))
        return files

    def get_headers(self) -> list:
        """
        Provides a list of VHeader objects, each of which
        contains header parameters for candidate filterbank
        files found in self.cand_dir

        Returns
        -------
        Header data : list
            List of objects, one element for each
            filterbank
        """
        self.headers = []
        for this_file in self.files:
            this_header = VHeader(this_file)
            self.headers.append(this_header)
        return self.headers

    def compare_data(self, truth_vector, chunk_size=1024) -> bool:
        """
        Compares the data components of two filterbanks.
        This happens in blocks, the size of which is
        specified by the user.

        Parameters
        ----------
        truth : str
            Path to the test vector

        chunk_size : int
            Number of samples to read in at a time from
            each filterbank

        Returns
        ------
        Result : bool
           False if data components of files differ, else True
        """

        # Check chunk size makes sense
        if chunk_size < 1:
            raise ValueError("Chunk size less than minimum value (1)")

        if not isinstance(chunk_size, int):
            raise TypeError("Chunk size must be integer")

        # Extract header info from candidate filterbank
        headers = self.get_headers()
        if len(headers) != 1:
            raise IOError("Cannot compare multiple filterbanks to one")
        header = headers[0]

        # Get truth header size, open file, and seek to that position in stream
        truth_header = VHeader(truth_vector)
        truth = open(truth_vector, "rb")
        truth.seek(truth_header.header_size())

        # Get candidate header size, open file,
        # and seek to that position in stream
        candidate_header_size = header.header_size()
        this_candidate = open(self.files[0], "rb")
        this_candidate.seek(candidate_header_size)

        # Check number of channels match  between files
        if header.nchans() != truth_header.nchans():
            raise IndexError(
                "Filterbanks have different numbers of channels. {} vs. {}".format(  # noqa
                    header.nchans(), truth_header.nchans()
                )
            )

        nbytes = int(chunk_size * header.nchans())

        cand_samples = 0
        truth_samples = 0

        # Loop through files in batches of chunk_samples * nchans
        # and exit if batches differ
        logging.info("Conducting bitwise search.....")
        while True:
            cand_raw = np.fromfile(
                this_candidate, dtype=np.uint8, count=nbytes
            )
            cand_channelised = cand_raw.reshape(-1, header.nchans()).astype(
                np.uint8
            )
            if cand_raw.shape[0] == 0:
                pass

            truth_raw = np.fromfile(truth, dtype=np.uint8, count=nbytes)
            truth_channelised = truth_raw.reshape(
                -1, truth_header.nchans()
            ).astype(np.uint8)
            if truth_raw.shape[0] == 0:
                break

            cand_samples += len(cand_raw)
            truth_samples += len(truth_raw)

            if not np.all(truth_channelised == cand_channelised):
                logging.info(
                    "Difference detected in bitwise search. Files differ"
                )
                return self.result

        # Double check we counted the same number of
        # samples from each file
        if cand_samples != truth_samples:
            logging.info("Different numbers of samples processed")
            return self.result

        logging.info(
            "Files identical. Samples processed: {}".format(truth_samples)
        )
        self.result = True
        return self.result
