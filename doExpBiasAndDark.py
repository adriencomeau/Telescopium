# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 12:51:17 2022

@author: Adrien
"""

import telescopium 

#############################################################################
# Set Observatory Object
#
observatory = telescopium.Observatory()
observatory.currentState = 'Initializing';
observatory.getMainControl()
observatory.setDebugLevel(True)

#############################################################################
#
#
observatory.setObsLocation()
observatory.calculateNight()

#############################################################################
# Start Webcam and TheSkyX
#
observatory.startCheese()
observatory.startTheSkyX()

#############################################################################
# Start items not needed to be powered up and Cycle Power
#
observatory.startWxMonitor()
observatory.startDcPowerSwitch()
observatory.setAllSwOff()
observatory.setAllSwOn()

#############################################################################
# Set folder for saving
#
observatory.setPathsForTonight()


#############################################################################
# Start the items that were powered up
#
observatory.startDomeController()
observatory.startParkDetector()
#observatory.startMount()
observatory.startMainCamera()
observatory.startMainFilter()
observatory.startFocuser()
observatory.startGuider()

observatory.setCameraTempTarget()

if observatory.mainControl['leaveLightOn']:
    observatory.dcPowerSwitch.setSwOff(6)

for tempSetPointLocal in observatory.mainControl['a_list']:
    if tempSetPointLocal >= observatory.tempSetPointForTonight:
        observatory.mainCamera.setTempSetPoint(True,tempSetPointLocal,True,observatory.mainControl['waitTimeMin'])

        for sequenceNdx in range(observatory.mainControl['numbBiasExp']):
            frameType       = 'Bias'
            tempSetPoint    = int(observatory.mainCamera.getTempSetPoint())
            objName         = 'noObj'
            filterName      = 'OSC'
            exposure        = 0
            binning         = 1
            reductionKind   = 'No'
            reductionGrp    = ''
            sequence        = sequenceNdx
            autoSaveFile    = False
            asyncMode       = False
            observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
            observatory.mainCamera.saveImgToFile(observatory.filePathBias,frameType,tempSetPoint,objName,filterName,exposure,binning,sequence)
        
        for exposureVal in observatory.mainControl['darkExpRange']:
            for sequenceNdx in range(observatory.mainControl['numbDarkExp']):
                frameType       = 'Dark'
                temp            = int(observatory.mainCamera.getTempSetPoint())
                objName         = 'noObj'
                filterName      = 'OSC'
                exposure        = exposureVal
                binning         = 1
                reductionKind   = 'No'
                reductionGrp    = ''
                sequence        = sequenceNdx
                autoSaveFile    = False 
                asyncMode       = False
                observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
                observatory.mainCamera.saveImgToFile(observatory.filePathBias,frameType,temp,objName,filterName,exposure,binning,sequence)

observatory.setAllSwOff()       
