'''Converts an HDF5 file to DataFrames using meta data constructed from the SEDML file.'''


import src.ExplorerSB.constants as cn
import src.ExplorerSB.util as util

import collections
import h5py
import json
import os
import pandas as pd
import typing


class _Descriptor(object):
    """This is the primary data structure for the converter."""
    def __init__(self, name:str=None, ids:list=None, labels:list=None, df:pd.DataFrame=None, is_truncate=True):
        """
        Constructor.

        Args:
            name: name of the dataset
            ids: list of sedmlDataSetIds
            labels: list of sedmlDataSetLabels
            df: DataFrame
            is_truncate: bool (truncate the labels to eliminate inconsistencies between 'plot' and 'report' datasets)
        """
        self.name = name
        self.labels = labels
        self.df = df 
        if is_truncate:
            # Truncate the labels to eliminate inconsistencies between 'plot' and 'report' datasets
            self.ids = self._truncate_ids(ids)

    @staticmethod
    def _truncate_ids(labels):
        """
        Truncates the ids to eliminate inconsistencies between 'plot' and 'report' datasets for generic names.
        A generic name is detected by the presence of "auto" in the id.

        Args:
            labels: list-str
        Returns:
            list-str
        """
        if labels is None:
            return
        new_labels = []
        for label in labels:
            new_label = label
            # in case bytes are returned rather than str
            try:
                label = label.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            if "auto" in label:
                pos = label.find("task")
                if pos >= 0:
                    new_label = label[pos:]
                    # Time is structured differently from the other labels.
                    if not "_" in new_label:
                        new_label = "time"
            new_labels.append(new_label)
        return new_labels

    def __repr__(self):
        return "Descriptor(name=%s, ids=%s, labels=%s, df.name=%s)" % (self.name, self.ids, self.labels, self.df.name)


class H5Converter(object):

    def __init__(self, h5_path:str, csv_dir=None):
        """
        Converts datasets in an HDF5 file to DataFrames.
        Optionally writes the DataFrames to CSV files if csv_path is not None.

        Args:
            path: str (path to HDF5 file)
            csv_dir: str (path to CSV files)
        """
        self.h5_path = h5_path
        self.csv_dir = csv_dir
        # Internal data
        self.descriptor_dct = {}  # key: dataset name, value: Descriptor
        # Outputs
        self.result_dct = {}  # key: dataset name, value: DataFrame

    def convert(self):
        """Converts the HDF5 file to DataFrames."""
        self._makeDescriptorDct()
        self._renamePlotColumns()
        self._createResult()
        if self.csv_dir is not None:
            self._writeCsv()

    def _makeDescriptorDct(self):
        """
        Creates the descriptor dictionary by recursively searching the HDF5 file.

        Globals Created:
            self.descriptor_dct: key: dataset name, value: Descriptor
        """
        def processH5Item(item, group_names):
            """
            Recursively searches groups for datasets with sedmlDataSetIds. Updates self.descriptor_dct.
            
            Args:
                item: Group/Dataset
                group_names: list-str
                df_dct: key: name, value: DataFrame
            """
            names = list(group_names)
            if "Dataset" in str(type(item)):
                # Encountered a leaf in the container graph
                if "sedmlDataSetLabels" in item.attrs.keys():
                    index = list(item.attrs["sedmlDataSetLabels"])
                    if len(item.shape) != 2:
                        print("** Ignored item with strange shape %s" % str(item.shape))
                        return []
                    name = item.attrs["sedmlId"]
                    df = pd.DataFrame(item[:,:], index=index)
                    df = df.T
                    df.name = name
                    descriptor = _Descriptor(name=name, ids=item.attrs["sedmlDataSetIds"],
                                labels=item.attrs["sedmlDataSetLabels"], df=df)
                    self.descriptor_dct[descriptor.name] = descriptor
            else:
                for key in item.keys():
                    new_names = list(names)
                    new_names.append(key)
                    processH5Item(item[key], new_names)
                return
        #
        self.descriptor_dct = {}  # key: dataset name, value: Descriptor
        with h5py.File(self.h5_path, 'r') as fd:
            processH5Item(fd, [])

    def _renamePlotColumns(self):
        """
        Renames the plot columns to correspond to the report columns.

        Globals Updated:
            self.descriptor_dct: key: dataset name, value: Descriptor
        """
        # Find the 'report' dataset to match plot dataset
        for name, descriptor in self.descriptor_dct.items():
            try:
                name = name.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            if "plot" in name:
                plot_descriptor = descriptor
                plot_df = plot_descriptor.df
                plot_name = name
                report_name = plot_name.replace("plot", "report")
                if report_name in self.descriptor_dct.keys():
                    # Construct the conversion dictionary
                    report_descriptor = self.descriptor_dct[report_name]
                    report_id_dct = {k: v for k, v in  zip(report_descriptor.ids, report_descriptor.labels)}
                    plot_label_dct = {k: v for k, v in  zip(plot_descriptor.labels, plot_descriptor.ids)}
                    # Convert the ids. Have to consider the position of the labels.
                    plot_rename_dct = {}
                    for label in plot_df.columns:
                        plot_id = plot_label_dct[label]
                        if plot_id in report_id_dct.keys():
                            plot_rename_dct[label] = report_id_dct[plot_id]
                    plot_df = plot_df.rename(columns=plot_rename_dct)
                    plot_df.name = plot_name
                    plot_descriptor.df = plot_df

    def _createResult(self):
        """
        Constructs the result dataframe.

        Globals Read:
            self.descriptor_dct: key: dataset name, value: Descriptor
        Globals Updated:
            self.result_dct: key: dataset name, value: DataFrame
        """
        # Find the 'report' dataset to match plot dataset
        for name, descriptor in self.descriptor_dct.items():
            plot_name = name
            self.result_dct[plot_name] = descriptor.df
        
    def _writeCsv(self):
        # Writes the dataframes to CSV files
        for name, df in self.result_dct.items():
            try:
                name = name.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            filename = name + ".csv"
            path = os.path.join(self.csv_dir, filename)
            df.to_csv(path, index=False)
