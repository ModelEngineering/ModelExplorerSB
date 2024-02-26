import src.ExplorerSB.constants as cn
from src.ExplorerSB.project_builder import ProjectBuilder

import os
import pandas as pd
import shutil
import unittest
import urllib3
import zipfile


IGNORE_TEST = False
IS_PLOT = False
PROJECT_ID = "Yeast-cell-cycle-Irons-J-Theor-Biol-2009"
RUNID = "61fea483f499ccf25faafc4d"
PROJECT_ID = "BIOMD0000000001_amici_A_kinetic_mechanism_for_nicoti"
RUNID = "647106f00dcacb55678b35f4"
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TEST_DIR, "test_data")
STAGE_DIR = os.path.join(TEST_DIR, "stage_data")
CONTEXT_FILE = os.path.join(DATA_DIR, "context.csv")
SAVED_CONTEXT_FILE = os.path.join(DATA_DIR, "saved_context.csv")
URLS = [
                "https://storage.googleapis.com/files.biosimulations.org/simulations/621d90b9b50991044c7a1ea6/contents/iYS854.xml",
                "https://storage.googleapis.com/files.biosimulations.org/simulations/621d42c187550e369891bbdb/contents/screenshot4.png"
        ]


#############################
# Tests
#############################
class TestProjectBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = self.makeBuilder()
        self.remove()

    def tearDown(self):
        self.remove()

    def mkdir(self, project, dest_dir=None):
        if dest_dir is None:
            dest_dir = project.stage_dir
        dir_path = os.path.join(dest_dir, project.runid)
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        os.mkdir(dir_path)
        return dir_path
    
    def remove(self):
        def removeDir(dir_path):
            path = os.path.join(dir_path, self.builder.runid)
            if os.path.isdir(path):
                shutil.rmtree(path)
        #
        removeDir(self.builder.data_dir)
        removeDir(self.builder.stage_dir)
        # Remove zip files
        ffiles = os.listdir(self.builder.data_dir)
        for ffile in ffiles:
            if ffile.endswith(".zip"):
                os.remove(os.path.join(self.builder.data_dir, ffile))

    def makeBuilder(self):
        builder = ProjectBuilder(PROJECT_ID, RUNID, data_dir=DATA_DIR, stage_dir=STAGE_DIR)
        # Ensure that the project cache is present
        _ = builder.getProjectDir(STAGE_DIR, is_create=True)
        return builder

    def testConstructor(self):
        if IGNORE_TEST:
            return
        self.assertIsNotNone(self.builder.project_id)
        stage_dir = self.builder.getProjectDir(STAGE_DIR)
        self.assertEqual(self.builder.runid, RUNID)

    def testGetUrlFileList(self):
        if IGNORE_TEST:
           return
        builder = self.makeBuilder()
        self.mkdir(builder)
        urls = builder._getUrlFileList()
        for url in urls:
            try:
                _ = urllib3.util.parse_url(url)
                is_parsed = True
            except:
                is_parsed = False
            self.assertTrue(is_parsed)

    def testCopyUrlFile(self):
        if IGNORE_TEST:
            return
        builder = self.makeBuilder()
        dir_path = self.mkdir(builder)
        def test(url):
            file_path = builder._copyUrlFile(url, dir_path)
            self.assertTrue(os.path.isfile(file_path))
        #
        ffiles = os.listdir(dir_path)
        self.assertEqual(len(ffiles), 0)
        for url in URLS:
            test(url)
        ffiles = os.listdir(dir_path)
        self.assertGreater(len(ffiles), 0)

    def testGetFilePaths(self):
        if IGNORE_TEST:
            return
        # Setup
        url = URLS[0]
        _ = self.mkdir(self.builder)
        dest_dir = self.builder.getProjectDir(self.builder.stage_dir)
        file_path = self.builder._copyUrlFile(url, dest_dir)
        # Test
        ffiles = self.builder.getFilePaths(self.builder.stage_dir)
        self.assertGreater(len(ffiles), 0)
        self.assertTrue(isinstance(ffiles[0], str))
        for ffile in ffiles:
            self.assertTrue(os.path.isfile(ffile))

    def testDownloadOutput(self):
        if IGNORE_TEST:
            return
        builder = self.makeBuilder()
        path = builder._downloadOutput()
        self.assertTrue(os.path.isdir(path))
        ffiles = os.listdir(path)
        self.assertGreater(len(ffiles), 0)

    def testGetH5FilePath(self):
        if IGNORE_TEST:
            return
        # Setup
        builder = self.makeBuilder()  # Create the builder
        builder._downloadOutput()  # Download the output
        # Test
        path = builder._getH5FilePath()
        self.assertTrue(os.path.isfile(path))
        splits = os.path.splitext(path)
        self.assertEqual(splits[1], ".h5")
    
    def testMakeCsvFromH5(self):
        if IGNORE_TEST:
            return
        # Setup
        builder = self.makeBuilder()
        builder._downloadOutput()  # Download the output
        # Test
        builder._makeCsvFromH5()
        path = builder.getProjectDir(builder.stage_dir)
        csv_files = [p for p in os.listdir(path) if ".csv" in p]
        self.assertGreater(len(csv_files), 0)

    def testMakeReadableModel(self):
        if IGNORE_TEST:
            return
        builder = self.makeBuilder()
        _ = builder._makeStagingData() 
        model_str = builder._makeReadableModel(is_write=True)
        stage_dir = builder.getProjectDir(STAGE_DIR)
        # Initial tests
        self.assertIsNotNone(model_str)
        self.assertGreater(len(model_str), 0)
        # See if the file was written
        ffiles = os.listdir(stage_dir)
        is_good = any([f for f in ffiles if ".ant" in f])
        self.assertTrue(is_good)

    def testMakeZipArchive(self):
        if IGNORE_TEST:
            return
        builder = self.makeBuilder()
        _ = builder._makeStagingData() 
        builder._makeZipArchive()
        zip_file = cn.ZIP_PAT % builder.runid
        zip_path = os.path.join(builder.data_dir, zip_file)
        self.assertTrue(os.path.isfile(zip_path))
        ffiles = os.listdir(builder.data_dir)
        self.assertTrue(zip_file in ffiles)

    def testPruneNonSbmlXml(self):
        builder = self.makeBuilder()
        _ = builder._makeStagingData() 
        ffiles = [ f for f in os.listdir(builder.getProjectDir(STAGE_DIR)) if ".xml" in f]
        # of xml before

        print(ffiles)
        builder._makeZipArchive()
        zip_file = cn.ZIP_PAT % builder.runid
        zip_path = os.path.join(builder.data_dir, zip_file)

        ffiles = [ f for f in os.listdir(builder.data_dir) if ".xml" in f]
        # self.assertLessEqual(postnum, prenum, "")
        # ffiles = os.listdir(builder.data_dir)
        # print(ffiles)
        # csv_files = [p for p in os.listdir(path) if ".csv" in p]
        # self.assertGreater(len(csv_files), 0)

    def testBuildProject(self):
        if IGNORE_TEST:
            return
        self.builder.buildProject()
        for attribute in cn.CONTEXT_KEYS:
            self.assertIsNotNone(self.builder.__getattribute__(attribute))
        self.assertGreater(len(self.builder.abstract), 0)
        # Check the files
        paths = self.builder.getFilePaths(self.builder.stage_dir)
        for path in paths:
            self.assertTrue(os.path.isfile(path))
   

if __name__ == '__main__':
    unittest.main()