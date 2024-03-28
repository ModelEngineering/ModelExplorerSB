# Scripts Usage Guide

# Overview

There are two main Python scripts that may edit the data cache:

1. mk_data.py
2. edit_cache.py

This guide will explain their behavior and how to use/run each script.

# `edit_cache.py`

This script provides functionality to add or remove a specified, custom file type from each project in the data cache. For instance, for every project in the destination folder, `addToAll` may add an SBML file or `removeFromAll` may exclude all the CSVs.

**The following parameters must be configured before use:**

1. `DATA_CACHE`
2. `STAGE_DIR`
3. `EXT`
4. custom function and `checkIsDesired`
5. The script itself to call the desired function (`addToAll` or `removeFromAll`)

**1. `DATA_CACHE`**: The path to the folder that will hold the finalized project files (in the case of addToAll)
OR the path to the folder from which to remove files from each project (in the case of removeFromAll). The script will visit each project housed in this directory.

**2. `STAGE_DIR`**: `addToAll` requires a "staging" directory that holds all possible, available files associated with a given project (`DATA_CACHE` may be a specialized subset of this containing only the files we desire). Therefore, `addToAll` will visit this directory and search for a matching project directory within it to pull the additional file from. For instance, `DATA_CACHE` > `proj_1080` may contain

- `report.csv`
- `directory.json`
- `figure1.png`

`STAGE_DIR` > `proj_1080` may contain a superset of this such as

- `report.csv`
- `directory.json`
- `figure1.png`
- `biomodel3.xml`
- and more (the full list of files associated with `proj_1080`)

If one desires to add `.xml` files to each project, it will be pulled from the `STAGE_DIR`.

**3. `EXT`**: a `string` representation of a target file-type's extension. For instance, `.xml` files should configure this as `EXT = "xml"`

**4. custom function and `checkIsDesired`**:
The way to detect a certain file type is largely dependent on that particular file. For instance, the same methods cannot be used to distinguish a JSON file from an SBML file. Therefore, a custom function must be provided within the script (see "Functions in `edit_cache.py` for details).

The variable within the script - `checkIsDesired` - must then be updated to be set to this custom function.
For example: `checkIsDesired = isSbmlFile`

**5. Update script**: Finally, the last line of the script must be updated to call the desired function.
Ex. `addToAll(checkIsDesired)`

## Functions in `edit_cache.py`

#### **`checkIsDesired`**: Given a file path, returns T/F based on if that file is of the desired type (CUSTOM DEFINED)

#### **Parameters**: `path: str`: the path to a file to examine and determine if it the target file-type or not.

- For example, `"data/proj_1080/model.xml"`

#### **Return**: `isTarget: bool`: A True/False value based on if the file at the provided path is the target file type.

#### **`addToAll`**: Given a method to distinguish file types, searches in `STAGE_DATA` to add files of that desired type into each project folder.

**Parameters:** `checkIsDesired: function`: name of a custom function that distinguishes if a file is the target type (see `checkIsDesired` above)

**Return:** None: Modifies each project in `DATA_CACHE`

# `mk_data.py`

`mk_data.py`is the main script that drives the build process of the data cache.

This script detects project that have already been built so that the build process may pick up where it left off should it experience any interruptions.
