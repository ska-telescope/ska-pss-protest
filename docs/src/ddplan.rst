# PSS ProTest Dedispersion Plan Manager

The `DedispersionPlanSelect` script provides a utility for managing, storing, and converting dedispersion plans. It allows users to maintain a registry of plans in JSON format and export them into XML structures compatible with Cheetah configurations.

---

## Class: DedispersionPlanSelect

This class handles the lifecycle of dedispersion plans, including disk persistence (JSON) and XML transformation.

### `__init__(self, ddplan_file=None)`

Initializes the manager and automatically attempts to load existing plans from the specified file.

* **Parameters:**
* `ddplan_file` (str, optional): Path to the JSON storage file. Defaults to `dd_plans.json` in the module directory.

---

## Methods

### `add(label, data)`

Adds a new dedispersion plan to the internal storage and immediately synchronizes with the disk.

* **Parameters:**
* `label` (str): A unique identifier for the plan.
* `data` (dict): A dictionary containing a `"plan"` key, which holds a list of dedispersion step dictionaries.
#### Note: If somebody wants to add metadata field to this plan, such as description, it can be done by adding a new key to the dictionary (Although the current implementation of the plan adder does not support this feature).


* **Raises:** `ValueError` if data is not a dict or if the "plan" key is missing.

### `select(label)`

Retrieves a specific plan by its unique label.

* **Parameters:**
* `label` (str): The unique name of the plan to retrieve.


* **Returns:** `list` of dictionaries defining the plan.
* **Raises:** `KeyError` if the label does not exist.

### `list_to_xml(dd_plan_list)` (Static Method)

Converts a list of dedispersion plan dictionaries into an `xml.etree.ElementTree` object.

* **Parameters:**
* `dd_plan_list` (list): A list of dicts. Each dict must contain keys such as `start`, `end`, and `step`.


* **Returns:** `ElementTree.Element` representing the `<ddtr>` root.

### `list_labels()`

Returns a list of all currently registered plan labels.

* **Returns:** `list[str]`

### `save_to_file() / load_from_file()`

Internal methods to handle JSON serialization. `load_from_file` is called automatically during instantiation.

---

## CLI Usage

The script can be executed directly from the terminal to manage plans interactively.

### 1. List Available Plans

```bash
python src/ska_pss_protest/product_tests/data/dm_plans/dm_plan.py --list

```

### 2. Add a New Plan

This triggers an interactive prompt to enter a Unique ID and DM ranges (start, end, step). Type `done` at the "Start" prompt to finish.

```bash
python src/ska_pss_protest/product_tests/data/dm_plans/dm_plan.py --add

```

### 3. Specify a Custom Storage File

```bash
python src/ska_pss_protest/product_tests/data/dm_plans/dm_plan.py --file path/to/my_plans.json --list

```

---

## Data Structures

### JSON Storage Format

Plans are stored in the following structure within the `.json` file:

```json
{
    "low_dm_plan": {
        "plan": [
            {
                "start": 0.0,
                "end": 100.0,
                "step": 0.1
            },
            {
                "start": 100.0,
                "end": 500.0,
                "step": 0.5
            }
        ]
    }
}

```

### Generated XML Format

The `list_to_xml` method produces the following hierarchy:

```xml
<ddtr>
    <dedispersion>
        <start>0.0</start>
        <end>100.0</end>
        <step>0.1</step>
    </dedispersion>
</ddtr>

```

---
