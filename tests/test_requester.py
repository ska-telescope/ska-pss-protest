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
import tempfile

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
