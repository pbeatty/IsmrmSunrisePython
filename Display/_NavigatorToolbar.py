"""
Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
    
Alan Kuurstra    
Philip J. Beatty (philip.beatty@gmail.com)
"""
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg

class NavigationToolbar(NavigationToolbar2QTAgg):    
    def __init__(self,canvas,parent):
        super(NavigationToolbar,self).__init__(canvas,parent)
        self.clear()
        a = self.addAction(self._icon('home.png'), 'Home', self.home)
        a.setToolTip('Reset original view')   
        a = self.addAction(self._icon('zoom_to_rect.png'), 'Zoom', self.zoom)
        a.setToolTip('Zoom to rectangle')
        a = self.addAction(self._icon('move.png'), 'Pan', self.pan)
        a.setToolTip('Pan axes with left mouse, zoom with right') 
        a = self.addAction(self._icon('zoom_to_rect.png'), 'Select', self.selectROI)
        self.addSeparator()
        a = self.addAction(self._icon('filesave.png'), 'Save',
                self.save_figure)
        a.setToolTip('Save the figure')

    def selectROI(self, *args):
        'activate selectROI'
        if self._active == "SELECTROI":
            self._active = None
        else:
            self._active = "SELECTROI"
        
        if self._idPress is not None:
            self._idPress=self.canvas.mpl_disconnect(self._idPress)
            self.mode = ''

        if self._idRelease is not None:
            self._idRelease=self.canvas.mpl_disconnect(self._idRelease)
            self.mode = ''
            
        if self._active:
            self._idPress=self.canvas.mpl_connect('button_press_event', self.press_selectROI)
            self._idRelease=self.canvas.mpl_connect('button_release_event', self.release_selectROI)
            self.mode = 'select rect'
            self.canvas.widgetlock(self)            
        else:
            self.canvas.widgetlock.release(self)

        for a in self.canvas.figure.get_axes():
            a.set_navigate_mode(self._active)

        self.set_message(self.mode)
        
    def press_selectROI(self,event):
        
        if event.button == 1:
            self._button_pressed=1
        elif  event.button == 3:
            self._button_pressed=3
        else:
            self._button_pressed=None
            return
        
        x, y = event.x, event.y

        self._xypress=[]
        for i, a in enumerate(self.canvas.figure.get_axes()):
            if (x is not None and y is not None and a.in_axes(event) and
                a.get_navigate()) :
                self._xypress.append(( x, y, a, i, a.viewLim.frozen(),
                                       a.transData.frozen() ))

        id1 = self.canvas.mpl_connect('motion_notify_event', self.drag_selectROI) 
        self._ids_selectROI = id1,        
        self.press(event)   
        
        
    def drag_selectROI(self, event):
        'the drag callback in zoom mode'        
        if self._xypress and self._button_pressed==1:
            x, y = event.x, event.y
            lastx, lasty, a, ind, lim, trans = self._xypress[0]

            # adjust x, last, y, last
            x1, y1, x2, y2 = a.bbox.extents
            x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
            y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2)
            
            #need better rectangle 
            self.draw_rubberband(event, x, y, lastx, lasty)
    def release_selectROI(self,event):
        for _id in self._ids_selectROI:
            self.canvas.mpl_disconnect(_id)
        
        self._ids_selectROI=[]
        
        if not self._xypress: return
        if self._button_pressed==1:       
            #need the box in data coordinates
            x, y = event.x, event.y
            lastx, lasty, a, ind, lim, trans = self._xypress[0]
            x1, y1, x2, y2 = a.bbox.extents
            x, lastx = max(min(x, lastx), x1), min(max(x, lastx), x2)
            y, lasty = max(min(y, lasty), y1), min(max(y, lasty), y2) 
            print x,y,lastx,lasty
        
        self.draw()
        self._xypress = None
        self._button_pressed = None        
        self.release(event)
  
