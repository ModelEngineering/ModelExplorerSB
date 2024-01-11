'''Builds a single project. Constructs context data. Downloads files into staging area. Copies selected files to data directory.'''

"""
Project context:
    Abstract
    Citation
    DOI
    PROJECT_ID (key)
    RUNID
    TITLE
    PAPER_URL

Conventions:
    In general, the key for a dictionary is the project_id.
    Dictionaries with an "inv" prefix, have a value of project_id.

Notes
  1. Does not keep any .json file
"""


import src.ExplorerSB.constants as cn
from src.ExplorerSB.h5converter import H5Converter
import src.ExplorerSB.util as util
from src.ExplorerSB.summary_parser import BiosimulationsSummaryParser, BiomodelsSummaryParser
from src.ExplorerSB.project_base import ProjectBase

import collections
import h5py
import json
import os
import pandas as pd
import shutil
import tellurium as te
import typing
import zipfile

# The following extensions are removed from the output directory
EXCLUDED_EXTENSIONS = ["ode", "m", "vcml", "rdf", "owl", "txt", "sci", "zip", "json", "h5", "nml"]

# Notes:
# Removed xml from excluded extensions. xml contains SBML so xml files are handled separately.


class ProjectBuilder(ProjectBase):

    def __init__(self, project_id: str, runid: str, data_dir:str=cn.DATA_DIR, stage_dir:str=cn.STAGE_DIR):
        """
        Creates the context entry for a project.

        Args:
            project_id: unique identifier for a project
            data_dir: directory in which project context is stored
        """
        super().__init__(project_id, data_dir=data_dir)
        self.stage_dir = stage_dir
        self.runid = runid
    
    def buildProject(self):
        """
        Constructs the context entry for a project

        Returns:
            dict: key, value for each context entry
        """
        if self.is_biomodels:
            summary_parser = BiomodelsSummaryParser(self.project_id)
        else:
            summary_parser = BiosimulationsSummaryParser(self.project_id)
        summary_parser.do()
        util.trace("Executed summary parser", 2)
        # Create the context information
        self.abstract = summary_parser.abstract
        if self.abstract == "":
            print("No abstract for %s" % self.project_id)
        self.citation = summary_parser.citation
        self.title = summary_parser.title
        self.doi = summary_parser.doi
        self.paper_url = summary_parser.paper_url
        util.trace("Acquired fields from summary parser", 2)
        # Construct and populate the staging directory
        _ = self._makeStagingData()  # Download the output files
        util.trace("Acquired staging data", 2)
        output_dir_path = self._downloadOutput()  # Download the output files
        if output_dir_path is None:
            util.trace("No output files found.", 2)
        else:
            util.trace("Downloaded output files.", 2)
            self._makeCsvFromH5()  # Create CSV files from the HDF5 files
            util.trace("Constructed CSV files from HDF5 file.", 2)
            self._makeReadableModel()
            util.trace("Constructed readable model.", 2)
        # Create the output data
        self._makeZipArchive()
        util.trace("Created zip archive.", 2)

    def _makeZipArchive(self):
        """
        Creates a zip archive of the stage files, including a
        JSON file with the names of the files in the directory.
        """
        project_data_dir = self.getProjectDir(self.data_dir)
        if os.path.isdir(project_data_dir):
            shutil.rmtree(project_data_dir)
        shutil.copytree(self.getProjectDir(self.stage_dir), project_data_dir)
        # TODO: Prune XML files that are not SBML
        self._pruneNonSbmlXml()
        _ = [self._removeFiles(project_data_dir, e) for e in EXCLUDED_EXTENSIONS]
        # Remove all subdirectories
        for ffile in os.listdir(project_data_dir):
            path = os.path.join(project_data_dir, ffile)
            if os.path.isdir(path):
                shutil.rmtree(path)
        # Create the directory of files
        ffiles = os.listdir(project_data_dir)
        ffiles = [f for f in ffiles if not f in [".", ".."]]
        ffile_json = json.dumps([{"file": f} for f in ffiles])
        path = os.path.join(project_data_dir, cn.DIRECTORY_FILE)
        with open(path, "w") as fd:
            fd.write(ffile_json)
        # Create the zip archive
        output_filename = cn.ZIP_PAT % self.runid
        output_filename = output_filename.replace(".zip", "")
        output_filename = os.path.join(self.data_dir, output_filename)
        path = shutil.make_archive(output_filename, "zip", project_data_dir)
        # Eliminate the data directory
        shutil.rmtree(project_data_dir)

    def _makeStagingData(self)->typing.List[str]:
        """
        Copies the files to the staging directory, creates CSV files from HDF5, and creates Antimony models.

        Returns:
            list of paths copied
        """
        copied_paths = []
        project_dir = self.getProjectDir(self.stage_dir, is_create=True)
        file_urls = self._getUrlFileList()
        for file_url in file_urls:
            path = self._copyUrlFile(file_url, project_dir)
            if path is None:
                continue
            if path.endswith(cn.JSON):
                continue
            copied_paths.append(path)
        return copied_paths
    
    def _getUrlFileList(self)->typing.List[str]:
        """
        Gets the list of file URLs for the project.

        Returns:
            list of URLs for project files
        """
        """
        Writes the files for this runid to the cache.

        Returns
        -------
        list-str (each string is a URL)
        """
        url = cn.API_URL + "/files/" + self.runid
        _, _, response_lst = util.readBiosimulations(url)
        file_urls = [x["url"] for x in response_lst]
        return file_urls
    
    def _downloadOutput(self)->str:
        """
        Downloads the output file and unzips it. Moves selected files to the
        project's staging directory.

        Returns:
            path to the directory
        """
        LOCAL_FILENAME = "output.zip"
        url = "%s/results/%s/download" % (cn.API_URL, self.runid)
        project_dir = self.getProjectDir(self.stage_dir, is_create=True)
        zip_path = self._copyUrlFile(url, project_dir, local_filename=LOCAL_FILENAME)
        # Unzip the file
        output_dir = os.path.join(project_dir, "outputs")
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        if not os.path.isfile(zip_path):
            return None
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(project_dir)
        # Move the HDF5 files to the staging directory
        ffiles = [f for f in os.listdir(output_dir) if f.endswith(".h5") or f.endswith(".xml")]
        for ffile in ffiles:
            if os.path.isfile(os.path.join(project_dir, ffile)):
                os.remove(os.path.join(project_dir, ffile))
            shutil.move(os.path.join(output_dir, ffile), project_dir) 
        #
        return output_dir
    
    @staticmethod 
    def _removeFiles(directory:str, extension:str):
        """
        Removes files with the designated extension.

        Args:
            directory: directory to clean
            extension:
        """
        ffiles = [f for f in os.listdir(directory) if f.endswith(extension)]
        for ffile in ffiles:
            os.remove(os.path.join(directory, ffile))

    def _pruneNonSbmlXml(self):
        """
        Removes all .xml files from the given directory that are not SBML files.

        Args:
            directory: directory to remove xml but retain sbml from
        """
        # get the directory (data_dir since the rest of the extensions are pruned out of here)
        project_data_dir = self.getProjectDir(self.data_dir)

        # gather only the xml files
        ffiles = [f for f in os.listdir(project_data_dir) if f.endswith("xml")]

        # if they are not SMBL, remove
        for ffile in ffiles:

            # form the path to that xml file
            file_path = os.path.join(project_data_dir, ffile)
            if not self._isSbmlFile(file_path):
                os.remove(file_path)

    def _isSbmlFile(self, path):
        """
        Checks if the given .xml file is SBML

        Returns: T/F if it does/does not contain SBML
        """
        # TODO: What does "manifest" check for?
        # splits = os.path.splitext(path)
        # if (splits[1] == ".xml") and ("manifest" not in path):

        with open(path, "r") as fd:
            lines = fd.readlines()
        model = "\n".join(lines)
        return ("sbml" in model)

    def _copyUrlFile(self, file_url:str, dir_path:str, local_filename:str=None)->str:
        """
        Copies the file in the URL to the specified directory for the runid.

        Args:
            file_url: URL to the file
            dir_path: Local directory in which file is placed

        Returns:
            path of copied file
        """
        try:
            response, _, _ = util.readBiosimulations(file_url, allow_redirects=True)
        except:
            print("\n**Could not access %s" % file_url)
            return
        if local_filename is None:
            local_filename = util.getFilenameFromUrl(file_url)
        output_path = os.path.join(dir_path, local_filename)
        with open(output_path, 'wb') as fd:
            fd.write(response.content)
        return output_path

    def _makeCsvFromH5(self):
        """
        Creates CSV files from the HDF5 files.
        """
        
        h5_path = self._getH5FilePath()
        if self.stage_dir is not None:
            project_stage_dir = self.getProjectDir(self.stage_dir)
        else:
            project_stage_dir = None
        converter = H5Converter(h5_path, csv_dir=project_stage_dir)
        _ = converter.convert()
    
    def _getH5FilePath(self)->str:
        """
        Provide the path to the HDF5 output file.

        Returns:
            path to file (or None)
        """
        project_stage_dir = self.getProjectDir(self.stage_dir)
        ffiles = [f for f in os.listdir(project_stage_dir) if ".h5" in f]
        if len(ffiles) == 0:
            print("*** No output directory for project %s" % self.project_id)
            ffile = None
        elif len(ffiles) > 1:
            print ("*** Multile h5 files. Using the first.")
            ffile = ffiles[0]
        else:
            ffile = ffiles[0]
        if ffile is not None:
            return os.path.join(project_stage_dir, ffile)
        else:
            return None
    
    def _makeReadableModel(self, is_write:bool=True, is_replace:bool=False)->str:
        """
        Converts a model to human readable text, if possible. Currently only
        supports conversion to Antimony. 

        Args:
            is_write: write the model and data to the cache
            is_replace: replace the file if it exiss
            cache_dir: where cached files are
        Returns:
            str: antimony model
        """
        # Get path to the antimony file
        project_stage_dir = self.getProjectDir(self.stage_dir)
        filename = "%s.ant" % self.project_id
        ant_path = os.path.join(project_stage_dir, filename)
        # Handle existing Antimony file
        if (not is_replace) and (os.path.isfile(ant_path)):
            with open(ant_path, "r") as fd:
                lines = fd.readlines()
            model_str = "".join(lines)
        # No existing Antimony file
        else:
            # See if there is an SBML file
            paths = self.getFilePaths(self.stage_dir)
            sbml_path = None
            for path in paths:
                splits = os.path.splitext(path)
                if (splits[1] == ".xml") and ("manifest" not in path):
                    with open(path, "r") as fd:
                        lines = fd.readlines()
                    model = "\n".join(lines)
                    if not "sbml" in model:
                        continue
                    sbml_path = path
                    break
            # Construct the model string
            model_str = None
            if sbml_path is not None:
                try:
                    rr = te.loadSBMLModel(sbml_path)
                    model_str = rr.getAntimony()
                except:
                    pass
            # Write the file
            if is_write and (model_str is not None):
                with open(ant_path, 'w') as fd:
                    fd.writelines(model_str)
        #
        return model_str