"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""
import matplotlib as mpl
mpl.use('Qt4Agg')
import matplotlib.pyplot as plt
plt.ion()
from PyQt4 import QtGui,QtCore
import Display._Core as _Core
import Display.Viewer3D._MainWindow3D 
import Display.Viewer2D._MainWindow2D 
import numpy as np

def _startViewer(viewer,block, windowTitle = None):
    #viewer.show() #put self.show() inside the init function of your main window class
    if block:                
        QtGui.qApp.exec_()
        return
    else:                
        viewerNum=_Core._storeViewer(viewer)
        viewer.setViewerNumber(viewerNum)
        
        if windowTitle is None:            
            viewer.setWindowTitle('Viewer '+str(viewerNum))
        else:
            viewer.setWindowTitle(windowTitle)
            
        return viewer
    
def imshow3d(data,interpolation='bicubic', block=False):
    viewer=Display.Viewer3D._MainWindow3D._MainWindow(data, interpolation=interpolation)
    if not block:       
        viewer.imagePanel3D.raw=np.copy(viewer.imagePanel3D.raw)
        #if the viewer is run as not blocking, then the underlying data
        #can change later on in the script and effect the results shown
        #in the viewer.  Therefore, we must make a copy.  If you have a
        #large data set and don't want to wait for the copy or can't afford
        #the memory, then you should run the viewer with block=True
    return _startViewer(viewer,block)
    
def imshow2d(data,interpolation='bicubic',origin='lower',windowTitle = None, titles=None,block=False, locationLabels=None, maxNumInRow=None, colormap=None):
    if type(data)==list or type(data)==tuple:
        concat = np.empty(data[0].shape+(len(data),),dtype='complex')
        for i in range(len(data)):
            concat[:,:,i]=data[i]
        data=concat
    viewer=Display.Viewer2D._MainWindow2D._MainWindow(data,interpolation=interpolation, origin=origin, titles=titles, locationLabels=locationLabels, maxNumInRow=maxNumInRow, colormap=colormap)
    return _startViewer(viewer,block, windowTitle)
       
def close(num=None):  
    _Core._checkViewerListExists()
    if type(num) is int:
        if num <= len(_Core._viewerList) and _Core._viewerList.has_key(num):
            del _Core._viewerList[num]
    if num is None:
        _Core._viewerList.clear()
        
def pause(pauseTime):    
    #pause time is in milliseconds
    loop = QtCore.QEventLoop()
    timer= QtCore.QTimer()
    #timer.setSingleShot(True)
    #timer.timeout.connect(loop.quit)
    #timer.start(pauseTime)    
    timer.singleShot(pauseTime,loop.quit)
    loop.exec_()
    
