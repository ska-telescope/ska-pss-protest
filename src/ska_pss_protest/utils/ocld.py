"""
    **************************************************************************
    |                                                                        |
    |                   PSS OCLD file reader                                 |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | This module provides functions to read OCLD files produced by the      |
    | Cheetah pipeline and extract metadata and data in a structured format. |
    **************************************************************************
    | Author: Raghuttam Hombal                                               |
    | Email : raghuttamshreepadraj.hombal@manchester.ac.uk                   |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2025 University of Manchester                                |
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

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)


class OcldReader:
    """
    This class reads and parses OCLD raw file header data

    ...

    Attributes
    ----------
    path : str
        Path to OCLD raw file
        to be evaluated
    metadata : dict
        Dictionary containing all metadata
        parameters of OCLD raw file
    """

    def __init__(self, path):

        self.path = path
        self.metadata = {}
        self.header_size = 512

    @staticmethod
    def _check_file(path: str) -> bool:
        """
        Checks for the presence of a file on
        the filesystem.

        Parameters
        ----------
        path: str
            Path to file to be checked

        Returns
        -------
        bool
            True if file exists, else False
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {path} not found.")
        return True

    @staticmethod
    def _parse(path: str, header_block_size: int) -> dict:
        """
        Reads header information from OCLD raw file
        and places each key and its value in a dict object.

        Arguments:
        ----------
        path : str
            Path to OCLD raw file
        data_block_size : int
            Size of data block to be read = nsubints * nbands * nbins

        Returns:
        --------
        metadata : dict
            Dictionary containing all metadata
            parameters of OCLD raw file
        """

        metadata = {}

        if not OcldReader._check_file(path):
            raise FileNotFoundError(f"File {path} not found.")

        with open(path, "rb") as f:
            # COUNT:1,NPHASE:128,NSUBBAND:64,NSUBINT:16
            first_header_chunk = f.read(header_block_size)
            first_header_chunk = first_header_chunk.replace(b"\x00", b"")

            first_header_chunk = dict(
                (k, float(v))
                for k, v in (
                    e.split(b":", -1)
                    for e in first_header_chunk.split(b",", -1)
                )
            )
            number_of_cands = int(first_header_chunk[b"COUNT"])
            metadata["nsubints"] = first_header_chunk[b"NSUBINT"]
            metadata["nbands"] = first_header_chunk[b"NSUBBAND"]
            metadata["nphase"] = first_header_chunk[b"NPHASE"]
            data_block_size = (
                metadata["nsubints"]
                * metadata["nbands"]
                * metadata["nphase"]
                * 4  # float32
            )
            metadata["candidates"] = []

            for cand in range(number_of_cands):
                seek_ptr = int((data_block_size + header_block_size) * cand)
                f.seek(seek_ptr)  # Move to candidate header

                metadata_chunk = f.read(header_block_size)
                metadata_chunk = metadata_chunk.replace(b"\x00", b"")
                metadata_chunk = dict(
                    (k, v)
                    for k, v in (
                        e.split(b":") for e in metadata_chunk.split(b",")
                    )
                )

                # Removing unneeded entries
                metadata_chunk.pop(b"COUNT", None)
                metadata_chunk.pop(b"NSUBINT", None)
                metadata_chunk.pop(b"NPHASE", None)
                metadata_chunk.pop(b"NSUBBAND", None)

                metadata["candidates"].append(metadata_chunk)
                # fpp_chunk = np.fromfile(f, dtype=np.float32, count=data_block_size)

        return metadata

    def load_metadata(self, header_block_size: int = 512):
        """
        Loads metadata from OCLD raw file

        Arguments:
        ----------
        header_block_size : int
            Size of header block to be read = 512 bytes (default)

        Returns:
        --------
        """

        self.metadata = self._parse(self.path, header_block_size)
