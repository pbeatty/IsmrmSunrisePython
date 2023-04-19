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

__all__ = ["MainWindow", "HandleException", "MakeColors"]
import matplotlib as mpl
import os
import sys

try:
    __IPYTHON__
    # for ipython console, first run "%matplotlib qt"
    # or Tools, Preferences, IPython console set Backend to Qt
except NameError:
    pass
else:
    mpl.use('QtAgg')
import matplotlib.pyplot as plt
plt.ion()

from qtpy import QtWidgets, QtCore

import qdarkstyle

def MakeColors(numDataSeries):

    pjb_colors = ['#FF0000',
                  '#00FF00',
                  '#0000FF',
                  '#FFFF00',
                  '#00FFFF',
                  '#FF00FF',
                  '#FFFFFF',
                  '#FF8000',
                  '#FF0080',
                  '#80FF00',
                  '#00FF80',
                  '#0080FF',
                  '#8000FF',
                  '#FF8080',
                  '#80FF80',
                  '#8080FF',
                  '#AAAAAA',
                  '#AA00AA',
                  '#00AAAA',
                  '#AAAA00']
    
    graphColors = pjb_colors
    colors = [graphColors[ind % len(graphColors)] for ind in range(numDataSeries)]
    return colors

def HandleException(err):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("Exception [{}] in [{}:{}] {}".format(exc_type, fname, exc_tb.tb_lineno, err))


def storeViewer(viewer):    
    checkViewerListExists()
    global viewerList   
    viewerCount=0
    while(1):
        viewerCount+=1
        if viewerCount not in viewerList:
            viewerList[viewerCount]=viewer
            break
    return viewerCount
    
def checkViewerListExists():
    global viewerList
    try:
        viewerList
    except NameError:
        viewerList = {}  

def pause(pauseTime):
    #pause time is in milliseconds
    loop = QtCore.QEventLoop()
    timer= QtCore.QTimer()
    timer.singleShot(pauseTime,loop.quit)
    loop.exec_()


def PySideCheck():
    try:
        import PySide
        return True
    except ImportError:
        return False

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, controlWidget=None, viewWidget=None):
        self.viewerNumber=0
        
        try:
            # set self.app to QApplication; create one if it doesn't exist
            self.app = QtWidgets.QApplication.instance()
            if self.app is None:
                self.app = QtWidgets.QApplication( [" "] )
                #self.app.connect( self.app, QtCore.SIGNAL( "lastWindowClosed()" ),
                #                self.app, QtCore.SLOT( "quit()" ) )
        
            super(MainWindow,self).__init__()
            self.setStyleSheet(qdarkstyle.load_stylesheet())

            if not (controlWidget is None or viewWidget is None):
                self.Setup(controlWidget, viewWidget)                
        except Exception as err:
            HandleException(err)



    def Setup(self, controlWidget, viewWidget):
        try:    
            self.controls = controlWidget
            self.view = viewWidget
    
            self.SetupLayout()
        except Exception as err:
            HandleException(err)



    def Start(self):
        viewerNum=storeViewer(self)
        self.setViewerNumber(viewerNum)

        self.setWindowTitle("{} [{}]".format(self.windowTitle, viewerNum))
        
                                              
    def SetupLayout(self):
        try:
            splitter=QtWidgets.QSplitter()
            splitter.addWidget(self.controls)
            splitter.addWidget(self.view)
            
            self.setCentralWidget(splitter) #used when inheriting from QMainWindow
            
            
            self.show()
            self.setFocus()
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            
        except Exception as err:
            HandleException(err)

        
        
    def setViewerNumber(self,number):
        self.viewerNumber=number
        
    def closeEvent(self,event):   
        try:
            if self.viewerNumber:
                del  viewerList[self.viewerNumber]
        except Exception as err:
            HandleException(err)

    
    

