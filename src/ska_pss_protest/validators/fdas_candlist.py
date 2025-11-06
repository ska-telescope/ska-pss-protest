"""
    **************************************************************************
    |                                                                        |
    |                       PSS Candidate parser                             |
    |                                                                        |
    **************************************************************************
    | Description: Candidate metadata sifter for FDAS                        |
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
import pandas as pd

from ska_pss_protest import OcldReader

# from ska_pss_protest.validators.candidate import Filterbank

np.set_printoptions(precision=17)

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

# pylint: disable=C0301,W1202,C0209,W0703,W0631,C0103,W0613


class FdasScl:
    """
    Parses metadata products from the frequency domain
    acceleration search (FDAS) pipeline.

    Parameters
    ----------
    scl_dir: str
        Path to directory containing FDAS candidate metadata
        file (scl=sifted candidate list)
    extension: str
        Expected file extension of scl file
    """

    def __init__(self, scl_dir=None, extension=".scl"):
        self.scl_dir = scl_dir
        self.extension = extension
        self.vheader_param = None

        # Have we set a scl dir?
        if not self.scl_dir:
            raise OSError("No candidate directory specified")
        # Does the scl dir exist on the filesystem?
        if not os.path.isdir(self.scl_dir):
            raise OSError("No such directory: {}".format(self.scl_dir))

        # Get list of cands from file in scl directory
        self.cands = self._get_cands(self.scl_dir, self.extension)

        self.expected = None
        self.detected = None
        self.recovered = None

    @staticmethod
    def _get_cands(scl_dir: str, ext: str) -> list:
        """
        Look up cands file in scl directory,
        and process each line as a candidate, return
        candidates as an array comprising period, pdot,
        DM, width and S/N values. One row for each candidate.

        Parameters
        ----------
        scl_dir: str
            Directory expected to contain
            candidate metadata file

        ext: str
            Extension of candidate metadata file

        Returns
        -------
        cand_metadata: numpy.ndarray
           MxN array containing M candidates
           each with N properties (nominally 5)
        """
        # Get name of metadata file from spccl_dir
        files = []
        for this_file in os.listdir(scl_dir):
            if this_file.endswith(ext):
                files.append(this_file)
        # Do we only have one candidate metadata file?
        if len(files) == 1:
            cand_file = os.path.join(scl_dir, files[0])
            logging.info("Detected candidates found at: {}".format(cand_file))
        else:
            raise IOError(
                "Expected 1 file in {} \
                    with extension {}. Found {}".format(
                    scl_dir, ext, len(files)
                )
            )
        # If one file is found, load as pandas dataframe and return
        scl_header = ["period", "pdot", "dm", "harmonic", "width", "sn"]
        cand_metadata = pd.read_csv(cand_file, sep="\t")
        cand_metadata.columns = scl_header
        if cand_metadata.empty:
            raise EOFError("Candidate list {} empty".format(cand_file))
        logging.info("Located {} candidates".format(cand_metadata.shape[0]))

        # Sort by S/N in descending order
        cand_metadata = cand_metadata.sort_values("sn", ascending=False)
        return cand_metadata

    def from_vector(self, vector: str, vector_header: dict) -> list:
        """
        Extract parameters of the pulsar using a test
        vector filename. These will be used to validate
        an acceleration search.

        Parameters
        ----------
        vector: str
            Path to test vector

        Returns
        -------
        list
            List of pulsar parameters. The list is an
            1xN list, where N is the number of parameters
            used to validate each candidate.
        """
        # Save header information
        self.vheader_param = vector_header

        logging.info("Extracting pulsar parameters from {}".format(vector))

        # Split path and extension from vector filename
        basename = os.path.splitext(os.path.basename(vector))[0].split("_")

        # Determine signal properties from name of vector
        period = 1.0 / float(basename[2]) * 1000  # milliseconds
        width = float(basename[3]) * period  # milliseconds
        disp = float(basename[4])
        accel = float(basename[5])
        sig_fold = float(basename[7])

        # Set expected period derivative from acceleration parameter
        pdot = -accel * period / 3e8

        self.expected = [period, pdot, disp, width, sig_fold]

    def search_tol(self, tol_set) -> None:
        """
        Method to search for an injected pulsar from the
        list of candidate detections. A match is defined if
        a candidate signal matches an expected signal within
        tolerances, as defined in the FdasDummyTol class.

        This is placeholder method until formal FDAS tolerances
        are defined.

        Parameters
        ----------
        tol_set: str
            Paramter to choose which tolerance set to use.
            Options are: dummy, basic
            dummy: Dummy tolerance set
            basic: Basic tolerance set
            If no tolerance set is specified, then ValueError
            is raised.
        """
        logging.info(
            "Searching pulsar candidates for {}".format(self.expected)
        )

        # Get a tolerance for each metadata parameter
        if tol_set == "dummy":
            # Dummy tolerance
            logging.info("Using ruleset: Dummy")
            rules = FdasTolDummy(self.expected)
        elif tol_set == "basic":
            # Basic tolerance
            logging.info("Using ruleset: Basic")
            rules = FdasTolBasic(self.expected, self.vheader_param)
        else:
            raise ValueError(
                "Invalid tolerance set specified: {}".format(tol_set)
            )

        # Apply tolerance rules to each candidate
        sifted, best = self._compare(self.cands, rules)

        # Are there ANY candidates within our tolerances?
        if best is None:
            # If no, our pulsar was not recovered. Exit
            self.detected = False
            return

        # One or more candidates have survived our tolerance rules.
        logging.info(
            "Reduced candidate list to {} candidates".format(sifted.shape[0])
        )
        logging.info("Candidates within tolerances:\n{}".format(sifted))

        # Find the highest S/N candidate in our list of survivors.
        self.recovered = sifted.loc[[best]]
        logging.info("Best candidate is \n{}".format(self.recovered))
        self.detected = True

    @staticmethod
    def _compare(
        cands: pd.DataFrame, rules: object
    ) -> tuple[pd.DataFrame, int]:
        """
        Compares metadata for a known pulsar signal to the metadata for each
        detected candidate. If a candidate that is consistent with the known
        signal is found, within the tolerances set by the ruleset used,
        its metadata is returned, else, None.

        Parameters
        ----------
        cands : object
           A pandas dataframe comprising 5 columns describing the
           period, period derivatives, dm, width, and S/N for each
           candidate

        rules : object
            An object defining the tolerances for each of the
            parameters in the known signal.
            NOTE that the width tolerance is not used in the
            comparison, as the width is not very accurate for
            periodicity searches using fourier transforms.

        Returns
        -------
        sifted cands : object
            pandas dataframe containing only candidates which
            satisfy tolerances defined in the ruleset used.

        detection : int
            The index of the surviving candidate that has the
            highest S/N.
        """
        # Take our pandas dataframe and reduce it to only those
        # candididates that fall within the tolerances set by the
        # rule set chosen
        sifted_cands = cands.query(
            "@rules.period_tol[0] <= period <= @rules.period_tol[1] & @rules.pdot_tol[0] <= pdot <= @rules.pdot_tol[1] &  @rules.dm_tol[0] <= dm <= @rules.dm_tol[1] & @rules.width_tol[0] <= width <= @rules.width_tol[1]"
        )
        if not sifted_cands.empty:
            # If we have any candidates left, sort them by S/N
            sifted_cands = sifted_cands.sort_values(by="sn", ascending=False)
            detection = sifted_cands["sn"].idxmax()
            return sifted_cands, detection
        return None, None


class FldoOcld:
    """
    Placeholder class for FDAS OCLD candidate validation
    """

    def __init__(self, ocld_dir=None, extension=".ocld"):
        self.ocld_dir = ocld_dir
        self.extension = extension

        # Have we set a ocld dir?
        if not self.ocld_dir:
            raise OSError("No candidate directory specified")
        # Does the ocld dir exist on the filesystem?
        if not os.path.isdir(self.ocld_dir):
            raise OSError("No such directory: {}".format(self.ocld_dir))

        self.candidate_df = self._get_cands(self.ocld_dir, self.extension)

    @staticmethod
    def _get_cands(ocld_dir: str, ext: str) -> pd.DataFrame:
        """
        Look up OCLD file in a directory,
        and use the OcldReader to parse the candidate metadata,
        returning a pandas dataframe.

        Parameters
        ----------
        ocld_dir: str
            Directory expected to contain
            candidate metadata and data file

        ext: str
            Extension of candidate metadata file

        Returns
        -------
        cand_metadata: pandas.DataFrame
           Dataframe containing candidate metadata
        """
        # Get name of metadata file from spccl_dir
        files = []
        for this_file in os.listdir(ocld_dir):
            if this_file.endswith(ext):
                files.append(this_file)
        # Do we only have one candidate metadata file?
        if len(files) == 1:
            cand_file = os.path.join(ocld_dir, files[0])
            logging.info("Detected candidates found at: {}".format(cand_file))
        else:
            raise IOError(
                "Expected 1 file in {} \
                    with extension {}. Found {}".format(
                    ocld_dir, ext, len(files)
                )
            )

        # If one file is found, load as pandas dataframe and return
        ocld_reader = OcldReader(cand_file)
        ocld_reader.load_metadata()
        return ocld_reader.get_metadata_df()

    def from_vector(self, vector: str, vector_header: dict) -> list:
        """
        Extract parameters of the pulsar using a test
        vector filename. These will be used to validate
        an acceleration search.

        Parameters
        ----------
        vector: str
            Path to test vector

        Returns
        -------
        list
            List of pulsar parameters. The list is an
            1xN list, where N is the number of parameters
            used to validate each candidate.
        """
        # Save header information
        self.vheader_param = vector_header

        logging.info("Extracting pulsar parameters from {}".format(vector))

        # Split path and extension from vector filename
        basename = os.path.splitext(os.path.basename(vector))[0].split("_")

        # Determine signal properties from name of vector
        period = 1.0 / float(basename[2]) * 1000  # milliseconds
        width = float(basename[3]) * period  # milliseconds
        disp = float(basename[4])
        accel = float(basename[5])
        sig_fold = float(basename[7])

        # Set expected period derivative from acceleration parameter
        pdot = -accel * period / 3e8

        self.expected = [period, pdot, disp, width, sig_fold]

    def search_tol(self, tol_set) -> None:
        """
        Method to search for an injected pulsar from the
        list of candidate detections. A match is defined if
        a candidate signal matches an expected signal within
        tolerances, as defined in the FdasDummyTol class.

        This is placeholder method until formal FDAS tolerances
        are defined.

        Parameters
        ----------
        tol_set: str
            Paramter to choose which tolerance set to use.
            Options are: dummy, basic
            dummy: Dummy tolerance set
            basic: Basic tolerance set
            If no tolerance set is specified, then ValueError
            is raised.
        """
        logging.info(
            "Searching pulsar candidates for {}".format(self.expected)
        )

        # Get a tolerance for each metadata parameter
        if tol_set == "dummy":
            # Dummy tolerance
            logging.info("Using ruleset: Dummy")
            rules = FdasTolDummy(self.expected)
        elif tol_set == "basic":
            # Basic tolerance
            logging.info("Using ruleset: Basic")
            rules = FdasTolBasic(self.expected, self.vheader_param)
        else:
            raise ValueError(
                "Invalid tolerance set specified: {}".format(tol_set)
            )

        # Apply tolerance rules to each candidate
        sifted, best = self._compare(self.candidate_df, rules)

        # Are there ANY candidates within our tolerances?
        if best is None:
            # If no, our pulsar was not recovered. Exit
            self.detected = False
            return

        # One or more candidates have survived our tolerance rules.
        logging.info(
            "Reduced candidate list to {} candidates".format(sifted.shape[0])
        )
        logging.info("Candidates within tolerances:\n{}".format(sifted))

        # Find the highest S/N candidate in our list of survivors.
        self.recovered = sifted.loc[[best]]
        logging.info("Best candidate is \n{}".format(self.recovered))
        self.detected = True

    @staticmethod
    def _compare(
        cands: pd.DataFrame, rules: object
    ) -> tuple[pd.DataFrame, int]:
        """
        Compares metadata for a known pulsar signal to the metadata for each
        detected candidate. If a candidate that is consistent with the known
        signal is found, within the tolerances set by the ruleset used,
        its metadata is returned, else, None.

        Parameters
        ----------
        cands : object
           A pandas dataframe comprising 5 columns describing the
           period, period derivatives, dm, width, and S/N for each
           candidate

        rules : object
            An object defining the tolerances for each of the
            parameters in the known signal.
            NOTE that the width tolerance is not used in the
            comparison, as the width is not very accurate for
            periodicity searches using fourier transforms.

        Returns
        -------
        sifted cands : object
            pandas dataframe containing only candidates which
            satisfy tolerances defined in the ruleset used.

        detection : int
            The index of the surviving candidate that has the
            highest S/N.
        """
        # Take our pandas dataframe and reduce it to only those
        # candididates that fall within the tolerances set by the
        # rule set chosen
        sifted_cands = cands.query(
            "@rules.period_tol[0] <= period <= @rules.period_tol[1] & @rules.pdot_tol[0] <= pdot <= @rules.pdot_tol[1] &  @rules.dm_tol[0] <= dm <= @rules.dm_tol[1] & @rules.width_tol[0] <= width <= @rules.width_tol[1] & @rules.sn_tol <= sn"
        )
        if not sifted_cands.empty:
            # If we have any candidates left, sort them by S/N
            sifted_cands = sifted_cands.sort_values(by="sn", ascending=False)
            detection = sifted_cands["sn"].idxmax()
            return sifted_cands, detection
        return None, None


class FdasTolDummy:
    """
    Class to compute the tolerances on the FDAS candidates

    This is a placeholder class until a format set of FDAS
    tolerances are defined.
    """

    def __init__(self, expected: list):

        self.expected = expected
        self.period_tol = None

        self.calc_tols()

    def calc_tols(self) -> None:
        """
        Set tolerances for each of the parameters
        we are testing candidates against.
        """
        self.period_tol = self.period(self.expected[0])
        self.pdot_tol = self.pdot(self.expected[1])
        self.dm_tol = self.dm(self.expected[2])
        self.width_tol = self.width(self.expected[3])
        self.sn_tol = self.sn(self.expected[4])
        logging.info("EXPECTED: {}".format(self.expected))

    @staticmethod
    def period(this_period: float) -> list[float]:
        """
        Dummy method to set period tolerance
        """
        ptol = 0.1 * this_period
        return [this_period - ptol, this_period + ptol]

    @staticmethod
    def pdot(this_pdot: float) -> list[float]:
        """
        Dummy method to set period derivative tolerance
        """
        return [0.1 * this_pdot, 10 * this_pdot]

    @staticmethod
    def dm(this_dm: float) -> list[float]:
        """
        Dummy method to set DM tolerance
        """
        dmtol = 0.1 * this_dm
        return [this_dm - dmtol, this_dm + dmtol]

    @staticmethod
    def width(this_width: float) -> list[float]:
        """
        Dummy method to set width tolerance
        """
        widthtol = 0.1 * this_width
        return [this_width - widthtol, this_width + widthtol]

    @staticmethod
    def sn(this_sn: float) -> float:
        """
        Dummy method to set S/N tolerance
        """
        sntol = 0.85 * this_sn
        return sntol


class FdasTolBasic:
    """
    Class to compute the tolerances on the FDAS candidates
    This set is named "basic" as it is a more realistic set
    of tolerances than the dummy set.
    """

    def __init__(self, expected: list, header: dict):

        self.expected = expected
        self.header = header

        self.psbc_time = self._get_psbc_time(
            self.header["duration"], self.header["tsamp"]
        )
        self.calc_tols()

    @staticmethod
    def _get_psbc_time(tobs: float, tsamp: float) -> float:
        """
        The function is used to calculate the time
        resolution of the PSBC search. The PSBC time
        is defined as the time equal to the closest
        power of 2 number of samples and is strictly
        smaller than the time of the observation.
        """
        exponent = np.floor(np.round(np.log2(tobs / tsamp)))
        t_psbc = (2**exponent) * tsamp
        return t_psbc

    @staticmethod
    def _get_z_levels(z: float, base: int):
        """
        Use the filter number to get the surrounding
        multiples of base
        """
        if base <= 0:
            raise ValueError("Base must be positive")

        nearest = round(z / base) * base
        lower = nearest - base
        upper = nearest + base

        return lower, nearest, upper

    @staticmethod
    def _get_acc_from_filter(z: float, freq: float, t_psbc: float) -> float:
        """
        A method to return the acceleration (m/s/s)
        from the filter number (z)
        """
        return (z * 3e8) / (freq * t_psbc**2.0)

    @staticmethod
    def _accel_to_pdot(accel: float, period: float) -> float:
        """
        Convert acceleration (m/s/s) to pdot (s/s)
        """
        return period * -accel / 3e8

    @staticmethod
    def _pdot_to_accel(pdot: float, period: float) -> float:
        """
        Convert pdot (s/s) to acceleration (m/s/s)
        """
        return pdot * 3e8 / -period

    def calc_tols(self) -> None:
        """
        Set tolerances for each of the parameters
        we are testing candidates against.
        """
        self.period_tol = self.period(self.expected[0])
        self.pdot_tol = self.pdot(self.expected[1])
        self.dm_tol = self.dm(self.expected[2], self.expected[3])
        self.width_tol = self.width(self.expected[3])
        self.sn_tol = self.sn(self.expected[4])
        logging.info("EXPECTED: {}".format(self.expected))

    def period(self, this_period: float) -> list[float]:
        """
        Method to set period tolerance
        For the pulse period, the frequency resolution post FFT
        is used to set the uncertainty which will be 1 frequency
        bin either side of the true frequency, defined by tol_bins.
        """

        # Number of bins to use for tolerance
        tol_bins = 1

        # The frequency resolution is given by
        delta_freq = 1 / self.psbc_time

        fmin, fmax = (1 / this_period) - (tol_bins * delta_freq), (
            1 / this_period
        ) + (tol_bins * delta_freq)
        return [1 / fmax, 1 / fmin]

    def pdot(self, this_pdot: float) -> list[float]:
        """
        A method to compute Pdot tolerances. the filter number we
        expect to find the pulsar in (z) is determined and the
        lowest and highest acceleration based on the filter width
        (i.e, delta_z = 5) is computed.
        This assumes a fixed value of delta z which may be subject
        to change later but this should be straightforward if needed.

        """
        delta_z = 5  # Separation of filters to use for tolerance

        freq = 1 / (self.expected[0] * 1e-3)
        accel = self._pdot_to_accel(this_pdot, self.expected[0] * 1e-3)
        t_psbc = self.psbc_time

        z = (accel * freq * t_psbc**2) / 3e8
        z_range = self._get_z_levels(z, delta_z)

        a_low = self._get_acc_from_filter(z_range[0], freq, t_psbc)
        a_high = self._get_acc_from_filter(z_range[-1], freq, t_psbc)

        # Convert acceleration to pdot
        pdot_high = self._accel_to_pdot(a_low, 1 / freq)
        pdot_low = self._accel_to_pdot(a_high, 1 / freq)

        return [pdot_low, pdot_high]

    def dm(self, this_dm: float, wint: float) -> list[float]:
        """
        Method to set DM tolerance
        This is defined by the maximum S/N degradation
        allowed due to dispersion smearing. This can be
        varied by changing the scaler value.
        The value of 2 is taken to set S/N loss up to 85%
        """
        scaler = 2

        fch_low = (
            self.header["fch1"] + self.header["nchans"] * self.header["foff"]
        )
        sqdiff = ((1 / fch_low) ** 2.0) - (1 / self.header["fch1"] ** 2.0)

        dmtol = (scaler * wint) / (4.15e9 * sqdiff)

        return [this_dm - (dmtol * 1e3), this_dm + (dmtol * 1e3)]

    def width(self, this_width: float) -> list[float]:
        """
        Method to set width tolerance
        Considering the fact that width reported by fourier
        domain periodicity search is not very accurate, we
        set the width tolerance to be +/- infinity.
        """
        return [-np.inf, np.inf]

    def sn(self, this_sn: float) -> float:
        """
        Method to set S/N tolerance
        TODO: Needs to be defined clearly.
        """
        sntol = 0.85 * this_sn
        return sntol
