"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Alan Kuurstra
Philip J. Beatty (philip.beatty@gmail.com)

Modified 2017, Philip J. Beatty
"""
__all__=["ImagePanel"]

import numpy as np
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
    

from .. import Common


class ImagePanel(FigureCanvas):
    signalChangeLocation = QtCore.Signal(int, int)
    signalChangeWindowLevel = QtCore.Signal(float, float)
    signalScroll = QtCore.Signal(int)
    def __init__(self,
                 dim0Description,
                 dim1Description,
                 currView,
                 imageData):
        ''' ImagePanel constructor

        Parameters
        ----------

        dim0Description : pandas Series containing Name, Shape, CurrLocation, Color 

        dim1Description : pandas Series containing Name, Shape, CurrLocation, Color 

        currView : pandas Series containing 
                   Window, Level, EnableWindowLevelChange, Colormap, Interpolation, Origin
        imageData : numpy 2D array of floats. The data to display

        imageDescription : pandas Series containing Title, Color, Index

        '''

        try:
            #
            # Qt related initialization
            #
            self.fig = mpl.figure.Figure()
            FigureCanvas.__init__(self, self.fig)
            FigureCanvas.setSizePolicy(self,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            FigureCanvas.updateGeometry(self)
            
            #
            # Event related initialization
            #
            self.mpl_connect('motion_notify_event', self.MoveEvent)
            self.mpl_connect('button_press_event', self.PressEvent)
            self.mpl_connect('button_release_event', self.ReleaseEvent)
            self.mpl_connect('scroll_event', self.ScrollEvent)
            self.leftMousePress = False
            self.middleMousePress = False
            self.rightMousePress = False

            #
            # Internal data model initialization
            #
            # Check that imageData shape matches dimXDescription Shape
            if dim0Description.get('Shape',0) != imageData.shape[0]:
                raise RuntimeError('Dimension 0 shape mismatch: imageData [{}], dim0Description [{}]'.format(imageData.shape[0], dim0Description.get('Shape', 0)))
            if dim1Description.get('Shape',0) != imageData.shape[1]:
                raise RuntimeError('Dimension 1 shape mismatch: imageData [{}], dim0Description [{}]'.format(imageData.shape[1], dim1Description.get('Shape', 0)))
  
            self.imageData = imageData  
            

            # Set location as CurrLocation
            # if CurrLocation does not exist, set to half the shape
            # Then, restrict location to be an integer in the range [0, Shape)
            self.location = np.array((dim0Description.get('CurrLocation', dim0Description.get('Shape',0)*0.5),
                             dim1Description.get('CurrLocation', dim1Description.get('Shape',0)*0.5)))
            self.location = np.minimum(np.maximum(self.location, [0,0]), np.subtract(self.imageData.shape, 1)).astype(int)
            
            #image
            #self.fig.subplots_adjust(bottom=0.1,left=0.1)
            if(oldMPL):
                self.axes=self.fig.add_subplot(111, axisbg=Common.darkBackgroundColor)
            else:
                self.axes=self.fig.add_subplot(111, facecolor=Common.darkBackgroundColor)

            #self.fig.tight_layout()
            self.fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0)
            self.fig.patch.set_color(Common.darkBackgroundColor)  
            
            self.axes.xaxis.get_label().set_color(Common.lightTextColor)
            for label in self.axes.xaxis.get_ticklabels():
                label.set_color(Common.lightTextColor)
            
            self.axes.yaxis.get_label().set_color(Common.lightTextColor)
            for label in self.axes.yaxis.get_ticklabels():
                label.set_color(Common.lightTextColor)
            
            
            # create the border on the image
            for spine in self.axes.spines.values():
                #spine.set_position(('outward', 5))
                spine.set_edgecolor('#000000')
                spine.set_linewidth(0)

            #self.axes.hold(False) # hold is deprecated an removing it doesn't seem to do anything...
            self.img = self.axes.imshow(np.zeros(self.imageData.shape).T, 
                                        interpolation=currView.get('Interpolation', 'bicubic'), 
                                        origin=currView.get('Origin', 'lower'))
            self.SetImageData(imageData)

            #self.axes.set_title(imageDescription.get('Title', ""), color=Common.lightTextColor)

            self.axes.xaxis.set_ticks([])
            self.axes.yaxis.set_ticks([])

            

            #cursor lines
            self.hline=self.axes.axhline(y=self.location[1], linewidth=1, linestyle='dashed', dashes=(2,2), color=dim0Description.get('Color', '#000000'))
            self.vline=self.axes.axvline(x=self.location[0], linewidth=1, linestyle = 'dashed', dashes=(2, 2), color=dim1Description.get('Color', '#000000'))

            self.SetView(currView)
            
            #zoom functionality
            self.toolbar=NavigationToolbar2QT(self,self)
            self.toolbar.hide()
            self.toolbar.zoom()
            if self.axes.get_navigate_mode() == 'ZOOM':
                self.toolbar.zoom()
            
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

    
    def SaveImage(self, fname):
        try:
            img=self.img.get_array()
            cmap=cmap=self.img.get_cmap()
            origin=self.img.origin
            vmin,vmax=self.img.get_clim()
    
            mpl.pyplot.imsave(fname=fname+'.png', arr=img, cmap=cmap, origin=origin, vmin=vmin, vmax=vmax, format="png")
        except Exception as err:
            Common.HandleException(err)

               
    #==================================================================
    #slots to deal with mpl mouse events
    #==================================================================
    def PressEvent(self,event): 
        try:
            #with matplotlib event, button 1 is left, 2 is middle, 3 is right        
            if event.button==1:
                self.leftMousePress=True   
               
            # for middle mouse click we want to show the image in a new window
            elif event.button==2:            
                self.middleMousePress=True
                img=self.img.get_array()
                cmap=cmap=self.img.get_cmap()
                origin=self.img.origin
                vmin,vmax=self.img.get_clim()
                mpl.pyplot.figure()
                mpl.pyplot.imshow(img,cmap=cmap,origin=origin, vmin=vmin,vmax=vmax)                      
                
            elif event.button==3:            
                self.rightMousePress=True
                    
            self.origIntensityWindow=self.intensityWindow            
            self.origIntensityLevel=self.intensityLevel
            self.origPointerLocation = [event.x, event.y]
            self.MoveEvent(event) 
        except Exception as err:
            Common.HandleException(err)


    def ReleaseEvent(self,event): 
        if event.button==1:
            self.leftMousePress=False        
        elif event.button==2:            
            self.middleMousePress=False
        elif event.button==3:            
            self.rightMousePress=False       

    def ScrollEvent(self, event):
        if event.button=="down":
            self.signalScroll.emit(1)
        else:
            self.signalScroll.emit(-1)
        

        
    def MoveEvent(self,event):
        try:        
            if (self.rightMousePress and self.enableWindowLevel ):
                
                levelScale = 0.001
                windowScale = 0.001
                
                dLevel = levelScale * float(self.origPointerLocation[1] - event.y) * self.dataRange
                dWindow = windowScale * float(event.x - self.origPointerLocation[0]) * self.dataRange
    
                newIntensityLevel = self.origIntensityLevel + dLevel
                newIntensityWindow = self.origIntensityWindow + dWindow
                self.signalChangeWindowLevel.emit(newIntensityWindow,newIntensityLevel)
                
            enableInvestigate = self.axes.get_navigate_mode() is None  
            if (self.leftMousePress and enableInvestigate):
                imShape = self.imageData.shape
                
                
                locationDataCoord = self.axes.transData.inverted().transform([event.x, event.y])            
                clippedLocation = np.minimum(np.maximum(locationDataCoord+0.5, [0,0]), np.subtract(imShape,1)).astype(int)

                self.signalChangeLocation.emit(clippedLocation[0], clippedLocation[1])
        except Exception as err:
            Common.HandleException(err)
                
    
    #==================================================================
    #functions that set internal data
    #==================================================================
    def SetImageData(self, newImage):
        ''' Sets new image data, does not update display
        
        '''
        try:
            self.imageData = newImage
            self.minVal = np.min(self.imageData)
            self.maxVal = np.max(self.imageData)
            self.dataRange = self.maxVal - self.minVal
            self.img.set_data(self.imageData.T)
        except Exception as err:
            Common.HandleException(err)
        
        
        
    # sets the internal location
    def SetLocation(self, newLocation):
        '''

        '''
        try:

            if (int(self.location[0]) != newLocation[0]) or (int(self.location[1]) != newLocation[1]):
                self.location = newLocation
                self.hline.set_ydata([self.location[1]+0.5,self.location[1]+0.5])
                self.vline.set_xdata([self.location[0]+0.5,self.location[0]+0.5])
        except Exception as err:
            Common.HandleException(err)

       

    def SetWindowLevel(self, newIntensityWindow,newIntensityLevel):
        ''' Set Window/Level
        
        '''
        try:

            if newIntensityWindow >= 0:
                self.intensityLevel = newIntensityLevel
                self.intensityWindow = newIntensityWindow        
                vmin=self.intensityLevel-(self.intensityWindow*0.5)
                vmax=self.intensityLevel+(self.intensityWindow*0.5)
                self.img.set_clim(vmin, vmax)
            else:
                self.SetWindowLevelToDefault()
                
        except Exception as err:
            Common.HandleException(err)


            
    def SetWindowLevelToDefault(self):
        ''' Sets default window/level
        
        '''
        try:
            self.intensityLevel = 0.5 * (self.minVal + self.maxVal)
            self.intensityWindow = self.maxVal-self.minVal
            self.img.set_clim(self.minVal, self.maxVal)
            
        except Exception as err:
            Common.HandleException(err)



                
    #==================================================================            
    #functions that update objects visualizing internal data
    #==================================================================

    def SetView(self, currView):
        try:
            self.img.set_cmap(currView.get('Colormap', mpl.cm.Greys_r))
            self.img.set_interpolation(currView.get('Interpolation', 'bicubic'))
            # have not yet found a fn to reset origin
            self.enableWindowLevel = currView.get('EnableWindowLevelChange', True)
            self.SetWindowLevel(currView.get('Window', -1.0), currView.get('Level', 0.0))

        except Exception as err:
            Common.HandleException(err)

                                 
    
    def UpdateImageAndLines(self):
        ''' This function allows the image to be updated fast
        
        '''
        try:            
            #if self.fig._cachedRenderer is not None:  
            self.axes.draw_artist(self.axes.patch)
            self.axes.draw_artist(self.img)
            for spine in self.axes.spines.values():
                self.axes.draw_artist(spine)

            self.axes.draw_artist(self.hline)
            self.axes.draw_artist(self.vline) 
                
            self.update()
        except Exception as err:
            Common.HandleException(err)
            
            
     
    
    #==================================================================        
    #functions related to Qt
    #==================================================================
    def sizeHint(self):
        return QtCore.QSize(self.imageData.shape[0], self.imageData.shape[1])             
