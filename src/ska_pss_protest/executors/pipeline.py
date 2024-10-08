"""
    **************************************************************************
    |                                                                        |
    |                       PSS Pipeline Runner                              |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Testing framework backend application that sets up and deploys PSS     |
    | pipelines with the relevant input parameters and provides logs         |
    **************************************************************************
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
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
import logging
import os
import re
import subprocess

import numpy as np

from ._config import setup_pipeline

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)


class Cheetah:
    """
    Sets up and deploys PSS pipeline with the
    relevant input parameters and provides logs
    """

    def __init__(
        self, binary, config, source=None, pipeline=None, build_dir=None
    ):

        # Check all inputs make sense,
        # returning the path to the
        # executable if so.
        self.exec = setup_pipeline(binary, config, source, pipeline, build_dir)

        self.pipeline = pipeline
        self.config = config
        self.source = source

        # Form cheetah command
        self.command = self._form_command()

        self.logs = None
        self.exit_code = None
        self.err = None

    def _form_command(self) -> list:
        """
        Takes inputs from constructor and forms command for
        cheetah execution.

        Returns
        -------
        command : array
            Command as numpy array
        """

        # Set the --config argument to ./cheetah
        this_config = "--config=" + self.config
        command = [self.exec, this_config]

        # Does the command need to specify a pipeline?
        if self.pipeline:
            this_pipeline = ["-p", self.pipeline]
            command = np.append(command, this_pipeline)

        # Does the command need to specify a source?
        if self.source:
            this_source = ["-s", self.source]
            command = np.append(command, this_source)

        return command

    def run(self, timeout=None, debug=False) -> None:
        """
        Runs required cheetah pipeline with arguments as a child process

        Returns
        -------
        out : array
            Cheetah logs from STDOUT as a numpy array
        err : str
            Cheetah logs from STDERR
        exit_code : int
            Return code from cheetah execution
        """
        command = np.asarray(self.command)

        # Set debug policy
        if debug:
            command = np.append(command, "--log-level=debug")
        cmd_str = " ".join(command)
        logging.info("Command is: {}".format(cmd_str))

        # Spawn cheetah as a child process
        child = subprocess.Popen(
            command.tolist(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            # Process should complete on its own
            out, err = child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Indefinite process needs to be terminated by kernel.
            child.kill()
            out, err = child.communicate()
            logging.info("cheetah exceeded {} s".format(timeout))

        # Handle STDERR
        self.err = err.decode("utf-8")
        if len(self.err) == 0:
            self.err = None
        else:
            logging.warning("STDERR: {}".format(err))

        # Pass STDOUT to formatter and get back json string
        out = out.decode("utf-8")
        self.logs = self._parse_stdout(out)

        # Get exit code
        self.exit_code = child.returncode
        logging.info("Return code is: {}".format(self.exit_code))

    def export_log(self, location: str) -> None:
        """
        Writes cheetah log data to a file.
        The file will be named cheetah_logs.json,
        and will be written to the directory <location>.

        Parameters
        ----------
        location : str
            The directory into which the log file
            will be written.
        """
        filename = os.path.join(location, "cheetah_logs.json")

        with open(filename, "w") as this_file:
            this_file.write(self.logs)

    @staticmethod
    def _parse_stdout(logdata: str) -> str:
        """
        Parses STDOUT cheetah logs into a searchable format.
        Each line of log data is written as a dict with keys

        "type" (e.g., warn, log, debug)
        "tid" (the thread id number)
        "src" (the file which produced the message)
        "time" (the unix timestamp of the log)
        "msg" (the message itself)

        and returned as a json string.

        Parameters
        ----------
        logdata : str
            Cheetah output STDOUT log data

        Returns:
        -------
        str
            json string of cheetah log messages

        TODO: Carriage returns within a log message
              are not yet parsed correctly
        """
        fields = logdata.split("\n")
        data_out = []
        for line in fields:
            line_dict = {}
            if line.startswith("["):
                metadata = re.findall(r"\[(.+?)\]", line)
                line_dict["type"] = metadata[0]
                line_dict["tid"] = metadata[1].replace("tid=", "")
                line_dict["src"] = metadata[2]
                line_dict["time"] = metadata[3]
                line_dict["msg"] = line.split("]")[-1]
                data_out.append(line_dict)

        json_out = json.dumps(data_out, indent=4)
        return json_out
