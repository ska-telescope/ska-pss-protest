#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |                       PSS Candidate parser                             |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    **************************************************************************
    | Usage: TBC                                                             |
    |                                                                        |
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

from ska_pss_protest.fil import VHeader

np.set_printoptions(precision=17)

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

# pylint: disable=C0301,W1202,C0209,W0703,W0631,C0103


class SpCcl:
    """
    Parses metadata products from the single pulse search
    (SPS) pipeline.

    Parameters
    ----------
    spccl_dir: str
        Path to directory containing SPS metadata file
    extention: str
        Expected file extention of SPS metadata file
    """

    def __init__(self, spccl_dir=None, extension=".spccl"):

        self.spccl_dir = spccl_dir
        self.extension = extension

        # Have we set a spccl dir?
        if not self.spccl_dir:
            raise OSError("No candidate directory specified")
        # Does the spccl dir exist on the filesystem?
        if not os.path.isdir(self.spccl_dir):
            raise OSError("No such directory: {}".format(self.spccl_dir))

        self.detections = []
        self.non_detections = []

        # Get list of cands from file in spccl directory
        self.cands = self._get_cands(self.spccl_dir, self.extension)
        self.expected = None

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
            return False
        return True

    @staticmethod
    def _get_cands(spccl_dir: str, ext: str) -> list:
        """
        Look up cands file in spccl directory,
        and process each line as a candidate, return
        candidates as an array timestamp, DM, width
        and S/N values. One row for each candidate.

        Parameters
        ----------
        spccl_dir: str
            Directory expected to contain
            candidate metadata file

        ext: str
            Extension of candidate metadata file

        Returns
        -------
        cand_metadata: numpy.ndarray
           MxN array containing M candidates
           each with N properties (nominally 4)
        """
        # Get name of metadata file from spccl_dir
        files = []
        for this_file in os.listdir(spccl_dir):
            if this_file.endswith(ext):
                files.append(this_file)
        # Do we only have one candidate metadata file?
        if len(files) == 1:
            cand_file = os.path.join(spccl_dir, files[0])
            logging.info("Detected candidates found at: {}".format(cand_file))
        else:
            raise IOError(
                "Expected 1 file in {} \
                    with extension {}. Found {}".format(
                    spccl_dir, ext, len(files)
                )
            )
        # If one file is found, load as array and return
        cand_metadata = np.loadtxt(
            cand_file, unpack=False, skiprows=1, dtype=np.float64
        ).tolist()
        if len(cand_metadata) == 0:
            raise Exception("Candidate list {} empty".format(cand_file))

        logging.info("Located {} candidates".format(len(cand_metadata)))
        return cand_metadata

    @staticmethod
    def _get_timestamps(fil: str, freq: float, disp: float) -> list:
        """
        Generates timestamps of pulses contained
        in test vector

        Parameters
        ----------
        fil: str
            Path to filterbank file from which
            to extract timestamps. Single pulse
            test vectors are generated by injecting
            periodic (pulsar signals) into filterbanks
            such that each rotation of the "pulsar"
            represents one of the single pulses which
            are to be searched by the SPS pipeline.

        freq: float
            Spin frequency of pulsar

        Returns
        ------
        list
            A list of floats, each of which is
            the MJD timestamp of one of the pulses in
            fil
        """
        timestamps = []
        # Extract parameters from vector header
        vector = VHeader(fil)
        start_time = vector.start_time()  # MJD
        end_time = start_time + (vector.duration() / 86400)  # MJD
        samples_per_period = 1 / (freq * vector.tsamp())

        # A fiducial pulse is placed at PEPOCH (which is the
        # midpoint of the observation). ft_inject_pulsar assumes
        # that the peak of the pulse is at this location. In our case
        # the peak occurs at the mid-point of the pulse period so the
        # sample of the peak of a reference pulse is half a period
        # later than PEPOCH
        fiducial_sample = int(samples_per_period / 2)

        # Convert into a fiducial time
        fiducial_time = (
            (fiducial_sample * vector.tsamp()) / 86400
        ) + start_time  # MJD

        # Compute DM offset
        dm_offset = (
            (4.15e6 * ((vector.fch1()) ** (-2)) * disp) / 1000 / 86400
        )  # days
        fiducial_time = fiducial_time + dm_offset

        # Compute pulse period
        period = 1 / (freq)

        # Get pulse times (at and) after fiducial time
        n = 0
        pulse_time = 0
        while pulse_time <= end_time:
            pulse_time = fiducial_time + (n * (period / 86400))
            if pulse_time > end_time:
                break
            timestamps.append(pulse_time)
            n += 1

        # Get pulse times before fiducial time
        n = 1
        pulse_time = np.inf
        while pulse_time >= start_time:
            pulse_time = fiducial_time - (n * (period / 86400))
            if pulse_time < start_time:
                break
            timestamps.append(pulse_time)
            n += 1

        timestamps.sort()
        return timestamps

    def from_vector(self, vector: str) -> list:
        """
        Extract parameters of each of the single pulses
        contained in a PSS SPS test vector. The parameters
        in the filename, as well as the header parameters in
        the vector are used to infer the parameters of the
        signal contained within it.

        Parameters
        ----------
        vector: str
            Path to test vector

        Returns
        -------
        list
            List of parameters of each of the single pulses
            in vector. The list is an Nx4 list, where N is
            the number of pulses contained in the vector.
        """
        # Check vector exists
        if not self._check_file(vector):
            raise FileNotFoundError("No such file {}".format(vector))

        logging.info("Extracting pulse data from {}".format(vector))

        # Split path and extension from vector filename
        basename = os.path.splitext(os.path.basename(vector))[0].split("_")

        # Determine signal properties from name of vector
        freq = float(basename[2])
        period = 1 / freq
        width = float(basename[3]) * period * 1000  # microseconds
        disp = float(basename[4])

        # Folded S/N and S/N per pulse
        sig_fold = float(basename[7])
        sig_pp = sig_fold * np.sqrt(period / VHeader(vector).duration())

        # Get list of timestamps
        timestamps = self._get_timestamps(vector, freq, disp)

        # Populate candidate array with expected parameters
        expected = []
        for timestamp in timestamps:
            this_cand = [timestamp, disp, width, sig_pp]
            expected.append(this_cand)

        # Sort by S/N in descending order
        expected.sort(key=lambda x: x[3], reverse=True)

        self.expected = expected

    def from_spccl(self, spccl_file) -> list:
        """
        This method loads a candidate metadata file directly,
        for comparison to the detected candidate file.
        There may or may not be columns labels at the top
        of the file. If found, the row will be skipped.

        Parameters
        ----------
        spccl_file: str
            Path to single pulse metadata file.

        Return
        ------
        list
            Single pulse metadata as an Nx4 list, where N is
            the number of entries in the metadata file.
        """
        if not self._check_file(spccl_file):
            raise FileNotFoundError("No such file {}".format(spccl_file))
        try:
            cand_metadata = np.loadtxt(
                spccl_file, unpack=False, skiprows=0, dtype=np.float64
            ).tolist()
        except ValueError:
            try:
                cand_metadata = np.loadtxt(
                    spccl_file, unpack=False, skiprows=1, dtype=np.float64
                ).tolist()
            except ValueError as exc:
                raise ValueError(
                    "File {} contains invalid types".format(spccl_file)
                ) from exc

        self.expected = cand_metadata

    def compare_dm(self, pars=None, sn_thresh=0.85):
        """
        Function to search for each expected pulse from the
        list of candidate detections. A match is defined if
        a candidate signal matches an expected signal within
        tolerances that are computed assuming the offset in
        detection values results ONLY from an error in the recovered
        DM value (see document associated with SP-2179 for tolerance
        derivations). Tolerances are defined in the DmTol class. This
        method requires information about the observing band and the
        frequency of the pulse in the test vector. These can be provided
        as a dictionary using the VHeader() method allpars().
        Further info in DmTol() class below.

        Parameters
        ----------
        pars : dict
            dictionary of test vector header and signal parameters.
            Required parameters are:
            "freq": the spin-frequency in Hz,
            "fch1: the frequency of the first channel (in MHz),
            "foff: the channel bandwidth (negative, in MHz),
            "nchans": the number of channels.

            E.g.,
            pars = {"freq" : 1.0,
                    "fch1 : 1670.0,
                    "foff" : -20.0,
                    "nchans" : 16}
        """
        logging.info("Using ruleset: DM")

        # For each known pulse in the test vector...
        for expected in self.expected:
            logging.info("Searching candidates for {}".format(expected))

            # Generate rules from the known pulse parameters and the
            # test vector parameters
            rules = DmTol(expected, pars, sn_thresh)

            # If we find it..
            if self._compare(expected, self.cands, rules):
                # Add to list of detected pulses
                self.detections.append(expected)
            else:
                # Add to list of non-detected pulses.
                self.non_detections.append(expected)

    @staticmethod
    def _compare(exp: list, cands: list, rules: object) -> bool:
        """
        Compares metadata for a known signal to the metadata for each
        detected candidate. If a candidate that is consistent with the known
        signal is found, within the tolerances set by the ruleset used,
        True is returned, else False.

        Parameters
        ----------
        exp : list
            A list of parameters of the known signal in the form
            [Timestamp (MJD), DM (pc/cc), Width (ms), S/N].

        cands : list
            A list of detected candidate metadata. Each list item
            is a list of parameters for a single candidate in the
            form above. For N candidates, the list has the shape
            N x 4.

        rules : object
            An object defining the tolerances for each of the
            parameters in the known signal.
        """
        detected = False
        # For each candidate....
        for cand in cands:
            if not detected:
                # Does the detected value of each parameter match that of
                # the known signal, with the tolerances set by the rules?
                if (
                    cand[3] >= rules.min_sn
                    and np.abs(exp[1] - cand[1]) <= rules.dm_tol
                    and np.abs(exp[2] - cand[2]) <= rules.width_tol / 1000
                    and np.abs(exp[0] - cand[0]) <= rules.timestamp_tol
                ):
                    logging.info("Detected with properties: {}\n".format(cand))
                    # Candidate matches - return True to caller
                    detected = True
                    return True
        # None of the candidates match our signal. Return False to caller.
        logging.info("No detection of pulse: {}\n".format(exp))
        return False


class DmTol:
    """
    Class to compute the tolerances on the single pulses using
    analytically derived values assuming the only source of
    variance is the signal being dedispersed at an
    incorrect DM value.

    This class is only relevant where the single pulse
    search is being conducted on PSS test vectors, as in this case
    the single pulses are injected periodically. As the pulse period
    (the constant interval between each "independent" single pulse) is
    fixed, the derivation of these tolerances would not be appropriate
    to validate real single pulse data.

    The class takes a list of pulse metadata parameters that represent
    the expected values, and computes a tolerance value for each of them.
    This can then be compared to the detected candidate metadata parameters.

    Parameters
    ----------
    expected : list
        A list of known metadata parameters in the form
        [Timestamp (MJD), DM (pc/cc), Width (ms), S/N]

    pars : dict
        A dictionary of parameters describing the properties
        of the filterbank being searched and of the signal
        injected into the filterbank.
    """

    def __init__(self, expected: list, pars: dict, sn_thresh: float):
        self.expected = expected
        self.pars = pars
        self.sn_thresh = sn_thresh

        self.width_tol = None
        self.min_sn = None
        self.dm_tol = None
        self.timestamp_tol = None
        self.weff = None

        # Check that the signal properties are
        # provided by the pars dictionary
        try:
            self.pars["freq"]
        except Exception as no_freq_error:
            raise KeyError from no_freq_error

        self.calc_tols()

    def calc_tols(self):
        """
        Generates tolerance data for each
        SpCcl metadata parameter.
        """
        # Compute period in us
        period = (1.0 / self.pars["freq"]) * 1e6

        self.sig(self.expected[3])
        self.width(self.expected[2] * 1000, period)
        self.dispersion(self.expected[1], self.expected[2] * 1000)
        self.timestamp()

    def sig(self, sn_int: float):
        """
        Sets threshold signal-to-noise ratio
        using the tolerance level of 85%
        """
        sn_threshold = sn_int * self.sn_thresh
        self.min_sn = sn_threshold

    def width(self, w_int: float, period: float):
        """
        Generates a width tolerance in
        microseconds

        Parameters
        ----------
        w_int : float
            Intrinsic width of the pulse being detected (us)

        period : float
            Period of the pulsar (us)
        """
        self.weff = (
            w_int * period / (self.sn_thresh**2.0 * (period - w_int) + w_int)
        )
        tol = np.abs(self.weff - w_int)
        self.width_tol = tol

    def dispersion(self, disp: float, wint: float):
        """
        Computes the effect of a broadened pulse on the DM
        in order to compute a DM tolerance (in pc/cc)

        Parameters
        ----------
        DM : float
            The "true" DM of the pulse

        wint: float
            The "true" width of the pulse in microseconds
        """
        # Compute frequency information
        fch_low = self.pars["fch1"] + self.pars["nchans"] * self.pars["foff"]
        bandwidth = self.pars["fch1"] - fch_low
        f_cent = (fch_low + (bandwidth / 2.0)) / 1000

        # Convert sample interval to microseconds
        tsamp = self.pars["tsamp"] / 1e-06

        # Compute DM tolerance
        term1 = 4 * f_cent**3.0 / (8.3 * bandwidth)
        term2 = 8.3 * bandwidth * disp / (self.pars["nchans"] * f_cent**3.0)
        this_dm_tol = term1 * np.sqrt(
            self.weff**2.0 - tsamp**2.0 - wint**2.0 - term2**2.0
        )

        self.dm_tol = this_dm_tol

    def timestamp(self):
        """
        Returns a timestamp tolerance in days
        """
        tol_us = self.weff / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        tol_s = tol_us * 1e-06
        self.timestamp_tol = tol_s / 86400
