"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""
from PyQt4 import QtGui, QtCore

def _create_qApp():
    """
    Only one qApp can exist at a time, so check before creating one.
    """
    if QtGui.QApplication.startingUp():
        global qApp
        app = QtGui.QApplication.instance()
        if app is None:
            qApp = QtGui.QApplication( [" "] )
            QtCore.QObject.connect( qApp, QtCore.SIGNAL( "lastWindowClosed()" ),
                                qApp, QtCore.SLOT( "quit()" ) )
        else:
            qApp = app      

def _storeViewer(viewer):    
    _checkViewerListExists()
    global _viewerList   
    viewerCount=0
    while(1):
        viewerCount+=1
        if not _viewerList.has_key(viewerCount):
            _viewerList[viewerCount]=viewer
            break
    return viewerCount
    
def _checkViewerListExists():
    global _viewerList
    try:
        _viewerList
    except NameError:
        _viewerList = {}  