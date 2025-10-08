"""
    **************************************************************************
    |                                                                        |
    |                  PSS Test Vector download and cacheing                 |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Testing framework backend application that handles the downloading     |
    | and cacheing of test vectors required for PSS pipeline tests.          |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    | from requester import VectorPull                                       |
    | vector = VectorPull(cache_dir=<custom_cache_dir>)                      |
    |                                                                        |
    | If cache_dir is not set, the env variable CACHE_DIR will be used.      |
    | If CACHE_DIR is also not set, cache will be placed in                  |
    | ~/.cache/SKA/test_vectors                                              |
    |                                                                        |
    | Available methods:                                                     |
    |                                                                        |
    | If the name of the vector is known                                     |
    | from_name(<name of vector>, <refresh=True/False>)                      |
    |                                                                        |
    | If the full URL of the vector is known                                 |
    | from_url(<url of vector>, refresh=<True/False>)                        |
    |                                                                        |
    | If a vector with specific properties is required but the explicit      |
    | name or url is not known                                               |
    | from_properties(duty=0.1, refresh=<True/False>) for a vector with a    |
    | 10% duty cycle (see method docstring for options/defaults).            |
    |                                                                        |
    | if refresh is set to True, the local cache will not be checked and a   |
    | download of the vector is made. Else a download only occurs if the     |
    | vector is not found in the cache.                                      |
    |                                                                        |
    | Attributes:                                                            |
    | cache_dir - the directory to be checked/used for cacheing vectors      |
    | local_path - the path to the local copy of the vector if downloaded    |
    |              or if already existing in cache.
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2024 SKA Observatory                                         |
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
import random
import shutil
from time import sleep
from typing import Union

import requests

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)

# pylint: disable=C0301,W1202,C0209,W0703


class VectorPull:
    """
    Class docstring
    """

    def __init__(self, cache_dir=None):

        self.cache_dir = cache_dir
        self.local_path = None
        self.prefix = "http://testvectors.jb.man.ac.uk/"

        # Hold of before processing the test vector for a random
        # period of time. This prevents mutiple test processes from
        # evaluating the write status of a locally stored test vector
        # at the same time.
        sleep(random.uniform(0, 5))

        self._setup_cache()

    def _setup_cache(self) -> None:
        """
        Sets up cacheing. If no cache directory is
        passed into constructor then the CACHE_DIR
        environment variable is checked. If this is
        set, it will be used as the cache directory.
        If not, a default will be selected.

        If the cache directory doesn't already exist,
        it is created.

        Parameters
        ----------
        None
        """
        # Do we have a custom cache dir?
        if self.cache_dir:
            self._dir_exists(self.cache_dir)
            logging.info("Cache location: {}".format(self.cache_dir))
            return

        # Is cache dir set in env
        try:
            self.cache_dir = os.environ["CACHE_DIR"]
        except KeyError:
            # Cache dir not set anywhere. Use a default.
            self.cache_dir = (
                os.path.expanduser("~") + "/.cache/SKA/test_vectors"
            )
        logging.info("Cache location: {}".format(self.cache_dir))
        self._dir_exists(self.cache_dir)

    @staticmethod
    def _dir_exists(this_dir: str) -> None:
        """
        Checks if a directory exists. Creates it if not.

        Parameters
        ----------
        this_dir: str
            Directory to check exists

        Returns
        -------
        None
        """
        if not os.path.isdir(this_dir):
            os.makedirs(this_dir, exist_ok=True)

    @staticmethod
    def _get_type(vector: str) -> str:
        """
        Extracts vector type from vector filename.
        This is used in forming the URL of a remote
        test vector.

        Parameters
        ----------
        vector: str
            Vector filename

        Returns
        -------
        vector_type: str
            The vector type
        """
        fields = vector.split("_")
        vector_type = fields[0]
        return vector_type

    def _check_cache(self, filename: str) -> Union[str, None]:
        """
        Checks if a vector exists in local cache directory.
        If the vector is found the path to the vector is returned,
        else None.

        Parameters
        ----------
        filename: str
           Vector filename

        Returns
        -------
        pathname: str, None
            Path to vector in local cache
        """

        # If our vector exists it will be at this location.
        pathname = self.cache_dir + "/" + filename

        # Is it?
        if os.path.isfile(pathname):
            logging.info("{} in local cache".format(filename))
            return pathname
        logging.info("{} not in local cache".format(filename))
        return None

    def check_disk_space(self, vector_url: str, cache: str) -> None:
        """
        Checks the size of the requested vector
        from the remote directory and compares to
        disk space in local cache directory

        Parameters
        ----------
        vector_url: str
           Name of vector to pull
        cache: str
           Path to local cache directory
        """

        # Check disk space available in cache directory
        free_space = shutil.disk_usage(cache)[2]

        # Check size of vector
        vector_size = self._remote_header(vector_url)["Content-Length"]

        # Set a disk buffer of 0.5 GB as a minimum amount of disk space
        # to have left on device after downloading
        disk_buffer = 0.5 * (1024**3)
        req_space = int(vector_size) + disk_buffer
        if int(req_space) > int(free_space):
            raise OSError("Unsufficient disk space")

    @staticmethod
    def _remote_header(url: str) -> dict:
        """
        Makes a HEAD request to a remote test vector
        and returns the HTTP header information

        Parameters
        ----------
        url: str
            Full path to remote vector

        """
        file_head = requests.head(url, timeout=20)
        if file_head.status_code != 200:
            raise FileNotFoundError("Vector not found on remote server")

        return file_head.headers

    def _compare_remote(self, local_path: str, remote_path: str) -> bool:
        """
        Compares the size of a local vector with a remote version
        on the test vector origin server.

        Parameters
        ----------
        local_path : str
            Path to local copy of test vector
        remote_path : str
            Path to remote copy of test vector

        Returns
        -------
        bool: True if sizes match, else False
        """
        local_size = os.stat(local_path).st_size
        if int(local_size) == int(
            self._remote_header(remote_path)["Content-Length"]
        ):
            return True
        return False

    def _download(self, remote_path: str) -> str:
        """
        Downloads vector from remote server and
        places it in local cache directory.

        Parameters
        ----------
        filename: str
            Vector filename

        Returns
        -------
        pathname: str
           The local path to the vector after download.
        """

        # Set local path in cache directory.
        local_path = os.path.join(
            self.cache_dir, os.path.basename(remote_path)
        )

        # Check that there is enough disk space to download
        self.check_disk_space(remote_path, self.cache_dir)

        # Request vector from server.
        stream = requests.get(remote_path, stream=True, timeout=20)
        if stream.status_code != 200:
            raise FileNotFoundError("Vector not found")
        logging.info("Pulling {}".format(remote_path))

        # Write content to local_path
        with open(local_path, "wb") as writer:
            for chunk in stream.iter_content(chunk_size=8192):
                writer.write(chunk)
        logging.info("Data written to {}".format(local_path))
        return local_path

    def from_name(
        self, vector_name: str, refresh=False, check_remote=True
    ) -> None:
        """
        Gets vector from vector name.
        This method is used if the name of the vector is
        known a-priori. It the vector exists in the local
        cache then it will be used. Else it will be pulled
        from the remote repo.

        Parameters
        ----------
        vector_name: str
            The filename of the vector.

        refresh: bool
            Check local cache

        check_remote: bool
            Verify test vector header with origin
        """
        this_path = None

        # Construct remote URL
        this_type = self._get_type(vector_name)
        remote_path = os.path.join(self.prefix, this_type, vector_name)

        # Check cache if required.
        if not refresh:
            this_path = self._check_cache(vector_name)

        # Is vector on local machine and does
        # it have the correct file size?
        if this_path:
            # Get the size of the file we've found
            file_size = os.stat(this_path).st_size
            if check_remote:
                # Do size check and exit if they match
                if self._compare_remote(this_path, remote_path):
                    self.local_path = this_path
                    return

                # If we're here, the local test vector has a different size to the remote
                # vector. In this scenario, we check that no other process is currently
                # writing to the file, and if that is true, then we begin the download
                # of a fresh copy. If another file is writing that test vector to our local
                # disk, we wait, using an exponential backoff loop, until that process stops.
                # If that happens and the file is still the same (wrong) size, we pull a fresh
                # copy, or, if it's now the correct size, we pass that vector on to the test.
                logging.info(
                    "{} and {} are different sizes.".format(
                        this_path, remote_path
                    )
                )
                base = random.uniform(1.5, 2.0)
                adverse_events = 1

                while True:
                    # This while loop is an exponential backoff loop. That is, the backoff time
                    # is t = b**c, where b is the base factor and c is the number of adverse
                    # events. The loop will be exited if the file size does not change between
                    # backoff durations.
                    delay_time = int(base**adverse_events)
                    logging.info(
                        "Backing off for {} seconds".format(delay_time)
                    )
                    sleep(delay_time)

                    # After our backoff period, has the file size changed?
                    file_size_now = os.stat(this_path).st_size
                    if file_size_now != file_size:
                        # Our file size has changed. Wait one backoff duration and try again
                        file_size = file_size_now
                        adverse_events += 1
                    else:
                        # If we're here, the file size is stable and we can proceed with the test
                        if self._compare_remote(this_path, remote_path):
                            # The file size matches that of the remote vector. No further action.
                            logging.info(
                                "{} passed checks. Proceeding with test".format(
                                    this_path
                                )
                            )
                            return
                        # If we're here, the file size has stablised, but is not the correct
                        # size. Therefore we repull from the test vector server.
                        logging.info("Repulling {}".format(this_path))
                        break
            else:
                self.local_path = this_path
                return

        self.local_path = self._download(remote_path)

    def from_properties(
        self,
        vectype="SPS-MID",
        freq=0.2,
        duty=0.2,
        disp=740.0,
        acc=0.0,
        shape="Gaussian",
        sig=50.0,
        rfi="0000",
        tnamp=0.0,
        tngam=0.0,
        refresh=False,
    ) -> None:
        """
        Queries the server for a test vector for which
        we don't know the file name or if it exists but for which
        we know its properties. This method is agnostic to the version
        or the noise seed. The server will look in the "latest" directory
        as, if the vector doesn't exist in latest it doesn't exists at all.

        If a vector with the required properties is found on the server
        we still have the option to check the local cache. This method
        will use the from_name method if the vector is found remotely.

        Parameters
        ----------
        vectype: str
            The vector type
        freq: float
            The rotation frequency of the source
        duty: float
            The duty cycle of the profile
        disp: float
            The dispersion measure
        acc: float
            The acceleration of the source
        shape: str
            The pulse profile shape
            (only Gaussian works for now)
        sig: float
            The signal-to-noise ratio
        refresh: bool
            Check local cache if True, else False
        """

        # Construct dictionary of search parameters
        params = {
            "type": vectype,
            "freq": freq,
            "duty": duty,
            "dm": disp,
            "acceleration": acc,
            "shape": shape,
            "sn": sig,
            "seed": "None",
            "version": "None",
            "rfi": rfi,
            "tnamp": tnamp,
            "tngam": tngam,
        }

        # Ask server to look for test vector with params
        query = requests.get(self.prefix + "/query", params=params, timeout=20)
        print(self.prefix + "/query")

        # Did the server accept the request? Exit if not.
        if query.status_code != 200:
            raise SyntaxError("Bad request. server does not understand query")

        # The server accepted the request. Get response.
        response = query.text

        # Did the server fail to find an appropriate vector? Exit if so.
        if response == "None":
            raise FileNotFoundError("No vector with requested properties")

        # Vector exists remotely
        # pass the details to from_name() for further handling.
        logging.info("Found vector: {}".format(response))
        self.from_name(response, refresh=refresh)

    def flush_cache(self) -> None:
        """
        Removes contents of cache directory.
        """
        logging.info("Clearing cache from {}".format(self.cache_dir))
        for filename in os.listdir(self.cache_dir):
            this_file = os.path.join(self.cache_dir, filename)
            try:
                os.unlink(this_file)
                logging.info("Deleted: {}".format(this_file))
            except Exception as this_ex:
                logging.error(
                    "Failed to delete {}. Reason: {}".format(
                        this_file, this_ex
                    )
                )
