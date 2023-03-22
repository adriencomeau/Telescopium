#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import telescopium

observatory = telescopium.Observatory()
telescopiumMainControl=observatory.getTelescopiumMainControl()
#telescopiumMainControl['debugCommLevel']        = True     # (False) True to log serial traffic
 
observatory.minimumSafeToHomeAngle      = telescopiumMainControl['minimumSafeToHomeAngle']
observatory.usableHorizon               = telescopiumMainControl['usableHorizon']
observatory.wxMonitorTempThreshold      = telescopiumMainControl['wxMonitorTempThreshold']
observatory.normalScheduling            = telescopiumMainControl['normalScheduling']
observatory.manualObservation           = telescopiumMainControl['manualObservation']
observatory.telescopiumLibraryPath      = telescopiumMainControl['telescopiumLibraryPath']
observatory.flatSpotAltitude            = telescopiumMainControl['flatSpotAltitude']
observatory.homeLocAlt                  = telescopiumMainControl['homeLocAlt']
observatory.homeLocAz                   = telescopiumMainControl['homeLocAz']
observatory.sunDownDegrees              = telescopiumMainControl['sunDownDegrees']
observatory.moonDownDegrees             = telescopiumMainControl['moonDownDegrees']

observatory.setDebugLevel(True)
observatory.setObsLocation(telescopiumMainControl['lat'],telescopiumMainControl['lon'],0)
observatory.calculateNight()
   
observatory.startDcPowerSwitch(telescopiumMainControl)
observatory.setAllSwOff(0)
observatory.setAllSwOn(telescopiumMainControl['leaveLightOn'],0)



