#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import telescopium

observatory = telescopium.Observatory()
telescopiumMainControl=observatory.getTelescopiumMainControl()
telescopiumMainControl['debugCommLevel']        = True     # (False) True to log serial traffic
 
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

observatory.startTheSkyX(telescopiumMainControl['getNewInstance'],telescopiumMainControl['theSkyProc'],telescopiumMainControl['theSkyApp'])

###############################################################################
# Start MainCamera
#

observatory.startMainCamera(telescopiumMainControl)

###############################################################################
# Start MainFilter
#   Queries Number of filter slots
#   Gathers the names of the filters (R,G,B,etc)
#
observatory.startMainFilter(telescopiumMainControl)

for ndx in range(observatory.mainFilter.numbFilters):
    exposure        = 1
    binning         = 2
    imageReduction  = 2
    imageReduction  = 0
    autoSaveFile    = False
    asyncMode       = False
    observatory.mainFilter.setFilterByNdx(ndx)
    observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)

for ndx in ['R','G','B','L','SII','OIII','Ha']:
    exposure        = 1
    binning         = 2
    imageReduction  = 2
    imageReduction  = 0
    autoSaveFile    = False
    asyncMode       = False
    observatory.mainFilter.setFilterByName(ndx)
    observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)



