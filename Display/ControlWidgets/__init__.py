"""
A collection of classes that are widget building blocks for display control panels

Code made available for the ISMRM 2015 Sunrise Educational Course

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.

Alan Kuurstra
Philip J. Beatty (philip.beatty@gmail.com)

2017, modified by Chad Harris
2017, modified by Philip Beatty
"""

try:
    from .NumColumns import *
    from .WindowLevelBox import *
    from .LocationBox import *
    from .ScrollableContainerWidget import *
    from .LineBox import *
    from .ViewBox import *
    from .BasicValueBox import *
    from .CloneButton import *
    from .NavModeBox import *
    from .DatasetLegendWidget import *
    
except Exception as err:
    print("Exception in ControlWidgets/__init__ : {}".format(err))
