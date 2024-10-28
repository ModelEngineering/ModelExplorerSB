# Directory Doctor Usage Guide
(This is for administration of a GitHub based cache. Admin can interact in 3 ways: set, add, remove)
Followed by sections detialing how to do each of these


Aniticipating meeting wiht user-side cache work people.
Demonstrate to everyone what im doing and why im doing it.
Gifs to readme
Document that mk_data will create local and you add and push to your own account.
Review what the result from mk_data will be.
# Overview
Directory Doctor is a package that automates administration usage of a GitHub based file cache. Admin can interact with the cache in 3 ways: 
1. Create 
2. Add 
3. Remove

There are two main Python scripts that may edit the data cache:


1. mk_data.py
2. edit_cache.py

This guide will explain their behavior and how to use/run each script.

# `mk_data.py` - Create

`mk_data.py` is the main script that drives the build process of the data cache.

**Usage**: `python mk_data.py`

This will trigger the build and build up a staging directory which contains all the available files associated with each project. Each project is then filtered and zipped into a final data directory that may be unzipped at the desired location to serve as the final data cache.

This script detects projects that have already been built so that the build process may pick up where it left off should it experience any interruptions.

# `edit_cache.py` - Add and Remove

This script provides functionality to add or remove a specified, custom file type from each project in the data cache. For instance, for every project in the destination folder, `addToAll` may add an SBML file or `removeFromAll` may exclude all the CSV files. 

Every edit to the directory will be recorded in a specified "history log" file.
This same log will be used to recognize which directories have already been processed. This allows for the operation to detect where it left off and pick up where it left off should the operation be interrupted or paused.

## Demo
![](https://github.com/ModelEngineering/ExplorerSB/blob/backend/scripts/directory_doctor_demo.gif)

## Usage Guide

<!-- **1. The following must be configured before use:** -->

<!-- 1. `config.yaml`
    - extension: The extension of the file type that is being added or removed
    - history_file: File path to where the history log of changes will be located
    - data_cache: File path to the final, unzipped data cache that is in use
    - stage_dir: File path to the staging directory created during the build of the data cache (please see mk_data description above)
2. `checkIsDesired` Located in edit_cache.py, this is a custom function written by the user to 
3. `EXT`
4. custom function and `checkIsDesired`
5. The script itself to call the desired function (`addToAll` or `removeFromAll`) -->

### Step 1. Configure `config.yaml`: 
**This file is a one-stop-shop to configure multiple file paths and variables that are used to run `edit_cache` and must specify the following:**
- **1. `extension`**: a `string` representation of a target file-type's extension. For instance, `.xml` files should configure this as `extension: "xml"`
- **2. `history_file`**: File path to where the history log of changes will be located
- **3. `data_cache`**: The path to the folder that will hold the finalized project files (when adding to all projects) OR the path to the folder from which to remove files from each project (when removing from each project). The script will visit each project housed in this directory.
- **4. `stage_dir`**: File path to the staging directory created during the build of the data cache (please see mk_data description above). 
    - Adding to each project requires a "staging" directory that holds all possible, available files associated with a given project (`DATA_CACHE` may be a specialized subset of this containing only the files we desire). Therefore, `addToAll` will visit this directory and search for a matching project directory within it to pull the additional file from. For instance, `DATA_CACHE` > `proj_1080` may contain

        - `report.csv`
        - `directory.json`
        - `figure1.png`

        `STAGE_DIR` > `proj_1080` may contain a superset of this such as

        - `report.csv`
        - `directory.json`
        - `figure1.png`
        - `biomodel3.xml`
        - and more (the full list of files associated with `proj_1080`)

    - If one desires to add `.xml` files to each project, it will be pulled from the `STAGE_DIR`.

### Step 2. Assign a custom function to `checkIsDesired`: 
The way to detect a certain file type is largely dependent on that particular file. For instance, the same methods cannot be used to distinguish a JSON file from an SBML file. Therefore, a custom function must be provided within the `edit_cache.py` script (see "Functions in `edit_cache.py` for details).

The variable within the script - `checkIsDesired` - must then be updated to be set to this custom function.
For example: `checkIsDesired = isSbmlFile` (name of custom function)

### Step 3. Run the script: 
Once Steps 1 & 2 are complete, the script can be run from the command line.
It takes 1 argument: `add` or `remove`.
- **TO RUN SCRIPT**: `python edit_cache.py` add OR `python edit_cache.py remove`

If the run is interrupted or paused, it may pick up where it left off by running the same command. If the user would instead like to re-run the script from the beginning, they may provide a blank `history_file` path in `config.yaml`.
<!-- **1. `DATA_CACHE`**: The path to the folder that will hold the finalized project files (in the case of addToAll)
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
Ex. `addToAll(checkIsDesired)` -->

## Functions in `edit_cache.py`

### **`checkIsDesired`**: 
Given a file path, returns T/F based on if that file is of the desired type (CUSTOM DEFINED)

#### **Parameters**: `path: str`: the path to a file to examine and determine if it the target file-type or not.

- For example, `"data/proj_1080/model.xml"`

#### **Return**: `isTarget: bool`: A True/False value based on if the file at the provided path is the target file type.


### **`addToAll`**: 
Given a method to distinguish file types, searches in `stage_dir` to add files of that desired type into each project folder. Updates `history_file` with the addition of any file in any project.

**Parameters:** `checkIsDesired: function`: name of a custom function that distinguishes if a file is the target type (see `checkIsDesired` above)

**Return:** None: Modifies each project in `data_cache`

### **`removeFromAll`**: 
Given a method to distinguish file types, remove files of that desired type from each project folder in data_cache. Updates `history_file` with the removal of any file in any project.

**Parameters:** `checkIsDesired: function`: name of a custom function that distinguishes if a file is the target type (see `checkIsDesired` above)

**Return:** None: Modifies each project in `data_cache`


