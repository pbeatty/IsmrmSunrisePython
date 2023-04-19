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
 
from .. import Common
from .DataModel import DataModel
from .ViewPanel import ViewPanel
from .ControlWidget import ControlWidget



class MainWindow(Common.MainWindow):
    def __init__(self,
                 complexImList,
                 interpolation='bicubic',
                 initLocation=None,
                 origin='lower',
                 titles=None,
                 axisLabels=None,
                 imageType=Common.ImageType.mag,
                 maxNumInRow=None,
                 colormap=None,
		 windowTitle=None):

        try:
            super(MainWindow, self).__init__()

            if windowTitle is None:
                self.windowTitle = 'Display'
            else:
                self.windowTitle = windowTitle
                # save calling parameters
            self.callingParams = {}
            self.callingParams['complexImList'] = complexImList
            self.callingParams['interpolation'] = interpolation
            self.callingParams['initLocation'] = initLocation
            self.callingParams['origin'] = origin
            self.callingParams['titles'] = titles
            self.callingParams['axisLabels'] = axisLabels
            self.callingParams['imageType'] = imageType
            self.callingParams['colormap'] = colormap
            self.callingParams['windowTitle'] = windowTitle
            self.callingParams['maxNumInRow'] = maxNumInRow
            

            if initLocation is None:
                initLocation = [int(complexImList[0].shape[0] * 0.5), int(complexImList[0].shape[1] * 0.5)]


            self.dataModel = DataModel(complexImList, titles)      
            self.controller = Common.Controller(self.dataModel)
            self.controller.signalClone.connect(self.Clone)
            controlWidget = ControlWidget(self.controller, self.dataModel)

            viewWidget = ViewPanel(self.controller, self.dataModel)


            self.Setup(controlWidget, viewWidget)


        except Exception as err:
            Common.HandleException(err)




    def Clone(self):
        try:
            viewer = MainWindow(**self.callingParams)
            viewer.Start()
        except Exception as err:
            Common.HandleException(err)
