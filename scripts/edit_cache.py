"""
Touches all projects in the cache to add or exclude a specified file type.
"""
import src.ExplorerSB.constants as cn
import os
import shutil

'''
USAGE GUIDE:
1. Edit DATA_CACHE and STAGE_DIR paths
2. Define EXT to be the extension of the desired file to include/exclude
3. Define custom function to detect a filetype and edit checkIsDesired
4. Edit script and pass in checkIsDesired as an argument
'''

# Define paths and constants
SRC_PATH = os.path.join(cn.PROJECT_DIR, 'src')
UI_PATH = os.path.join(SRC_PATH, 'UI')
EXT = 'xml' # Define the extension of the file type to include/exclude

# EDITABLE PATHS
# path to "public" folder whose files must be updated
DATA_CACHE = os.path.join(UI_PATH, 'test_public') # Ex. /Users/juliep/Documents/SauroLab/ExplorerSB/src/UI/test_public 
# path to dir which holds all available files for each project downloaded from BioSim
STAGE_DIR = cn.STAGE_DIR # is the same as in constants.py
# Ex. /Users/juliep/Documents/SauroLab/ExplorerSB/staging

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

# Loop through each project in the DATA_CACHE directory
# Loop through each file in each project
# If desired file not in project:
    # Find that project id in the STAGE_DIR 
    # loop through each file in the project in STAGE_DIR and
    # pass each file to the custom function
    # if is the desired file type
        # download the file into the DATA_CACHE folder under that project id

# Notes:
# If addToAll detects at least 1 file of the desired type included in the project
# in the public folder, it will not go and look for more.
# Must be fixed so that we have a better way of knowing if the project has been completed processing
def addToAll(checkIsDesired):
    breakpoint()
    list_public = os.listdir(DATA_CACHE) # get list of all projects in the cache
    for proj in list_public:
        proj_path = os.path.join(DATA_CACHE, proj)
        contains = False
        # Loop through all files in the project
        for file in os.listdir(proj_path):
            proj_file_path = os.path.join(proj_path, file)
            if proj_file_path.endswith(EXT):
                # Check if the file is the desired file
                if checkIsDesired(proj_file_path):
                    contains = True
                    #printf("%s already contains file" %proj)
                    print("Project already contains file")
                    break
        if not contains:
            # Need to go to the STAGE_DIR to see if it exists
            print("Looking in stage_dir")
            # Create path to proj in STAGE_DIR
            stage_proj_path = os.path.join(STAGE_DIR, proj)
            # List the files the project contains
            try:
                list_proj_stagefiles = os.listdir(stage_proj_path)
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
                            print("Copied file to proj")
            except FileNotFoundError:
                print("Project not found in staging directory")
             

checkIsDesired = isSbmlFile # name of a custom function to detect a desired file type
addToAll(checkIsDesired)

'''
Testing
    1. Test basic where 1 file is transferred from staging to public
    2. Test where multiple files are valid and test that all are moved to public
'''
