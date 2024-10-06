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
import pandas as pd

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
# *If the file has already been copied, will overwrite the old one
# at most, duplicate work is the maximum number of files in a single directory
# No duplicate files because will overwrite if a file already exists in the repo
# to copy to
def addToAll(checkIsDesired):
    
    # Open file for recording details about added files
    # 'a' for writing. "The data being written will be inserted at the end of the file. 
    # Creates a new file if it does not exist."

    # Populate set with completed projects parsed from history log
    with open(HIST_FILE, 'a', newline='') as changelog_file:
        finished_projects = set()
        writer = csv.writer(changelog_file)
        if os.path.getsize(HIST_FILE) < 1:
            # Add headers to new file
            fields = ['project_id', 'file_added', 'datetime', 'edit_action']
            writer.writerow(fields)
        else:
            # Parse for completed projects
            df = pd.read_csv(HIST_FILE)
            completed_mask = df['edit_action'] == 'COMPLETE_ADD'
            completed = df[completed_mask]
            finished_projects = set(completed['project_id'])

        list_public = os.listdir(DATA_CACHE) # get list of all projects in the cache
        for proj in list_public:
            if proj in finished_projects:
                print('Project {} already processed for addition of file'.format(proj))
                continue
            proj_path = os.path.join(DATA_CACHE, proj)
            # Otherwise, need to go to the STAGE_DIR for that project
            print("Looking in stage_dir")
            stage_proj_path = os.path.join(STAGE_DIR, proj)
            try:
                list_proj_stagefiles = os.listdir(stage_proj_path)
                # Look for the desired extension
                for file in list_proj_stagefiles:
                    stage_filepath = os.path.join(stage_proj_path, file)
                    # Only check the file if it has the proper extension
                    if file.endswith(EXT) and checkIsDesired(stage_filepath):
                        # Add to the project if correct file
                        source = stage_filepath
                        dest = proj_path
                        shutil.copy(source, dest)

                        # Record in csv
                        writer.writerow([str(proj), str(file), str(datetime.datetime.now()), 'added'])
                        print('Copied file {} to {}'.format(file, dest))

                # Record project as completed
                writer.writerow([str(proj), '', str(datetime.datetime.now()), 'COMPLETE_ADD'])
                finished_projects.add(str(proj))
            except FileNotFoundError:
                print("Project not found in staging directory")
        
        # with open will automatically close file


def removeFromAll(checkIsDesired):
    # Gather completed projects
    with open(HIST_FILE, 'a', newline='') as changelog_file:
        finished_projects = set()
        writer = csv.writer(changelog_file)
        if os.path.getsize(HIST_FILE) < 1:
            # Add headers to new file
            fields = ['project_id', 'file_added', 'datetime', 'edit_action']
            writer.writerow(fields)
        else:
            # Parse for completed projects
            df = pd.read_csv(HIST_FILE)
            completed_mask = df['edit_action'] == 'COMPLETE_REMOVE'
            completed = df[completed_mask]
            finished_projects = set(completed['project_id'])


        list_public = os.listdir(DATA_CACHE)
        # Loop through all projects
        for proj in list_public:
            if proj in finished_projects:
                print('Project {} already processed for removal of files'.format(proj))
                continue   
            # Otherwise, loop through all files in project to see if remove
            proj_path = os.path.join(DATA_CACHE, proj)
            for file in os.listdir(proj_path):
                proj_file_path = os.path.join(proj_path, file)
                if (proj_file_path.endswith(EXT) and 
                    checkIsDesired(proj_file_path) and
                    os.path.exists(proj_file_path)
                ):
                    # Remove it
                    os.remove(proj_file_path)
                    writer.writerow([str(proj), str(file), str(datetime.datetime.now()), 'removed'])
                    print('Deleted {} from {}'.format(file, proj_file_path))
            writer.writerow([str(proj), '', str(datetime.datetime.now()), 'COMPLETE_REMOVE'])
            finished_projects.add(str(proj))
             
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