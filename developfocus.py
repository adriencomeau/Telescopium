# # -*- coding: utf-8 -*-
# """
# Spyder Editor

# This is a temporary script file.
# """

import telescopium

observatory = telescopium.Observatory()
observatory.getMainControl()


#############################################################################
#
#
observatory.setObsLocation()
observatory.calculateNight()

#############################################################################
# Start Webcam and TheSkyX
#
observatory.startTheSkyX()

#############################################################################
# Set folder for saving
#
observatory.setPathsForTonight()

observatory.startDcPowerSwitch()
observatory.setAllSwOn()

#############################################################################
# Start the items that were powered up
#
observatory.startFocuser()

observatory.mainFocuser.loadFocuserDataSet(observatory.mainControl['telescopiumLibraryPath'],observatory.mainControl['focuserDataSet'])
observatory.mainFocuser.setTempCurve()
observatory.mainFocuser.moveToTempCurve()
#observatory.mainFocuser.focus2()


