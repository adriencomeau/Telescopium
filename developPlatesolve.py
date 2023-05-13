# # -*- coding: utf-8 -*-
# """
# Spyder Editor

# This is a temporary script file.
# """

import telescopium 

observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.mainControl['verboseLevel']          = 10           # json active while running
observatory.mainControl['debugCommLevel']        = True       # json active while running
observatory.debugCommLevel = observatory.mainControl['debugCommLevel']

observatory.startTheSkyX()
observatory.startMainCamera()

#
# Pointing 2x2
#
if True:
    observatory.mainCamera.lastSaveFilePath="/home/acomeau/Library/Telescopium/20230510"
    observatory.mainCamera.lastFileName="Light -10C M101PointingExp OSC 10s 2bin #001 20230511-013840.fit"
    
    for ndx in range(20):    
        returnInfo=observatory.plateSolve(0.78)
        if not returnInfo['retCode']:
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve failed')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",returnInfo['errorCode'])
        else:
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve succeeded')
        returnInfo=observatory.plateSolve2(0.78)
        if not returnInfo['retCode']:
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve failed')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",returnInfo['errorCode'])
        else:
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve succeeded')

#
# Pointing 1x1
#
if True:
    observatory.mainCamera.lastSaveFilePath="/home/acomeau/Library/Telescopium/20230510"
    observatory.mainCamera.lastFileName="Light -10C M101 OSC 300s 1bin #020 20230511-014430.fit"
    
    for ndx in range(20):    
        returnInfo=observatory.plateSolve(0.39)
        if not returnInfo['retCode']:
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve failed')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",returnInfo['errorCode'])
        else:
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve succeeded')
