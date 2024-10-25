"""
    **************************************************************************
    |                                                                        |
    |               Unit tests for pipeline runner                           |
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
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    |  pytest -m reqtests
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

import json
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

import pytest
from pytest import mark

from ska_pss_protest import Cheetah
from ska_pss_protest.executors import _config

# pylint: disable=E1123,C0114,E1101,W0621,W0613,R0903

DATA_DIR = os.path.join(
    Path(os.path.abspath(__file__)).parents[1], "tests/data"
)
SPS_CONFIG = "tests/data/examples/sps_pipeline_config.xml"


@pytest.fixture(scope="function")
def resource():
    """
    Fixture to set up a fake "cheetah" executable
    for mocking subprocess calls
    """

    def _setup(module, binary):
        build = tempfile.mkdtemp()
        module = os.path.join(build, module)
        os.makedirs(module)
        executable = os.path.join(module, binary)
        open(executable, "a", encoding="utf8").close()
        attr = os.stat(executable)
        os.chmod(executable, attr.st_mode | stat.S_IEXEC)
        return build, executable

    return _setup


@mark.unit
@mark.pipeline
class RunnerTests:
    """
    Tests to test the test framework itself.
    RunnerTests tests the functionality of the
    cheetah pipeline runner
    testapps/pipeline.py.
    """

    def test_no_build_dir(self):
        """
        If the name of the build directory
        is not set, raise exception.
        """
        try:
            del os.environ["CHEETAH_BUILD"]
        except KeyError:
            pass

        with pytest.raises(EnvironmentError):
            Cheetah("cheetah_pipeline", SPS_CONFIG, "sigproc", "SinglePulse")

    def test_no_executable(self, resource):
        """
        If the name of the executable passed
        is not correct, raise exception.
        """
        build, _ = resource("pipelines/search_pipeline", "cheetah_pipeline")
        with pytest.raises(EnvironmentError):
            Cheetah(
                "cheet_pipeline",
                SPS_CONFIG,
                "sigproc",
                "SinglePulse",
                build_dir=build,
            )
        shutil.rmtree(build)

    def test_build_dir_not_found(self):
        """
        If the cheetah build directory is not found,
        raise exception.
        """
        with pytest.raises(FileNotFoundError):
            Cheetah(
                "cheetah_pipeline",
                SPS_CONFIG,
                "sigproc",
                "SinglePulse",
                build_dir="/tmp/some_dir/",
            )

    def test_invalid_pipeline(self, resource):
        """
        If the name of the pipeline is not valid,
        raise exception.
        """
        build, _ = resource("pipelines/search_pipeline", "cheetah_pipeline")
        with pytest.raises(KeyError):
            Cheetah(
                "cheetah_pipeline",
                SPS_CONFIG,
                "sigproc",
                "XXXXXX",
                build_dir=build,
            )
        shutil.rmtree(build)

    def test_invalid_source(self, resource):
        """
        If the name of the source is not valid,
        raise exception.
        """
        build, _ = resource("pipelines/search_pipeline", "cheetah_pipeline")
        with pytest.raises(KeyError):
            Cheetah(
                "cheetah_pipeline",
                SPS_CONFIG,
                "XXXXX",
                "SinglePulse",
                build_dir=build,
            )
        shutil.rmtree(build)

    def test_no_exec_permission(self, resource):
        """
        If the path to the cheetah binary is not
        executable, raise exception.
        """

        # Set up fake cheetah resorces
        build, executable = resource(
            "pipelines/search_pipeline", "cheetah_pipeline"
        )

        # Disable execute permission on cheetah binary
        current = stat.S_IMODE(os.lstat(executable).st_mode)
        os.chmod(executable, current & ~stat.S_IEXEC)

        # Check we raise a permission error if we can't execute cheetah
        with pytest.raises(PermissionError):
            Cheetah(
                "cheetah_pipeline",
                SPS_CONFIG,
                "sigproc",
                "SinglePulse",
                build_dir=build,
            )

        shutil.rmtree(build)

    def test_no_config_file(self, resource):
        """
        Tests that the correct exception is raise if
        a non-existent config file is passed.
        """
        build, _ = resource("pipelines/search_pipeline", "cheetah_pipeline")
        with pytest.raises(FileNotFoundError):
            Cheetah(
                "cheetah_pipeline",
                "fake_config_file.xml",
                "sigproc",
                "SinglePulse",
                build_dir=build,
            )
        shutil.rmtree(build)

    def test_search_path(self):
        """
        Tests the cases where the user does not supply a
        path to a cheetah build/install directory, and instead
        assumed the executable they wish ProTest to launch
        already exists in the system $PATH

        To test this we use ls
        """
        # Test the case where the executable is found
        launcher = "ls"
        path = _config.search_path(launcher).split("/")
        assert launcher in path

        # Test the case where the executable is not found
        launcher = "non-existent-binary"
        with pytest.raises(FileNotFoundError):
            _config.search_path(launcher).split("/")

    def test_install_dir_search(self):
        """
        Tests the case where the user has supplied
        a path to an install directory (i.e., when building
        cheetah, the command "make install" was executed,
        producing a directory "install/bin" in which all
        pipeline launchers are to be found
        """
        # Set up executable in an "install" dir
        cheetah_dir = tempfile.mkdtemp()
        launcher = "cheetah_pipeline"
        executable = os.path.join(cheetah_dir, launcher)
        open(executable, "a", encoding="utf8").close()
        attr = os.stat(executable)
        os.chmod(executable, attr.st_mode | stat.S_IEXEC)
        launcher_dict = {"path": "/some/path"}

        # Test the case where the executable is found under the install dir
        path = _config.search_build(cheetah_dir, launcher, launcher_dict)
        assert launcher in path.split("/")

        # Test the case where the executable is not found under the install dir
        with pytest.raises(FileNotFoundError):
            _config.search_build(cheetah_dir, "bad_launcher", launcher_dict)

    def test_subprocess_call_to_cheetah_pipeline(self, mocker, resource):
        """
        Test that a call to ./cheetah_pipeline is correctly made by
        the subprocess.
        """

        # Set up fake cheetah resources
        build, executable = resource(
            "pipelines/search_pipeline", "cheetah_pipeline"
        )

        # Set cheetah log messages
        cheetah_log = (
            open(
                os.path.join(DATA_DIR, "cheetah_pipeline_log.txt"),
                "r",
                encoding="utf8",
            )
            .read()
            .encode()
        )

        class ChildStub:
            """
            Mocks call to child process
            """

            returncode = -9

            def communicate(self, timeout):
                """
                Emulate subprocess.communicate()
                """
                return (cheetah_log, b"")

        # Intercept call to subprocess with child_stub()
        mocker.patch("subprocess.Popen")
        subprocess.Popen.side_effect = [ChildStub()]

        # Instantiate "cheetah pipeline" and run it
        cheetah = Cheetah(
            "cheetah_pipeline",
            SPS_CONFIG,
            "sigproc",
            "SinglePulse",
            build_dir=build,
        )
        cheetah.run(debug=True)

        # Load parsed cheetah logs fixture
        dummy_parsed = json.load(
            open(os.path.join(DATA_DIR, "cheetah_pipeline_log.json"))
        )

        # Test log parser returns content expected
        assert json.loads(cheetah.logs) == dummy_parsed

        # Test the subprocess call
        subprocess.Popen.assert_called_once_with(
            [
                executable,
                "--config=tests/data/examples/sps_pipeline_config.xml",
                "-p",
                "SinglePulse",
                "-s",
                "sigproc",
                "--log-level=debug",
            ],
            stderr=-1,
            stdout=-1,
        )

        shutil.rmtree(build)

    def test_subprocess_call_to_cheetah_candidate_pipeline(
        self, mocker, resource
    ):
        """
        Test that a call to ./cheetah_candidate_pipeline
        is correctly made by the subprocess.
        """

        build, executable = resource(
            "pipelines/candidate_pipeline", "cheetah_candidate_pipeline"
        )

        cheetah_log = (
            open(
                os.path.join(DATA_DIR, "candidate_pipeline_log.txt"),
                "r",
                encoding="utf8",
            )
            .read()
            .encode()
        )

        class ChildStub:
            """
            Mocks call to child process
            """

            returncode = -9

            def communicate(self, timeout):
                """
                Emulate subprocess.communicate()
                """
                return (cheetah_log, b"")

        # Intercept call to subprocess with child_stub()
        mocker.patch("subprocess.Popen")
        subprocess.Popen.side_effect = [ChildStub()]

        # Instantiate "cheetah pipeline" and run it
        cheetah = Cheetah(
            "cheetah_candidate_pipeline",
            "tests/data/examples/cand_pipeline_config.xml",
            "spead",
            "empty",
            build_dir=build,
        )

        # run "pipeline" for 1 second
        cheetah.run(timeout=1)

        # Load parsed cheetah logs fixture
        dummy_parsed = json.load(
            open(
                os.path.join(DATA_DIR, "candidate_pipeline_log.json"),
                encoding="utf8",
            )
        )

        # Test log parser returns content expected
        assert json.loads(cheetah.logs) == dummy_parsed

        # Test the subprocess call
        subprocess.Popen.assert_called_once_with(
            [
                executable,
                "--config=tests/data/examples/cand_pipeline_config.xml",
                "-p",
                "empty",
                "-s",
                "spead",
            ],
            stderr=-1,
            stdout=-1,
        )

        shutil.rmtree(build)

    def test_subprocess_call_to_emulator(self, mocker, resource):
        """
        Test that a call to ./cheetah_emulator is correctly made by
        the subprocess.
        """

        build, executable = resource("emulator", "cheetah_emulator")

        cheetah_log = (
            open(
                os.path.join(DATA_DIR, "emulator_log.txt"),
                "r",
                encoding="utf8",
            )
            .read()
            .encode()
        )

        class ChildStub:
            """
            Mocks call to child process
            """

            returncode = -9

            def communicate(self, timeout):
                """
                Emulate subprocess.communicate()
                """
                return (cheetah_log, b"")

        # Intercept call to subprocess with child_stub()
        mocker.patch("subprocess.Popen")
        subprocess.Popen.side_effect = [ChildStub()]

        # Instantiate "cheetah pipeline" and run it
        cheetah = Cheetah(
            "cheetah_emulator",
            "tests/data/examples/emulator_config.xml",
            build_dir=build,
        )

        # run "pipeline" for 5 seconds
        cheetah.run(timeout=5)

        # Load parsed cheetah logs fixture
        dummy_parsed = json.load(
            open(os.path.join(DATA_DIR, "emulator_log.json"), encoding="utf8")
        )

        # Test log parser returns content expected
        assert json.loads(cheetah.logs) == dummy_parsed

        # Test the subprocess call
        subprocess.Popen.assert_called_once_with(
            [executable, "--config=tests/data/examples/emulator_config.xml"],
            stderr=-1,
            stdout=-1,
        )

        shutil.rmtree(build)
