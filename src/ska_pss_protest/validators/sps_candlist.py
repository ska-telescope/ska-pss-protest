"""
    **************************************************************************
    |                                                                        |
    |                       PSS Candidate parser                             |
    |                                                                        |
    **************************************************************************
    | Description: Candidate metadata sifter for SPS                         |
    |                                                                        |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    | Author: Raghuttam Hombal                                               |
    | Email : raghuttamshreepadraj.hombal@manchester.ac.uk                   |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2025 SKA Observatory                                         |
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

from ska_pss_protest import VHeader

np.set_printoptions(precision=17)

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

# pylint: disable=C0301,W1202,C0209,W0703,W0631,C0103,W0613


class SpCcl:
    """
    Parses metadata products from the single pulse search
    (SPS) pipeline.

    Parameters
    ----------
    spccl_dir: str
        Path to directory containing SPS metadata file
    extension: str
        Expected file extension of SPS metadata file
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
            raise EOFError("Candidate list {} empty".format(cand_file))
        logging.info("Located {} candidates".format(len(cand_metadata)))

        # Sort by S/N in descending order
        cand_metadata.sort(key=lambda x: x[3], reverse=True)
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

    def from_vector(self, vector: str, reject_last=None) -> list:
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

        reject_last : int
            Do not expect candidates to be detected
            after this number of samples into the scan.
            Cheetah currently rejects all candidates that occur
            in the last dedispersion buffer.

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

        header = VHeader(vector)

        # Split path and extension from vector filename
        basename = os.path.splitext(os.path.basename(vector))[0].split("_")

        # Determine signal properties from name of vector
        freq = float(basename[2])
        period = 1 / freq
        width = float(basename[3]) * period * 1000  # milliseconds
        disp = float(basename[4])

        # Folded S/N and S/N per pulse
        sig_fold = float(basename[7])
        sig_pp = sig_fold * np.sqrt(period / header.duration())

        # Get list of timestamps
        timestamps = self._get_timestamps(vector, freq, disp)

        # If we want to not include the candidates in the final dedispersion
        # buffer, we can pass the number of samples in that buffer to
        # reject_last. By doing this, ProTest will not expect them.
        if reject_last:
            # Convert number of samples into a number of days
            reject_window = (reject_last * header.tsamp()) / 86400

            # Compute MJD of end of scan
            scan_end = header.start_time() + (header.duration() / 86400)

            # Compute the epoch after which candidates are not considered
            reject_after = scan_end - reject_window

            # Create a modified list of timestamps that does not include the
            # final buffer
            timestamps_filtered = [k for k in timestamps if k <= reject_after]
            timestamps = timestamps_filtered

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

    def compare_widthstep(self, pars=None, widths_list=None) -> None:
        """
        Function to search for each expected pulse from the
        list of candidate detections. A match is defined if
        a candidate signal matches an expected signal within
        tolerances, as defined in the WidthTol class. This
        method requires information about the observing band and the
        frequency of the pulse in the test vector. These can be provided
        as a dictionary using the VHeader() method allpars().
        Further info in WidthTol() class below.

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

        windex : int
            List pulse widths searched by the relevant
            SPS algotrithm used.
        """
        logging.info("Using ruleset: WidthStep")

        # For each known pulse in the test vector...
        for expected in self.expected:
            logging.info("Searching candidates for {}".format(expected))

            # Generate rules from the known pulse parameters and the
            # test vector parameters
            rules = WidthTol(expected, pars, widths_list)

            # If we find it..
            result = self._compare(expected, self.cands, rules)
            if result[4]:
                # Add to list of detected pulses
                self.detections.append(result[:4])
            else:
                # Add to list of non-detected pulses.
                self.non_detections.append(result[:4])

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
        logging.info("DM tolerance {}".format(rules.dm_tol))
        logging.info(
            "Width range {}-{} ms".format(
                rules.width_tol[0] / 1000, rules.width_tol[1] / 1000
            )
        )
        logging.info("TOA tolerance {} d".format(rules.timestamp_tol))
        detected = False
        # For each candidate....
        for cand in cands:
            if not detected:
                # Does the detected value of each parameter match that of
                # the known signal, with the tolerances set by the rules?
                # Note: We currently do not test on S/N.
                timestamp_check = (
                    exp[0] - rules.timestamp_tol
                    <= cand[0]
                    <= exp[0] + rules.timestamp_tol
                )
                dm_check = (
                    exp[1] - rules.dm_tol <= cand[1] <= exp[1] + rules.dm_tol
                )
                width_check = (
                    rules.width_tol[0] / 1000
                    <= cand[2]
                    <= rules.width_tol[1] / 1000
                )
                if timestamp_check and dm_check and width_check:
                    logging.info("Detected with properties: {}\n".format(cand))
                    # Candidate matches - return True to caller
                    detected = True
                    return cand[0], cand[1], cand[2], cand[3], True
        # None of the candidates match our signal. Return False to caller.
        logging.info("No detection of pulse: {}\n".format(exp))
        return exp[0], exp[1], exp[2], exp[3], False

    def summary_export(self, vector_header) -> None:
        """
        Exports a Summary file named - summary.txt in the candidate_dir
        containing all the information about all the detections and non-detections.

        Parameters
        --------------
        vector_header: dict
            This is a dictionary containing information about
            headers such as information about pulses injected into
            test-vector, RFI-ID, Filterbank header etc..
        """
        logging.info("Writing Summary file")
        file_mark = f"{vector_header['freq']},{vector_header['width']},{vector_header['disp']},{vector_header['sig']},{vector_header['rfi_id']}"
        with open(
            os.path.join(self.spccl_dir, "summary.txt"), "a+"
        ) as summary_file:
            summary_file.write(
                "test,frequency,duty,dm,sn,rfi_id,result,detect_mjd,detect_dm,detect_width,detect_sn\n"
            )

            for detection in self.detections:
                info = f"rfim_sps,{file_mark},detection,{','.join(map(str, detection))}\n"
                summary_file.write(info)

            for non_detection in self.non_detections:
                info = f"rfim_sps,{file_mark},non_detection,{','.join(map(str, non_detection))}\n"
                summary_file.write(info)


class WidthTol:
    """
    Class to compute the tolerances on the single pulses using
    Boxcar width steps from the PSS config file.

    This class is only relevant for a single pulse search
    and not a periodicity search.

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

    widths_list : list
        A list of matched filter (boxcar) widths (in bins).
    """

    def __init__(self, expected: list, pars: dict, widths_list: list):
        self.expected = expected
        self.pars = pars
        self.widths_list = widths_list

        self.width_tol = None
        self.dm_tol = None
        self.timestamp_tol = None
        self.sntol = None

        self.calc_tols()

    def calc_tols(self) -> None:
        """
        Generates tolerance data for each
        SpCcl metadata parameter.
        """

        # Compute period in microseconds
        period = 1.0 / self.pars["freq"] * 1e6

        # Compute true pulse width in microseconds
        wint = self.expected[2] * 1000

        self.dispersion(wint)
        self.timestamp(wint)
        self.width(wint)
        self.sig(self.expected[3], wint, period)

    def dispersion(self, wint: float) -> None:
        """
        Sets the DM tolerance using the pulse width.

        A "scaler" can be tuned to increase or decrease
        the tolerance as required.
        Parameters
        ----------
        wint: float
            The "true" width of the pulse in microseconds

        """
        scaler = 2

        fch_low = self.pars["fch1"] + self.pars["nchans"] * self.pars["foff"]
        sqdiff = ((1 / fch_low) ** 2.0) - (1 / self.pars["fch1"] ** 2.0)

        self.dm_tol = (scaler * wint) / (4.15e9 * sqdiff)

    def timestamp(self, wint: float) -> None:
        """
        Returns a timestamp tolerance in days

        Parameters
        ----------
        wint: float
            The "true" width of the pulse in microseconds
        """

        wint_s = wint / 1e6
        tol_s = wint_s / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        self.timestamp_tol = tol_s / 86400

    def width(self, wint: float) -> None:
        """
        Sets the tolerance on the width by comparing the
        true width of the test pulse to the nearest boxcar
        width used in the SPS matched filtering process.

        The range of permitted widths are set according
        to the boxcar widths each size of the one that is
        nearest to the intrinsic width.

        For example, if we search for a 10,000 microseconds wide
        pulse using matched filters with widths of
        2048, 4096, 8192, 16384, 32768 microseconds, the nearest to
        true pulse width is 8192 microseconds, so the range of
        allowed widths is 4096 - 16384 microseconds.

        Note: Unlike the other tolerances in this class which return
        a delta (such that the range of allowed values is
        <true value> +/- delta), this function sets an allowed
        range explicitely - i.e, [lower_limit, upper_limit].

        Parameters
        ----------
        wint : float
            The "true" width of the pulse in microseconds
        """

        # Take list of trial boxcar sizes and
        # convert to a list of widths (us)
        trial_widths = np.asarray(
            [
                (trial_box_bin * self.pars["tsamp"]) * 1e6
                for trial_box_bin in self.widths_list
            ]
        )

        # Find the closest index in trial_widths to the test value wint
        nearest = np.absolute(trial_widths - wint).argmin()

        # Determine the lower and upper bounds of an acceptable candidate width.....
        # Is nearest width the narrowest?
        if nearest == 0:
            # Is our intrinsic width narrower than the narrowest?
            if wint < trial_widths[0]:
                lower, upper = wint, trial_widths[nearest + 1]
            # Or is it wider than the narrowest?
            else:
                lower, upper = trial_widths[nearest], trial_widths[nearest + 1]
        # Is nearest width the widest?
        elif nearest == len(trial_widths) - 1:
            # Is our intrinsic width wider than the widest?
            if wint > trial_widths[-1]:
                lower, upper = trial_widths[nearest - 1], wint
            # Is our intrinsic width narrower than the widest?
            else:
                lower, upper = trial_widths[nearest - 1], trial_widths[nearest]
        else:
            lower, upper = trial_widths[nearest - 1], trial_widths[nearest + 1]

        self.width_tol = [lower, upper]

    def sig(self, sn_int: float, wint: float, period: float) -> None:
        """
        Sets the S/N tolerance by using the radiometer
        equation for two pulses with different widths,
        where wint is the injected pulse width and weffbox
        is the closest box car width.
        More information on the S/N tolerance is given in
        documents connected to feature SP-2949.

        Parameters
        ----------
        sn_int: float
             The injected single pulse S/N

        wint : float
            The "true" width of the pulse in microseconds

        period: float
             Injected pulse period in us

        TODO - Fully implement and add to unit tests
        """
        trial_widths = np.asarray(
            [
                (trial_box_bin * self.pars["tsamp"]) * 1e6
                for trial_box_bin in self.widths_list
            ]
        )

        weffbox = trial_widths[np.absolute(trial_widths - wint).argmin()]

        self.sntol = sn_int * np.sqrt(
            (wint * (period - weffbox)) / (weffbox * (period - wint))
        )
