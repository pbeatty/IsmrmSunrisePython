"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""

from PyQt4 import QtCore

signalImageTypeChange = QtCore.pyqtSignal(int, name='imageTypeChanged')
signalImageCmapChange = QtCore.pyqtSignal(int, name='imageCmapChanged')

signalXLocationChange = QtCore.pyqtSignal(int, name='xLocationChanged')
signalYLocationChange = QtCore.pyqtSignal(int, name='yLocationChanged')
signalZLocationChange = QtCore.pyqtSignal(int, name='zLocationChanged')
signalLocationChange = QtCore.pyqtSignal(int, int)

signalWindowLevelChange = QtCore.pyqtSignal(float, float)    
signalWindowLevelReset = QtCore.pyqtSignal(name='windowLevelReset')

signalSaveToFile = QtCore.pyqtSignal(str)