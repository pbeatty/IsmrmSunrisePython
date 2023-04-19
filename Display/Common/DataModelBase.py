"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Alan Kuurstra
Philip J. Beatty (philip.beatty@gmail.com)

2017, modified by Chad Harris
2017, modified by Philip Beatty
"""

__all__ = ["CommonDataState", "DataModel"]

from . import DisplayCore
import numpy as np
import pandas as pd
import matplotlib.cm as colormaps

from IPython.display import display

from qtpy import QtCore


class CommonDataState(QtCore.QObject):
    signalDataChange = QtCore.Signal()
    signalVisibleChange = QtCore.Signal(int, bool)
    signalMarkerChange = QtCore.Signal(int, int)    

    def GetNumDims(self):
        return self.dimsTable.shape[0]
    
    def GetDimValue(self, dimIndex, label):
        try:
            result = self.dimsTable.iloc[dimIndex, self.dimsTable.columns.get_loc(label)]
            return result
        except Exception as err:
            print("Exception in GetDimValue: {}".format(label))

        
    def GetCurrViewValue(self, label=None):
        try:
            colIndex = slice(None)
            if not label is None:
                colIndex = self.viewsTable.columns.get_loc(label)

            rVal = self.viewsTable.iloc[self.currViewIndex, colIndex]
            return rVal
        except Exception as err:
            print("Exception in GetCurrViewValue: {}".format(label))



            
    def __init__(self, dimShape):
        try:
            super(CommonDataState, self).__init__()


            def CreateDimsTable(dimShape):
                nDims = len(dimShape)

                names = ['x', 'y', 'z']
                colors = ['m', 'c', 'y']
                dimsTable = pd.DataFrame({'Name':names[0:nDims],
                                          'Shape':dimShape,
                                          'Color' : colors[0:nDims],
                                          'CurrLocation' : (np.array(dimShape)*0.5).astype(int)})
                return dimsTable
            
            def CreateViewsTable():
                # Set Name as index, but also leave as data column
                viewsTable = pd.DataFrame({'Name':['Magnitude', 'Phase', 'Real', 'Imaginary']})
                viewsTable = viewsTable.set_index('Name', drop=False)

                # Add data columns
                viewsTable['Index'] = range(4)

                viewsTable['ReductionFn'] = lambda x: np.abs(x)
                viewsTable.at['Phase', 'ReductionFn'] = lambda x: np.angle(x)

                #N.B. cannot use np.real(x) because it has different behavior
                # in scalar case. It returns a size 1 array instead of a scaler
                viewsTable.at['Real', 'ReductionFn'] = lambda x: x.real
                viewsTable.at['Imaginary', 'ReductionFn'] = lambda x: x.imag

                viewsTable['MaxMin'] = 1000.0 # cannot have a larger min than this
                viewsTable['MinMax'] = -1000.0 # cannot have a smaller max than this

                viewsTable.at['Phase', 'MaxMin'] = -3.1416
                viewsTable.at['Phase', 'MinMax'] =  3.1416
                viewsTable.at['Magnitude', 'MaxMin'] = 0.0

                return viewsTable

            #
            # viewsTable is a data frame, where each row completely
            # describes the settings for each type of view of the
            # (complex) data.  I am trying to make it so that the
            # viewer code does not need domain knowledge of how
            # particulary types of viewsTable should be displayed. That
            # info should all be kept here, in the DataModel
            #
            self.viewsTable = CreateViewsTable()

            # Set starting image type to Magnitude
            self.currViewIndex = self.viewsTable.loc['Magnitude', 'Index']
            self.dimsTable = CreateDimsTable(dimShape)
        except Exception as err:
            print("Exception in DataModelBase.CommonDataState.__init__: {}".format(err))




class DataModel(object):
    def __init__(self, numDataSeries, titles = None):
        """ 

        Parameters
        ----------

        """

        def MakeTitles(titles, numDataSeries):
            if isinstance(titles, str):
                prefix = titles
                titles = None
            else:
                prefix = "Image"

            if titles is None:
                titles = ["{} {}".format(prefix, ic) for ic in range(numDataSeries)]
            return titles


        try:
            titles = MakeTitles(titles, numDataSeries)
            colors = DisplayCore.MakeColors(numDataSeries)
            self.dataTable = pd.DataFrame({'Title': titles,
                                         'Color' : colors,
                                         'Visible' : True,
                                         'Index' : range(numDataSeries)})

        except Exception as err:
            DisplayCore.HandleException(err)



    def GetCurrDataSlice(self, datasetIndex, dim1Slice = slice(None), dim2Slice = slice(None), dim3Slice = slice(None)):
        #cs = self.commonState

        rFn = self.commonState.GetCurrViewValue('ReductionFn')
        currData = self.dataTable.iloc[datasetIndex, self.dataTable.columns.get_loc('Data')]
        if(currData.ndim == 1):            
            result = rFn(currData[dim1Slice])
        elif(currData.ndim == 2):
            result = rFn(currData[dim1Slice, dim2Slice])
        elif(currData.ndim == 3):
            result = rFn(currData[dim1Slice, dim2Slice, dim3Slice])
        return result

    
    def GetCurrViewValue(self, label=None):
        return self.commonState.GetCurrViewValue(label)

    def GetDimValue(self, dimIndex, label):
        return self.commonState.GetDimValue(dimIndex, label)

    def GetNumDatasets(self):
        return self.dataTable.shape[0]

    def GetNumDims(self):
        return self.commonState.GetNumDims()
    
    def GetDataTableValue(self, index, label=None):
        
        colIndex = slice(None)
        if not label is None:
            colIndex = self.dataTable.columns.get_loc(label)
            
        result = self.dataTable.iloc[index, colIndex]
        return result

    def SetMinMaxVisibleViewValues(self):
        """Iterates through dataTable. For each visible data, computes the min
        and max according to each view. Adds these min and max values
        to viewsTable as 'DataMin' and 'DataMax' columns

        """
        try:
            self.commonState.viewsTable['DataMin'] = 0.0
            self.commonState.viewsTable['DataMax'] = 0.0
        
            for viewIndex in range(self.commonState.viewsTable.shape[0]):
                dataMin = self.commonState.viewsTable.iloc[viewIndex, self.commonState.viewsTable.columns.get_loc('MaxMin')]
                dataMax = self.commonState.viewsTable.iloc[viewIndex, self.commonState.viewsTable.columns.get_loc('MinMax')]
                rFn = self.commonState.viewsTable.iloc[viewIndex, self.commonState.viewsTable.columns.get_loc('ReductionFn')]
                for dataIndex in range(self.dataTable.shape[0]):
                    if self.dataTable.iloc[dataIndex, self.dataTable.columns.get_loc('Visible')]:
                        dataView = rFn(self.dataTable.Data[dataIndex])
                        currMin = np.min(dataView)
                        currMax = np.max(dataView)

                        dataMin = min(dataMin, currMin)
                        dataMax = max(dataMax, currMax)

                self.commonState.viewsTable.iloc[viewIndex, self.commonState.viewsTable.columns.get_loc('DataMin')] = dataMin
                self.commonState.viewsTable.iloc[viewIndex, self.commonState.viewsTable.columns.get_loc('DataMax')] = dataMax

        except Exception as err:
            DisplayCore.HandleException(err)
