#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import telescopium

observatory = telescopium.Observatory()
observatory.getMainControl()

observatory.startTheSkyX()

observatory.setPathsForTonight()

observatory.startDcPowerSwitch()
observatory.setAllSwOn()

###############################################################################
# Start MainCamera
#
observatory.startMainCamera()

###############################################################################
# Start MainFilter
#
observatory.startMainFilter()

if True:
    frameType       = 'Light'
    tempSetPoint    = int(observatory.mainCamera.getTempSetPoint())

    exposure        = 0.01
    binning         = 1

    filterName      = 'OSC'

    reductionKind   = 'None'
    reductionGrp    = f'{tempSetPoint}C_{filterName}_{exposure}s_{binning}bin'
 
    autoSaveFile    = False
    asyncMode       = True

    for sequenceNdx in range(10):
        observatory.mainFilter.setFilterByName(filterName)
        observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
        while not observatory.mainCamera.isComplete():
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'{observatory.mainCamera.getExpStatus()}')
            observatory.sleep(1)    
        objName         = 'NoObject'
        observatory.mainCamera.saveImgToFile(observatory.filePathLights,frameType,tempSetPoint,objName,filterName,exposure,binning,sequenceNdx)



if False:
    for ndx in range(observatory.mainFilter.numbFilters):
        frameType       = 'Light'
        exposure        = 1
        binning         = 2
        reductionKind   = 'No'
        reductionGrp    = ''
        autoSaveFile    = False
        asyncMode       = False
        observatory.mainFilter.setFilterByNdx(ndx)
        observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
    
    for ndx in ['R','G','B','L','SII','OIII','Ha']:
        frameType       = 'Light'
        exposure        = 1
        binning         = 2
        reductionKind   = 'No'
        reductionGrp    = ''
        autoSaveFile    = False
        asyncMode       = False
        observatory.mainFilter.setFilterByName(ndx)
        observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)



