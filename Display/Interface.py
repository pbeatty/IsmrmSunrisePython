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

__all__ = ["Plot", "PlotListInterface", "ShowImage2D", "ShowImage3D", "BlockOnOpenWindow"]

import numpy as np
from . import Common
from ._Plot import MainWindow as PlotWindow
from ._ShowImage2D import MainWindow as Image2DWindow
from ._ShowImage3D import MainWindow as Image3DWindow

def BlockOnOpenWindow():
    
    from qtpy import QtWidgets
    app = QtWidgets.QApplication.instance()

    if not app is None:
        app.exec_()


def ShowImage2D(data,
                interpolation='bicubic',
                origin='lower',
                windowTitle=None,
                titles=None,
                axisLabels=None,
                maxNumInRow=None,
                colormap=None):
    """ Interface for plotting 2D images and sets of 2D images

    """

    
    if type(data) == np.ndarray:
        if data.ndim == 2:
            data = [data]
        elif data.ndim == 3:
            tmp = np.dsplit(data, data.shape[2])
            data = list(map(lambda elem: np.reshape(elem, [elem.shape[0], elem.shape[1]]), tmp))
        
        
    if type(data) != list:
        raise RuntimeError('data must be a list: {}'.format(type(data)))

    viewer=Image2DWindow.MainWindow(data,
                                    interpolation=interpolation,
                                    origin=origin,
                                    titles=titles,
                                    axisLabels=axisLabels,
                                    maxNumInRow=maxNumInRow,
                                    colormap=colormap,
                                    windowTitle=windowTitle)

    viewer.Start()
    return viewer


def ShowImage3D(data,
                interpolation='bicubic',
                origin='lower',
                windowTitle=None,
                titles=None,
                axisLabels=None,
                colormap=None):
    """ Interface for plotting 3D images and sets of 3D images

    """
    if type(data) != list:
        raise RuntimeError('data must be a list: {}'.format(type(data)))
    viewer=Image3DWindow.MainWindow(data,
                                    interpolation=interpolation,
                                    origin=origin,
                                    titles=titles,
                                    axisLabels=axisLabels,
                                    colormap=colormap,
                                    windowTitle=windowTitle)

    viewer.Start()
    return viewer


# Interface for plotting 1D images and sets of 1D images
def Plot(data,windowTitle=None):
    viewer = PlotWindow.MainWindow(data, windowTitle)
    viewer = viewer.Start()
    return viewer


def PlotListInterface(complexDataList, sampleLocationsList, titleList=None, windowTitle=None):
    from ._Plot import DataFactories as DataFactories
    data = DataFactories.CreateDataFrameFromLists(complexDataList, sampleLocationsList, titleList)
    viewer = PlotWindow.MainWindow(data, windowTitle)
    viewer = viewer.Start()
    return viewer
    
