#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import telescopium

observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.setDebugLevel(True)

observatory.startTheSkyX()


###############################################################################
# Start MainCamera
#
observatory.startGuider()
observatory.guider.setDebugCommLevel(False)
observatory.guider.setExposure(4)
observatory.guider.takeImage()

if observatory.guider.findStar():
    if observatory.guider.start():
        pass
    else:
        print('Guiding dod not start well enough')
else:
    print('No Guide star')