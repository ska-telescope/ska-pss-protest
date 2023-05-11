#!/usr/bin/env python

"""
    **************************************************************************
    |                                                                        |
    |                  PSS Test Vector logfile parser                        |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Testing framework backend application that checks and parses the       |
    | Cheetah log files.                                                     |
    **************************************************************************
    | Author: Lina Levin Preston                                             |
    | Email : lina.preston@manchester.ac.uk                                  |
    | Author: Benjamin Shaw                                                  |
    | Email : benjamin.shaw@manchester.ac.uk                                 |
    **************************************************************************
    | Usage:                                                                 |
    |                                                                        |
    | from logparser import LogParse                                         |
    | logs = LogParse(cheetahlogs)                                           |
    |                                                                        |
    | To search log files:                                                   |
    | logs.search(item="<string to find>")                              |
    |                                                                        |
    | To check for any errors in logfile, and save error log:                |
    | logs.errors()                                                    |
    |                                                                        |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Copyright 2021 University of Manchester                                |
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
from typing import Union

# pylint: disable=W1202

logging.basicConfig(
    format="1|%(asctime)s|%(levelname)s\
            |%(funcName)s|%(module)s#%(lineno)d|%(message)s",
    datefmt="%Y-%m-%dT%I:%M:%S",
    level=logging.INFO,
)


class LogParse:
    """
    Class docstring
    """

    def __init__(self, logs=None):
        self.logs = self._check_logs(logs)

    @staticmethod
    def _check_logs(logs: str) -> Union[str, bool]:
        """
        Checks and loads Cheetah logs and ensures
        they are valid JSON

        Parameters
        ----------
        logs: str
           JSON string of cheetah logs

        Returns
        -------
        str, bool
           JSON string object if logs are valid, else False
        """
        this_logs = json.loads(logs)
        logging.info("Cheetah logs valid JSON")
        return this_logs

    def search(self, item: str) -> bool:
        """
        Searches logs for string

        Parameters
        ----------
        item: str
           String to search for

        Returns
        -------
        bool
           True if string was found in log messages, else False
        """
        logging.info("Searching logs for message: '{}'".format(item))
        messages = [msg.get("msg") for msg in self.logs]
        if any(item in string for string in messages):
            logging.info("String '{}' found".format(item))
            return True
        logging.info("String '{}' not found".format(item))
        return False

    def errors(self) -> Union[bool, str]:
        """
        Searches logs for messages of type 'error'

        Returns
        -------
        bool, str
          False if no errors found,
          else JSON string of error messages
        """
        errors_list = []
        logging.info("Searching for messages of type 'error'")
        for entry in self.logs:
            if entry["type"] == "error":
                errors_list.append(entry)
                logging.info("Log message of type 'error' found")
            if len(errors_list) == 0:
                logging.info("No log messages of type 'error'")
                return False
        json_out = json.dumps(errors_list, indent=4)
        return json_out
