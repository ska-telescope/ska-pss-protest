"""
    **************************************************************************
    |                                                                        |
    |               Unit tests for test vector provisioning                  |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Tests the functionality of the PSS testing framework backend           |
    | application requester.py. Requester's purpose is to download and       |
    | cache the test vectors required as part of the testing framework.      |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    |  pytest -m reqtests                                                    |
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

import os
import shutil
import tempfile
from multiprocessing import Process

import pytest
from pytest import mark

from ska_pss_protest import VectorPull

# pylint: disable=E1123,C0114,W1514

VECTOR = "FDAS-HSUM-MID_38d46df_500.0_0.1_1.0_0.0_Gaussian_50.0_0000_0.0_0.0_123123123.fil"


@mark.unit
@mark.reqtests
class RequesterTests:
    """
    Tests to test the test framework itself.
    RequesterTests tests the functionality of the test
    vector pulling and cacheing capabilities in
    testapps/requester.py.
    """

    def test_two_simultaneous_downloads(self):
        """
        Tests that two simulataneous downloads of the same vector
        to the same location on the filesystem cannot interfere
        with each other. To do this we utilise the multiprocessing
        module to launch two downloads in parallel.
        """

        vector = "FDAS-HSUM-MID_38d46df_500.0_0.05_1.0_100.397_Gaussian_50.0_0000_0.0_0.0_123123123.fil"

        def task(cache_dir):
            """
            A function to set up a requester object and request
            download of an FDAS test vector. This will be called by
            the multiprocessing method Process().
            """
            pull = VectorPull(cache_dir=cache_dir)
            pull.from_properties(
                vectype="FDAS-HSUM-MID",
                freq=500.0,
                duty=0.05,
                disp=1.0,
                acc=100.397,
                sig=50.0,
            )

        cache_dir = tempfile.mkdtemp()

        # Check that we don't already have the file we want
        # to test the download of
        assert not os.path.isfile(
            os.path.join(
                cache_dir,
                vector,
            )
        )

        processes = []

        # Set and launch the first download process
        process_a = Process(target=task, args=(cache_dir,))
        processes.append(process_a)
        process_a.start()
        # Set and launch the second download process
        process_b = Process(target=task, args=(cache_dir,))
        processes.append(process_b)
        process_b.start()

        # Wait for both process to complete
        for this_process in processes:
            this_process.join()

        # Check that we have our file at the location we expect
        assert os.path.isfile(
            os.path.join(
                cache_dir,
                vector,
            )
        )
        shutil.rmtree(cache_dir)

    def test_from_name_with_cache_env(self):
        """
        Tests from_name() method with cache dir specified
        as environment variable. Vector does not a-priori
        exist in cache.
        """
        env_cache_dir = os.environ["CACHE_DIR"] = tempfile.mkdtemp()
        pull = VectorPull()
        assert pull.cache_dir == env_cache_dir
        assert os.path.isdir(env_cache_dir)
        pull.from_name(VECTOR)
        assert pull.local_path == os.path.join(env_cache_dir, VECTOR)
        assert os.path.isfile(pull.local_path)
        pull.flush_cache()

    def test_from_name_no_cache_env(self):
        """
        Tests from_name() method with cache dir not specified
        Vector does not a-priori exist in cache.
        """
        try:
            del os.environ["CACHE_DIR"]
        except KeyError:
            pass
        pull = VectorPull()
        assert (
            pull.cache_dir
            == os.path.expanduser("~") + "/.cache/SKA/test_vectors"
        )
        pull.from_name(VECTOR)
        assert pull.local_path == os.path.join(pull.cache_dir, VECTOR)
        assert os.path.isfile(pull.local_path)
        pull.flush_cache()

    def test_from_name_custom_cache(self):
        """
        Tests from_name() method using a user specified cache dir.
        Vector does not a-priori exist in cache.
        """
        custom_cache_dir = tempfile.mkdtemp()
        pull = VectorPull(cache_dir=custom_cache_dir)
        assert pull.cache_dir == custom_cache_dir
        assert os.path.isdir(custom_cache_dir)
        pull.from_name(VECTOR)
        assert pull.local_path == os.path.join(custom_cache_dir, VECTOR)
        pull.flush_cache()

    def test_from_name_vector_in_cache(self):
        """
        Tests from_name() method with vector already in cache.
        """
        custom_cache_dir = tempfile.mkdtemp()

        pull = VectorPull(cache_dir=custom_cache_dir)
        assert pull.cache_dir == custom_cache_dir
        assert os.path.isdir(custom_cache_dir)

        # Get vector into cache and clear local_path variable
        pull.from_name(VECTOR)
        pull.local_path = False

        # Pull vector again, this time with the file in
        # local cache
        pull.from_name(VECTOR)
        assert pull.local_path == os.path.join(custom_cache_dir, VECTOR)
        pull.flush_cache()

    def test_pull_non_existent_vector(self):
        """
        Tests the correct exception is raised if requested
        vector does not exist either in cache or on remote server.
        """
        with pytest.raises(FileNotFoundError):
            VectorPull().from_name("fake_file.fil", refresh=True)

    def test_pull_from_properties(self):
        """
        Tests from_properties() method.
        """
        custom_cache_dir = tempfile.mkdtemp()
        pull = VectorPull(cache_dir=custom_cache_dir)
        assert pull.cache_dir == custom_cache_dir
        pull.from_properties(
            vectype="FDAS-HSUM-MID", freq=500.0, duty=0.1, disp=1.0
        )
        assert pull.local_path == os.path.join(custom_cache_dir, VECTOR)
        pull.flush_cache()

    def test_from_properties_bad_request(self):
        """
        Tests from_properties raises the correction exception
        if a bad request is sent to test vector server.
        """
        pull = VectorPull(cache_dir=tempfile.mkdtemp())
        with pytest.raises(SyntaxError):
            pull.from_properties(duty=None, refresh=True)

    def test_from_properties_no_matching_vector(self):
        """
        Tests from_properties raises the correct exception
        if a non-existent vector is requested from the server.
        """
        pull = VectorPull(cache_dir=tempfile.mkdtemp())
        with pytest.raises(FileNotFoundError):
            pull.from_properties(duty=0.00000001)

    def test_from_name_local_changed_check_remote(self):
        """
        Test that a vector is pulled from the remote server
        even if that file exists in the cache, if it has a
        different file size to the remote version
        """
        cache_dir = tempfile.mkdtemp()
        pull = VectorPull(cache_dir=cache_dir)
        local_vector_path = os.path.join(cache_dir, VECTOR)
        open(local_vector_path, "a").close()
        before_size = os.stat(local_vector_path).st_size
        pull.from_name(VECTOR)
        after_size = os.stat(pull.local_path).st_size
        assert after_size > before_size
        pull.flush_cache()

    def test_from_name_local_changed_check_remote_off(self):
        """
        Test that a vector is not pulled from the remote server
        even if that file exists in the cache, and has a different
        size to the remote version
        """
        cache_dir = tempfile.mkdtemp()
        pull = VectorPull(cache_dir=cache_dir)
        local_vector_path = os.path.join(cache_dir, VECTOR)
        open(local_vector_path, "a").close()
        before_size = os.stat(local_vector_path).st_size
        pull.from_name(VECTOR, check_remote=False)
        after_size = os.stat(pull.local_path).st_size
        assert after_size == before_size
        pull.flush_cache()
