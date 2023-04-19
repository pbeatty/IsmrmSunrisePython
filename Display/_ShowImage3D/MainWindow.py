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

from datetime import datetime

class MainWindow(Common.MainWindow):
    def __init__(self,
                 complexImList,
                 interpolation='bicubic',
                 initLocation=None,
                 origin='lower',
                 titles=None,
                 axisLabels=None,
                 imageType=Common.ImageType.mag,
                 colormap=None,
                 windowTitle=None):

        try:
            #print("{}: @Start MainWindow".format(datetime.now().strftime('%X.%f')))
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
            if initLocation is None:
                initLocation = [int(complexImList[0].shape[0] * 0.5), int(complexImList[0].shape[1] * 0.5), int(complexImList[0].shape[2] * 0.5)]


            self.dataModel = DataModel(complexImList, titles)
            #print("{}: DataModel created".format(datetime.now().strftime('%X.%f')))
            self.controller = Common.Controller(self.dataModel)
            self.controller.signalClone.connect(self.Clone)
            #print("{}: Controller created".format(datetime.now().strftime('%X.%f')))

            controlWidget = ControlWidget(self.controller, self.dataModel)
            #print("{}: ControlWidget created".format(datetime.now().strftime('%X.%f')))
            viewWidget = ViewPanel(self.controller, self.dataModel)
            #print("{}: ViewPanel created".format(datetime.now().strftime('%X.%f')))
            self.Setup(controlWidget, viewWidget)
            #print("{}: Setup done".format(datetime.now().strftime('%X.%f')))


        except Exception as err:
            Common.HandleException(err)




    def Clone(self):
        try:
            viewer = MainWindow(**self.callingParams)
            viewer.Start()
        except Exception as err:
            Common.HandleException(err)
