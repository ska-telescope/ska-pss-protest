#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |                   PSS filterbank/sigproc file reader                   |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | This module provides header information from a sigproc/filterbank      |
    | This code is based on components of the filtools packages              |
    | https://filtools.readthedocs.io/en/latest/                             |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    | Author: Michael Keith                                                  |
    | Email: michael.keith@manchester.ac.uk                                  |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    | from fil import VHeader                                                |
    |                                                                        |
    | filterbank = VHeader(<path to filterbank>)                             |
    |                                                                        |
    | Then to show the duration of the observation, for example:             |
    | print(filterbank.duration()). All other public methods are             |
    | listed below.                                                          |
    |                                                                        |
    | all_pars()                                                             |
    |      A dictionary of all header parameters (dict)                      |
    |                                                                        |
    | machine_id()                                                           |
    |      The identifier of the data taking system (int)                    |
    |                                                                        |
    | tel()                                                                  |
    |      The code used to identify the telescope (str)                     |
    |                                                                        |
    | fch1()                                                                 |
    |      The frequency of the first channel in MHz (float)                 |
    |                                                                        |
    | chbw()                                                                 |
    |      The channel bandwidth in MHz (float)                               |
    |                                                                        |
    | nchans()                                                               |
    |      The number of channels (int)                                      |
    |                                                                        |
    | source_name()                                                          |
    |      The name of the source (for test vectors this is generated        |
    |       by the fast_fake package) (str)                                  |
    |                                                                        |
    | raj()                                                                  |
    |      The source right ascension, as a decimal (float)                  |
    |                                                                        |
    | decj()                                                                 |
    |      The source declination, as a decimal (float)                      |
    |                                                                        |
    | nbits()                                                                |
    |      The number of bits per sample (int)                               |
    |                                                                        |
    | start_time()                                                           |
    |      The MJD of the first sample (float)                               |
    |                                                                        |
    | tsamp()                                                                |
    |      The sample interval (float)                                       |
    |                                                                        |
    | header_size()                                                          |
    |      The size (in bytes) of the header (int)                           |
    |                                                                        |
    | duration()                                                             |
    |      The duration of the observation (float)                           |
    |                                                                        |
    | data_size()                                                            |
    |      The size (in bytes) of the data (int)                             |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2022 University of Manchester                                |
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
    |                                                                        |
    |THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS     |
    |"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       |
    |LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A |
    |PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT      |
    |HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,  |
    |SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT        |
    |LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,   |
    |DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON       |
    |ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR      |
    |TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE  |
    |USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH        |
    |DAMAGE.                                                                 |
    **************************************************************************
"""
import logging
import os

import numpy as np

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)


class VHeader:
    """
    This class reads and parses sigproc file header data

    ...

    Attributes
    ----------
    path : str
        Path to filterbank (sigproc) file
        to be evaluated
    header_pars : dict
        Dictionary containing all header
        parameters of sigproc file
    """

    _inttypes = [
        "machine_id",
        "telescope_id",
        "data_type",
        "nchans",
        "nbits",
        "nifs",
        "scan_number",
        "barycentric",
        "pulsarcentric",
        "nbeams",
        "ibeam",
    ]

    _strtypes = ["source_name", "rawdatafile"]

    _dbltypes = [
        "tstart",
        "tsamp",
        "fch1",
        "foff",
        "refdm",
        "az_start",
        "za_start",
        "src_raj",
        "src_dej",
    ]

    _chrtypes = ["signed"]

    def __init__(self, path):

        self.path = path
        self.header_pars = self._parse(self.path)
        self.signal_pars = self._get_signal_pars(self.path)

    @staticmethod
    def _read_string(infile: str) -> str:
        """
        Extracts all header parameter names from filterbank file
        """
        nchar = np.fromfile(infile, dtype=np.int32, count=1)[0]
        if nchar < 1 or nchar > 80:
            raise Exception(
                "Cannot parse filterbank header (Nchar was {} when reading string).".format(  # noqa
                    nchar
                )
            )
        byte_data = infile.read(nchar)
        string_data = byte_data.decode("UTF-8")
        return string_data

    @staticmethod
    def _get_size(filename: str) -> int:
        """
        Obtains size on disk of filterbank
        """
        stat = os.stat(filename)
        return stat.st_size

    @staticmethod
    def _get_signal_pars(filename: str):
        basename = os.path.splitext(os.path.basename(filename))[0].split("_")
        try:
            signal_pars = {
                "freq": float(basename[2]),
                "width": float(basename[3]),
                "disp": float(basename[4]),
                "sig": float(basename[7]),
            }
            return signal_pars
        except Exception:
            logging.info("Non-standard vector: skipping signal extraction")
            return {}

    @staticmethod
    def _parse(path: str) -> dict:
        """
        Reads header information from filterbank
        and places each key and its value in a dict object.
        """
        header = {}
        fil = open(path, "rb")
        key = VHeader._read_string(fil)
        bytes_read = len(key) + 4

        if key == "HEADER_START":
            key = VHeader._read_string(fil)
            bytes_read = len(key) + 4

            while key != "HEADER_END":
                if key in VHeader._strtypes:
                    header[key] = VHeader._read_string(fil)
                    bytes_read += len(header[key]) + 4
                elif key in VHeader._inttypes:
                    header[key] = np.fromfile(fil, dtype=np.int32, count=1)[0]
                    bytes_read += 4
                elif key in VHeader._dbltypes:
                    header[key] = np.fromfile(fil, dtype=np.float64, count=1)[
                        0
                    ]
                    bytes_read += 8
                elif key in VHeader._chrtypes:
                    header[key] = np.fromfile(fil, dtype=np.int8, count=1)[0]
                    bytes_read += 1
                else:
                    raise Exception(
                        "Cannot parse filterbank header, key '{}' not understood".format(  # noqa
                            key
                        )
                    )

                key = VHeader._read_string(fil)
                bytes_read += len(key) + 4

        header["header_size"] = fil.tell()
        return header

    def allpars(self) -> dict:
        """
        Returns all header parameters as dict
        """
        all_pars = {}
        all_pars.update(self.header_pars)
        all_pars.update(self.signal_pars)
        return all_pars

    def machine_id(self) -> int:
        """
        Returns machine id
        """
        return self.header_pars["machine_id"]

    def tel(self) -> str:
        """
        Returns telescope used to record
        filterbank data
        """
        return self.header_pars["telescope_id"]

    def fch1(self) -> float:
        """
        Returns the frequency of the first channel
        (in MHz)
        """
        return self.header_pars["fch1"]

    def chbw(self) -> float:
        """
        Returns the channel bandwidth
        (in MHz)
        """
        return self.header_pars["foff"]

    def nchans(self) -> int:
        """
        Returns the number of channels
        """
        return self.header_pars["nchans"]

    def source_name(self) -> str:
        """
        Returns the name of the source
        being observed
        """
        return self.header_pars["source_name"]

    def raj(self) -> float:
        """
        Retuns the right ascension of the source
        """
        return self.header_pars["src_raj"]

    def decj(self) -> float:
        """
        Returns the declination of the source
        """
        return self.header_pars["src_dej"]

    def nbits(self) -> int:
        """
        Returns the number of bits per sample
        """
        return self.header_pars["nbits"]

    def start_time(self) -> float:
        """
        Returns the start time of the observation
        """
        return self.header_pars["tstart"]

    def tsamp(self) -> float:
        """
        Returns the sampling interval (s)
        """
        return self.header_pars["tsamp"]

    def header_size(self) -> int:
        """
        Returns the size of the header
        """
        return self.header_pars["header_size"]

    def total_size(self) -> int:
        """
        Obtains size on disk of filterbank
        """
        stat = os.stat(self.path)
        return stat.st_size

    def duration(self) -> float:
        """
        Returns the duration of the observation in seconds
        """
        duration = (
            (self.total_size() - self.header_size()) / self.nchans()
        ) * self.tsamp()
        return duration

    def data_size(self) -> int:
        """
        Returns the size of the data component of
        the filterbank.
        """
        data_size = self.total_size() - self.header_size()
        return data_size

    def nspectra(self) -> int:
        """
        Returns the number of spectra
        (time samples for a single channel)
        """
        return int(self.data_size() / self.nchans())
