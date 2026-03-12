"""
**************************************************************************
|                                                                        |
|          PSS ProTest dedispersion plan selecting script                |
|                                                                        |
**************************************************************************
| Author: Raghuttam Hombal                                               |
| Email : raghuttamshreepadraj.hombal@manchester.ac.uk                   |
**************************************************************************
| License:                                                               |
|                                                                        |
| Copyright 2026 SKA Organisation                                        |
|                                                                        |
|Redistribution and use in source and binary forms, with or without      |
|modification, are permitted provided that the following conditions are  |
|met:                                                                    |
|                                                                        |
|1. Redistributions of source code must retain the above copyright       |
|notice, this list of conditions and the following disclaimer.           |
|                                                                        |
|2. Redistributions in binary form must reproduce the above copyright    |
|notice, this list of conditions and the following disclaimer in the     |
|documentation and/or other materials provided with the distribution.    |
|                                                                        |
|3. Neither the name of the copyright holder nor the names of its        |
|contributors may be used to endorse or promote products derived from    |
|this software without specific prior written permission.                |
**************************************************************************
"""

import argparse
import json
import os
from xml.etree import ElementTree


class DedispersionPlanSelect:
    """
    This class is responsible for selecting a suitable dedispersion plan
    """

    def __init__(self, ddplan_file=None):
        """
        Initialiser for the class

        Parameters
        ------------
        ddplan_file: str
            Path to file that contains ddplans
            default: dd_plans.json
        """
        if ddplan_file is None:
            self.ddplan_file = self._get_default_ddplan_file()
        else:
            self.ddplan_file = ddplan_file
        self.storage = {}
        # Automatically try to load existing data on startup
        self.load_from_file()

    @staticmethod
    def _get_default_ddplan_file():
        """
        Returns the path to dd_plans.json in the same directory as this module

        Returns
        -------------------
        a path to a default file in the same folder as this module
        which will be a permenant holder for dedispersion plans
        """
        module_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(module_dir, "dd_plans.json")

    def add(self, label: str, data: dict):
        """
        Adds a dictionary and immediately saves to disk
        Parameters
        -------------------
        label: str
            A unique label to the store dedispersion plans

        data: dict
            A dictionary with key 'plan' and the value being
            a list of dictionaries defining dedispersion plan
        """

        if not isinstance(data, dict):
            raise ValueError(f"Expected a dict, got {type(data).__name__}")

        try:
            assert "plan" in data.keys()
        except ValueError:
            raise ValueError(
                "The data provided is not in right format, it does not contain 'plan' key"
            )

        self.storage[label] = data
        self.save_to_file()

    @staticmethod
    def list_to_xml(dd_plan_list: list):
        """
        Converts and slots in the list of DDPlan into the element tree of dedispersion
        Paramters
        -----------------
        root: ElementTree.SubElement
            XML Element Tree from cheetah config

        dd_plan_list: list
            A list of dictionaries defining the dedisersion plan
            must contain 'start', 'end' and 'step' as keys in every dictionary

        Returns
        ----------------
        ElementTree.SubElement
            XML Element Tree with updated dedispersion plan
        """
        root = ElementTree.Element("ddtr")
        for element in dd_plan_list:
            dedispersion = ElementTree.SubElement(root, "dedispersion")

            for key, value in element.items():
                child = ElementTree.SubElement(dedispersion, key)
                child.text = str(value)
            root.append(dedispersion)

        return root

    def select(self, label: str) -> list:
        """
        Returns the dictionary associated with the label

        Parameters
        ------------
        label: str
            An unique plan name given to the dedispersion plan

        Returns
        --------------
        list
            A list of dictionaries defining the dedispersion plan
        """

        if not (label in self.storage.keys()):
            raise KeyError

        return self.storage.get(label)["plan"]

    def save_to_file(self):
        """
        Serialises and stores the data into a JSON file defined by self.ddplan_file
        """
        try:
            with open(self.ddplan_file, "w") as f:
                json.dump(self.storage, f, indent=4)
        except IOError as e:
            print(f"Error saving to file: {e}")

    def load_from_file(self):
        """
        Loads data from the JSON file if it exists
        """
        if os.path.exists(self.ddplan_file):
            try:
                with open(self.ddplan_file, "r") as f:
                    self.storage = json.load(f)
            except (json.JSONDecodeError, IOError):
                print(
                    "Warning: Could not read file. Starting with empty registry."
                )
                self.storage = {}
        else:
            self.storage = {}

    def list_labels(self) -> list:
        """
        Returns the list all the dedispersion plans saved
        """
        return list(self.storage.keys())


def user_inputs():
    """
    Function to ask user to input dedispersion plan
    """
    plan_list = []
    unique_id = input("Unique ID for dedispersion plan:").strip().lower()

    while True:
        try:
            start_raw = input("\nStart: ").strip().lower()
            if start_raw == "done":
                break

            end_raw = input("\nend: ").strip().lower()
            if end_raw == "done":
                break

            step_raw = input("\nStep: ").strip().lower()
            if step_raw == "done":
                break

            plan_list.append(
                {
                    "start": float(start_raw),
                    "end": float(end_raw),
                    "step": float(step_raw),
                }
            )
        except ValueError:
            raise ValueError

    return unique_id, plan_list


if __name__ == "__main__":
    """
    Entry is using only dm_plan to adding and viewing
    """

    parser = argparse.ArgumentParser(description="Dedispersion plan manager")

    group = parser.add_argument(
        "--list", action="store_true", help="List all the available DM plans"
    )
    group = parser.add_argument(
        "--add", action="store_true", help="Add a dedispersion plan"
    )
    group = parser.add_argument(
        "--file",
        default=None,
        help="JSON file containing all DM plans (if none, default is chosen)",
    )

    args = parser.parse_args()

    if args.file is not None:
        dd_plan = DedispersionPlanSelect(args.file)
    else:
        dd_plan = DedispersionPlanSelect()

    if args.list:
        print("List of dedispersion plans available:")
        for plan_id in dd_plan.list_labels():
            print(f"- {plan_id}")

    if args.add:
        label, plan = user_inputs()
        dd_plan.add(label=label, data={"plan": plan})
