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
__all__ = ["ShowImageCommonDataState", "ShowImageDataModel"]
import numpy as np
import pandas as pd
import matplotlib.cm as colormaps
from IPython.display import display

from qtpy import QtCore
from . import DataModelBase
from . import DisplayCore

class ShowImageCommonDataState(DataModelBase.CommonDataState):
    ''' Stores values common across all data series


    '''

    def __init__(self, dimShape):
        try:
            super(ShowImageCommonDataState, self).__init__(dimShape)

            def AddToViewsTable(viewsTable):
                # Set Name as index, but also leave as data column
                # Add data columns
                viewsTable['Window'] = -1.0
                viewsTable['Level'] = 0.0
                viewsTable['EnableWindowLevelChange'] = True
                viewsTable['Colormap'] = colormaps.Greys_r

                viewsTable.at['Phase', 'Colormap'] = colormaps.hsv
                viewsTable.at['Phase', 'Window'] = 2.0 * np.pi
                viewsTable.at['Phase', 'EnableWindowLevelChange'] = False
                
                return viewsTable

            #
            # viewsTable is a data frame, where each row completely
            # describes the settings for each type of view of the
            # (complex) data.  I am trying to make it so that the
            # viewer code does not need domain knowledge of how
            # particulary types of views should be displayed. That
            # info should all be kept here, in the DataModel
            #
            self.viewsTable = AddToViewsTable(self.viewsTable)

        except Exception as err:
            DisplayCore.HandleException(err)





class ShowImageDataModel(DataModelBase.DataModel):
    def __init__(self, complexDataList, titles = None):
        """ Stores a set of N-D complex images of equal shape

        Parameters
        ----------

        complexDataList : list of N-D arrays
        """

        try:

            numImages = len(complexDataList)
            super(ShowImageDataModel, self).__init__(numImages, titles)


            self.dataTable['Data'] = complexDataList
            self.commonState = ShowImageCommonDataState(complexDataList[0].shape)
            self.SetMinMaxVisibleViewValues()

        except Exception as err:
            DisplayCore.HandleException(err)


                    
