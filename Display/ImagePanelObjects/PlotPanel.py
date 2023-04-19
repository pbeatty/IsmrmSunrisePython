"""

Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)


Modified 2017, Philip J. Beatty
"""
__all__ = ["PlotPanel"]
from .. import Common
import matplotlib as mpl
from packaging.version import parse as parse_version
oldMPL = parse_version(mpl.__version__) < parse_version('2')

from qtpy import QtCore, QtWidgets, PYQT5

if PYQT5:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
else:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4 import NavigationToolbar2QT


import numpy as np


import sys

class PlotPanel(FigureCanvas):
    """ Panel that displays line plots

    """
    signalHoverOnLine = QtCore.Signal(int, int) 
    def __init__(self, 
                 dataFn,
                 locationFn,
                 markerFn,
                 dimsTable,
                 numLines,
                 colorFn,
                 visibleFn,
                 yLimits,
                 title=None):

        ''' Constructor

        Parameters
        ----------

        dataFn : lambda
            Given index of line, returns the y values for this line

        locationFn : lambda
            Given index of line, returns sample locations

        markerFn : lambda
            Given index of line, returns the sample index where the marker should be set
        
        dimsTable : pandas series for this dim from dimsTable, includes Color and Name
                
        visibleFn : lambda
            Given index of line, returns True if the line should be displayed

        '''
        try:
            self.visibleFn = visibleFn
            #
            # Qt related initialization
            #        
            self.fig=mpl.figure.Figure() 
            FigureCanvas.__init__(self,self.fig)
            
            self.fig.patch.set_color(Common.darkBackgroundColor)  

            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)        
            self.setMinimumSize(200,200)
            if(oldMPL):
                self.axes=self.fig.add_subplot(111, axisbg=Common.darkBackgroundColor)
            else:
                self.axes=self.fig.add_subplot(111, facecolor=Common.darkBackgroundColor)

            self.SyncYLimits(yLimits)
            # Set labels and tick lines to Common.lightTextColor
            self.axes.xaxis.get_label().set_color(Common.lightTextColor)
            for label in self.axes.xaxis.get_ticklabels():
                label.set_color(Common.lightTextColor)

            self.axes.yaxis.get_label().set_color(Common.lightTextColor)
            for label in self.axes.yaxis.get_ticklabels():
                label.set_color(Common.lightTextColor)
                
            for tick in self.axes.xaxis.get_ticklines():
                tick.set_color(Common.lightTextColor)

            for tick in self.axes.yaxis.get_ticklines():
                tick.set_color(Common.lightTextColor)

            # Connect mpl events
            self.mpl_connect('motion_notify_event', self.OnPlotHover)
            self.mpl_connect('resize_event', self.OnPlotResize)

            #
            # create lines
            #
            self.numChannels = numLines#dataDescription.shape[0]
            self.lines = []
            minLoc = min(locationFn(0))
            maxLoc = max(locationFn(0))
            for line in range(self.numChannels):
                locs = locationFn(line)
                minLoc = min(minLoc, min(locs))
                maxLoc = max(maxLoc, max(locs))
                self.lines.append(self.axes.plot(locs, locs, colorFn(line)))
            self.axes.set_xlim(minLoc, maxLoc) 
            self.fig.tight_layout()
            self.draw()
            
            #
            # create markers
            #
            self.markers = []
            for line in range(self.numChannels):
                x = locationFn(line)[0]
                y = dataFn(line)[0]
                self.markers.append(self.axes.plot(x, y, colorFn(line), marker='o'))


            self.SyncData(dataFn)                          
            self.SyncMarkers(markerFn)    
    
            #
            # Initialize objects visualizing the internal data model
            #
            self.axes.title.set_color(Common.lightTextColor)
            if title is not None:
                self.axes.set_title(title) 
            self.axes.set_xlabel(dimsTable.get('Name', "")) 
                
            #zoom functionality
            self.toolbar=NavigationToolbar2QT(self,self)
            self.toolbar.hide()
            self.toolbar.zoom()
            if self.axes.get_navigate_mode() == 'ZOOM':
                self.toolbar.zoom()
    
            self.fig.tight_layout()        
            FigureCanvas.updateGeometry(self)

            borderColor = dimsTable.get('Color', Common.lightTextColor)
            for spine in self.axes.spines.values():
                spine.set_edgecolor(borderColor)
                spine.set_linewidth(1)

        except Exception as err:
            Common.HandleException(err)


    def sizeHint(self):
        return QtCore.QSize(400,400)
    def OnPlotResize(self, event):
        self.fig.tight_layout()
        self.draw()
        #self.Refresh()
        
    def OnPlotHover(self, event):
        '''
        If in Inspect mode (i.e. navigate_mode is None), 
        then see if hover intersects a visible line.
        If so, emit a 'signalHoverOnLine' signal
        '''
        try:
            if self.axes.get_navigate_mode() is None:
                for lineIndex in range(self.numChannels):
                    currMarker = self.markers[lineIndex][0]
                    if currMarker.get_visible():
                        currLine = self.lines[lineIndex][0]
                        hit, props = currLine.contains(event)
                        if hit:
                            sampleIndex = props['ind'][0]       
                            self.signalHoverOnLine.emit(lineIndex, sampleIndex)

        except Exception as err:
            Common.HandleException(err)
   

    def Reset(self):
        ''' Reset Axis, undoing Pan and Zoom actions
        '''
        self.toolbar.home()
        


    def SyncYLimits(self, yLimits=None):
        if not (yLimits is None):
            self.axes.set_ylim(yLimits)
            self.draw()
        else:
            raise RuntimeError('Need to grab max/min from curr data')
        
    def Refresh(self):
        ''' Redraw screen
        '''
        try:
            #self.fig.tight_layout()
            #self.draw()
            self.axes.draw_artist(self.axes.patch)
            for line in range(self.numChannels):
                self.axes.draw_artist(self.lines[line][0])
                self.axes.draw_artist(self.markers[line][0])

            for spine in self.axes.spines.values():
                self.axes.draw_artist(spine)
            
            self.update()
        except Exception as err:
            Common.HandleException(err)


    def ChangeNavMode(self, mode):
        ''' Change between Inspect, Zoom and Pan modes 
        
        Parameters
        ----------
        mode : 'ZOOM', 'PAN' or None
            None = inspect mode
        '''
        try:
            # It looks like the only way to set zoom and pan is through the toolbar, which only allows access through toggle calls
            # this is a hack to enable us to select type without toggle.
            if mode == 'INSPECT':
                mode = None
            
            currMode = self.axes.get_navigate_mode()
            if mode != currMode:
                if mode is None:
                    if currMode == 'ZOOM':
                        self.toolbar.zoom()
                    elif currMode == 'PAN':
                        self.toolbar.pan()
                elif mode == 'ZOOM':
                    self.toolbar.zoom()
                elif mode == 'PAN':
                    self.toolbar.pan()
        except Exception as err:
            Common.HandleException(err)
       
        
       
    def SyncMarkers(self, markerFn):
        ''' Synchronize markers with a model
       
        Note: marker location is set based on current data, so SyncData before SyncMarkers       
       
        Parameters
        ---------- 
        markerFn : lambda
            Given index of line, returns the sample index where the marker should be set
        '''
        try:
            for lineIndex in range(self.numChannels):
                currMarker = self.markers[lineIndex][0]
                sampleIndex = int(markerFn(lineIndex))
                currLine = self.lines[lineIndex][0]
                xloc = currLine.get_xdata()[sampleIndex]
                yloc = currLine.get_ydata()[sampleIndex]
                currMarker.set_data(xloc, yloc)
            self.Refresh()
        except Exception as err:
            Common.HandleException(err)
 

    def SyncVisible(self):
        ''' Synchronize which lines are visible with a model
        
        Parameters
        ----------
        '''
        try:
            for line in range(self.numChannels):
                isVisible = self.visibleFn(line)
                self.lines[line][0].set(visible=isVisible)
                self.markers[line][0].set(visible=isVisible)
            self.Refresh()
        except Exception as err:
            Common.HandleException(err)
            
            
    def SyncData(self, dataFn):
        ''' Synchronize data with a model
        
        Updates y limits based on data.        
        
        Parameters
        ----------
        dataFn : lambda
            Given index of line, returns the y values for this line
            
            
        '''
        try:

            for line in range(self.numChannels):
                ydata = dataFn(line)
                self.lines[line][0].set_ydata(ydata)
            
            self.Refresh()
       
        except Exception as err:
            Common.HandleException(err)
        
