"""
Touches all projects in the cache to add or exclude a specified file type.
"""
import src.ExplorerSB.constants as cn
import os
import shutil
import datetime
import argparse
import csv
import yaml

'''
USAGE GUIDE:
1. Edit DATA_CACHE and STAGE_DIR paths
2. Define EXT to be the extension of the desired file to include/exclude
3. Define custom function to detect a filetype and edit checkIsDesired
4. Edit script and pass in checkIsDesired as an argument
'''

# TODO: Update README on how to use changelog - DONE
# Must define name for changelog 'added<filetype>.txt' to ADD_HIST_PATH
# or 'remove<filetype>.txt' to REMOVE_HIST_PATH

# ARGPARSE - DEFINE USER INPUT VARIABLES
parser = argparse.ArgumentParser()
parser.add_argument("modify", help=" \"add\" to ADD from staging or \"remove\" to REMOVE a filetype", type=str)
args = parser.parse_args()
print(args.modify)

# # Define paths and constants
# SRC_PATH = os.path.join(cn.PROJECT_DIR, 'src')
# UI_PATH = os.path.join(SRC_PATH, 'UI')
# EXT = 'xml' # Define the extension of the file type to include/exclude
# HIST_PATH = os.path.join(SRC_PATH, 'changelog')
# # ADD_HIST_PATH = os.path.join(HIST_PATH, 'addedSBML.txt')
# # COMPLETED_PROJ = os.path.join(HIST_PATH, 'completed_projs.txt')
# SBML_HIST_PATH = os.path.join(HIST_PATH, 'sbml_log.csv')

# # EDITABLE PATHS
# # path to "public" folder whose files must be updated
# DATA_CACHE = os.path.join(UI_PATH, 'test_public') # Ex. /Users/juliep/Documents/SauroLab/ExplorerSB/src/UI/test_public 
# # path to dir which holds all available files for each project downloaded from BioSim
# STAGE_DIR = cn.STAGE_DIR # is the same as in constants.py
# # Ex. /Users/juliep/Documents/SauroLab/ExplorerSB/staging

# Load in with YAML
with open('scripts/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    print(config)

    EXT = config['extension']
    HIST_FILE = config['history_file']
    DATA_CACHE = config['data_cache']
    STAGE_DIR = config['stage_dir']
    # checkIsDesired = config['check_is_desired']
    print(HIST_FILE, DATA_CACHE, STAGE_DIR)

# Define custom functions to compare a file against the desired file type
def isSbmlFile(path):
    """
    Checks if the given .xml file is SBML

    Returns: T/F if it does/does not contain SBML
    """
    with open(path, "r") as fd:
        lines = fd.readlines()
    model = "\n".join(lines)
    return ("sbml" in model)

def isCellMlFile(path):
    """
    Checks if the given .cellml file is the proper cellml format

    Returns: T/F if the given path does/does not contain a cellml file
    """
    with open(path, "r") as fd:
        lines = fd.readlines()
    model = "\n".join(lines)
    return ("www.cellml.org" in model)


# TO NOTE
# 1. Records IDs of finished projects (after all files have been processed)
# to allow the process to pick up where it finished off.
# 2. Only records a project as "finished" after all files in the staging directory have been reviewed.
# - Interruption while looping through files? 
# - Will lose info on already processed files BUT will always add all available.
def addToAll(checkIsDesired):
    # breakpoint()
    # try:
    #     # 1. Get already modified project ID's into a set
    #     done_file = open(COMPLETED_PROJ,"r")
    #     finished_projects = done_file.readlines()
    #     # strip off whitespace character
    #     finished_projects = [k.strip() for k in finished_projects]
    #     finished_projects = set(finished_projects)
    #     done_file.close()
    # except FileNotFoundError:
    #     print('ERROR: Log of completed projects at {} does not exist'.format(COMPLETED_PROJ))
    #     return
    
    # 2. Open file for recording details about added files
    # 'a' for writing. "The data being written will be inserted at the end of the file. 
    # Creates a new file if it does not exist."
    # changelog_file = open(ADD_HIST_PATH,"a")
    # 3. Open file for completed projects only
    # completed_projs = open(COMPLETED_PROJ, "a")
    finished_projects = set()
    with open(HIST_FILE, 'a', newline='') as changelog_file:
        writer = csv.writer(changelog_file)
        if os.path.getsize(HIST_FILE) < 1:
            # Add headers to new file
            fields = ['project_id', 'files_added', 'datetime', 'edit_action']
            writer.writerow(fields)

        list_public = os.listdir(DATA_CACHE) # get list of all projects in the cache
        for proj in list_public:
            proj_path = os.path.join(DATA_CACHE, proj)
            if proj in finished_projects:
                print('Project {} already processed for addition of file'.format(proj))
            else:
                # Need to go to the STAGE_DIR to see if it exists
                print("Looking in stage_dir")
                # Create path to proj in STAGE_DIR
                stage_proj_path = os.path.join(STAGE_DIR, proj)
                # List the files the project contains
                try:
                    list_proj_stagefiles = os.listdir(stage_proj_path)
                    # added_files = []
                    # Look for the desired extension
                    for file in list_proj_stagefiles:
                        # Only check the file if it has the proper extension
                        if file.endswith(EXT):
                            stage_filepath = os.path.join(stage_proj_path, file)
                            if checkIsDesired(stage_filepath):
                                # Add to the project if correct file
                                source = stage_filepath
                                dest = proj_path
                                shutil.copy(source, dest)

                                # Record in csv
                                writer.writerow([str(proj), str(file), str(datetime.datetime.now()), 'added'])
                                # Add to array of added files for this project
                                # added_files.append(file)

                                # Record modified project ID into changelog
                                # TODO: ID is written as soon as 1 file is added
                                # Change to make more robust when interrupted before all n SBML
                                # files from staging could be transferred
                                # changelog_file.write(str(proj) + '\n')
                                print('Copied file {} to {}'.format(file, dest))
                    
                    # Finished processing all files in this project.
                    # Record the modifications
                    # result = []
                    # result.append(str(proj))                    # PROJECT ID
                    # result.append(str(added_files))             # LIST ADDED FILES
                    # result.append(str(datetime.datetime.now())) # TIMESTAMP
                    # result.append('added')                      # ACTION
                    # result = ",".join(result)

                    # # Record in 1. Completed Projects AND 2. Added Files
                    # completed_projs.write(str(proj) + '\n')
                    # changelog_file.write(str(result) + '\n')
                except FileNotFoundError:
                    print("Project not found in staging directory")
        
        # Close down both files
        # changelog_file.close()
        # completed_projs.close()

# Loop through each project in the DATA_CACHE directory
# Loop through each file in each project
# If desired file in project:
    # remove from project
def removeFromAll(checkIsDesired):
    # breakpoint()
    list_public = os.listdir(DATA_CACHE) # get list of all projects in the cache
    for proj in list_public:
        proj_path = os.path.join(DATA_CACHE, proj)
        # Loop through all files in the project
        for file in os.listdir(proj_path):
            proj_file_path = os.path.join(proj_path, file)
            if proj_file_path.endswith(EXT):
                # Check if the file is the desired file
                if checkIsDesired(proj_file_path):
                    # Double check it exists
                    if os.path.exists(proj_file_path):
                        # Remove it
                        os.remove(proj_file_path)
                        print('Deleted {} from {}'.format(file, proj_file_path))

             

checkIsDesired = isSbmlFile # name of a custom function to detect a desired file type

if args.modify == "add":
    addToAll(checkIsDesired)

elif args.modify == "remove":
    removeFromAll(checkIsDesired)

'''
Testing
    1. Test basic where 1 file is transferred from staging to public
    2. Test where multiple files are valid and test that all are moved to public
'''

# Should add xml to 2e(BIOM), 21(Caravagna), NOT to 6e, e8(WholeCell), 4d (model.xml)
# Works as expected