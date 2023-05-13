#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import telescopium
import math
import json
from astropy.time import Time

#############################################################################
# Set Observatory Object
#
observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.setPathsForTonight()

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

#############################################################################
# Start the items that were powered up
#
observatory.startDomeController()
observatory.startParkDetector()
observatory.startMainCamera()
observatory.startMainFilter()
observatory.startFocuser()
observatory.startGuider()
observatory.startMount()


observatory.mainFocuser.loadFocuserDataSet(observatory.mainControl['telescopiumLibraryPath'],observatory.mainControl['telescopiumFocuserDataSet'])
observatory.mainFocuser.mainFocuserDataSet.loc[len(observatory.mainFocuser.mainFocuserDataSet)] = {'DateTime':Time.now(), 'Temperature':observatory.mainFocuser.getTemp(), 'Step':observatory.mainFocuser.getPosition()}
observatory.mainFocuser.saveFocuserDataSet(observatory.mainControl['telescopiumLibraryPath'],observatory.mainControl['telescopiumFocuserDataSet'])


observatory.telescopeMount.loadPointingDataSet(observatory.mainControl['telescopiumLibraryPath'],observatory.mainControl['telescopiumPointingDataSet'])
observatory.telescopeMount.pointingDataSet.loc[len(observatory.telescopeMount.pointingDataSet)] = {'DateTime':Time.now(), 'deltaRaMin':10, 'deltaDecMin':11}
observatory.telescopeMount.savePointingDataSet(observatory.mainControl['telescopiumLibraryPath'],observatory.mainControl['telescopiumPointingDataSet'])

x=1/0

#############################################################################
# Select target CCD temperature
#
observatory.setCameraTempTarget()
    
#############################################################################
# If it is clear open the roof
#
if observatory.wxMonitor.isClear():
    observatory.domeController.openRoof()

    #############################################################################
    # If it is safe to hmoe, home the mount, and slre to safeCoords
    #
    if observatory.isSafeToHome():
        observatory.telescopeMount.home(asyncMode=False)
        observatory.telescopeMount.slewToSafeCoord(observatory.obsLocation)

        #############################################################################
        # flats
        #
        if False:
            exposure = 0.01
            tergetADU=20000.0
            for sequenceNdx in range(30):
                observatory.calculateFlatSkyLoc()
                observatory.slewToFlat()
                
                frameType = 'Flat'
                filterName = 'OSC'
                binning = 1
                reductionKind = 'No'
                reductionGrp = ''
                autoSaveFile = False
                asyncMode = False
                observatory.mainFilter.setFilterByName(filterName)
                observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
                imgAvgADU = float(observatory.mainCamera.getImgAvgADU())
                print(f'{filterName} {binning} {imgAvgADU}')
                tempSetPoint    = int(observatory.mainCamera.getTempSetPoint())
                objName         = 'noObj'
                observatory.mainCamera.saveImgToFile(observatory.filePathLights,frameType,tempSetPoint,objName,filterName,exposure,binning,sequenceNdx)
                exposure = exposure*tergetADU/imgAvgADU


        if True:
            #############################################################################
            # load the work list
            #
            observatory.loadWorkList()

            #############################################################################
            # Choose a work item
            #
            if observatory.chooseWorkItem():
                
                #############################################################################
                # Slew to object
                #
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Slew to object')
                observatory.telescopeMount.slewToRaDec(observatory.workList.loc[observatory.workItemRowNdx].skyCoordRaHrsJNow,observatory.workList.loc[observatory.workItemRowNdx].skyCoordDecValJNow,False)

                #############################################################################
                # Run focus
                # FEATURE ADD:
                #   * how to monitor focuser performance
                #
                if not observatory.runFocus():
                    #############################################################################
                    # handle focus did not work out
                    #
                    observatory.workList.loc[observatory.workItemRowNdx,'done']='failed'
                    observatory.saveWorkList()
                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToObserve state')
                    observatory.currentState = 'ReadyToObserve';
                else:
                    #############################################################################
                    # Retuen to object
                    #
                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Slew (return) to object')
                    observatory.telescopeMount.slewToRaDec(observatory.workList.loc[observatory.workItemRowNdx].skyCoordRaHrsJNow,observatory.workList.loc[observatory.workItemRowNdx].skyCoordDecValJNow,False)

                    #############################################################################
                    # Do a pointing correction
                    # FEATURE ADD:
                    #   * how to monitor pointing correction performance
                    #
                    if not observatory.pointingCorrection():
                        #############################################################################
                        # handle pointing correction did not work out
                        #
                        observatory.workList.loc[observatory.workItemRowNdx,'done']='failed'
                        observatory.saveWorkList()
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToObserve state')
                        observatory.currentState = 'ReadyToObserve';
                    else:
                        #############################################################################
                        # Start Guider
                        # FEATURE ADD:
                        #   * how to monitor guider performance
                        #
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Take guider exposure')
                        observatory.guider.setExposure(4)
                        observatory.guider.takeImage()
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Find guide star')
                        if not observatory.guider.findStar():
                            #############################################################################
                            # handle no guide star
                            #
                            observatory.workList.loc[observatory.workItemRowNdx,'done']='failed'
                            observatory.saveWorkList()
                            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToObserve state')
                            observatory.currentState = 'ReadyToObserve';
                        else:
                            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Start guider')
                            if not observatory.guider.start():
                                #############################################################################
                                # handle guider start did not work out
                                #
                                observatory.workList.loc[observatory.workItemRowNdx,'done']='failed'
                                observatory.saveWorkList()
                                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToObserve state')
                                observatory.currentState = 'ReadyToObserve';
                            else:
                                #############################################################################
                                # get the exposure details
                                #
                                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Set exposure set')
                                kBool_o=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_o) or (observatory.workList.loc[observatory.workItemRowNdx].done_o.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_o.astype(int))))
                                kBool_1=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_1) or (observatory.workList.loc[observatory.workItemRowNdx].done_1.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
                                kBool_2=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_2) or (observatory.workList.loc[observatory.workItemRowNdx].done_2.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
                                kBool_3=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_3) or (observatory.workList.loc[observatory.workItemRowNdx].done_3.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
                                if kBool_o:
                                    exposure            = observatory.workList.loc[observatory.workItemRowNdx].Exp_o.astype(int)
                                    binning             = observatory.workList.loc[observatory.workItemRowNdx].Bin_o.astype(int)
                                    filterName          = observatory.workList.loc[observatory.workItemRowNdx].F_o
                                    srtNdx              = observatory.workList.loc[observatory.workItemRowNdx].done_o.astype(int)
                                    endNdx              = observatory.workList.loc[observatory.workItemRowNdx].Rep_o.astype(int)
                                    maxCount            = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
                                elif kBool_1:
                                    exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp_j.astype(int)
                                    binning         = observatory.workList.loc[observatory.workItemRowNdx].Bin_j.astype(int)
                                    filterName      = observatory.workList.loc[observatory.workItemRowNdx].F_1
                                    srtNdx          = observatory.workList.loc[observatory.workItemRowNdx].done_1.astype(int)
                                    endNdx          = observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int)
                                    maxCount        = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
                                elif kBool_2:
                                    exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp_j.astype(int)
                                    binning         = observatory.workList.loc[observatory.workItemRowNdx].Bin_j.astype(int)
                                    filterName      = observatory.workList.loc[observatory.workItemRowNdx].F_2
                                    srtNdx          = observatory.workList.loc[observatory.workItemRowNdx].done_2.astype(int)
                                    endNdx          = observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int)
                                    maxCount        = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
                                elif kBool_3:
                                    exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp_j.astype(int)
                                    binning         = observatory.workList.loc[observatory.workItemRowNdx].Bin_j.astype(int)
                                    filterName      = observatory.workList.loc[observatory.workItemRowNdx].F_3
                                    srtNdx          = observatory.workList.loc[observatory.workItemRowNdx].done_3.astype(int)
                                    endNdx          = observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int)
                                    maxCount        = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
                                else:
                                    raise Exception('shit 1')

                                frameType       = 'Light'
                                tempSetPoint    = int(observatory.mainCamera.getTempSetPoint())
                                objName         = observatory.workList.loc[observatory.workItemRowNdx].ObjName
                                #############################################################################
                                # FEATURE ADD:
                                #   * gain control over calibration (reduction) frames
                                #
                                reductionKind   = 'Full'
                                reductionGrp    = f'{tempSetPoint}C_{filterName}_{exposure}s_{binning}bin'
                                autoSaveFile    = False
                                asyncMode       = True
                                                                
                                #############################################################################
                                # darken the observatory
                                #
                                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Darken observatory')
                                if observatory.mainControl['leaveLightOn']: observatory.dcPowerSwitch.setSwOff(6)

                                for sequenceNdx in range(srtNdx,min(endNdx,srtNdx+maxCount)):

                                    #############################################################################
                                    # if weather has triggered break sequence loop
                                    #
                                    if not(observatory.wxMonitor.isClear()):
                                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                                        observatory.currentState = 'NeedToClose';
                                        break
                                    #############################################################################
                                    # if user has requested break sequence loop
                                    #
                                    with open(observatory.mainControl['telescopiumLibraryPath']+'telescopium.json', 'r') as f:
                                      data = json.load(f)
                                    if(data['stopTelescopium']):
                                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ExitMainLoop state')
                                        observatory.currentState = 'ExitMainLoop';
                                        break

                                    #############################################################################
                                    # FEATURE ADD:
                                    #   * focus on second images as an option
                                    #
                                    if False:
                                        observatory.guider.stop()
                                        observatory.runFocus()
                                        observatory.pointingCorrection()
                                        observatory.guider.setExposure(4)
                                        observatory.guider.takeImage()
                                        observatory.guider.findStar()
                                        observatory.guider.start()

                                    #############################################################################
                                    # take image
                                    #
                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Set filter')
                                    observatory.mainFilter.setFilterByName(filterName)
                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Take exposure')
                                    observatory.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
                                    terminateReason = 'none' 
                                    while not observatory.mainCamera.isComplete():
                                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'{observatory.mainCamera.getExpStatus()}')
                                        #############################################################################
                                        # FEATURE ADD:
                                        #   * need to make this async and monitor guider performance
                                        #
                                        observatory.sleep(10)
                                        #############################################################################
                                        # if weather has triggered break sequence loop
                                        #
                                        if not(observatory.wxMonitor.isClear()):
                                            observatory.mainCamera.abortImage()
                                            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                                            observatory.currentState = 'NeedToClose';
                                            terminateReason = 'NeedToClose'
                                            break
                                        #############################################################################
                                        # if user has requested break sequence loop
                                        #
                                        with open(observatory.mainControl['telescopiumLibraryPath']+'telescopium.json', 'r') as f:
                                          data = json.load(f)
                                        if(data['stopTelescopium']):
                                            observatory.mainCamera.abortImage()
                                            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','User triggered exit')
                                            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ExitMainLoop state')
                                            observatory.currentState = 'ExitMainLoop';
                                            terminateReason = 'ExitMainLoop'
                                            break

                                    #############################################################################
                                    # break sequence loop if triggered
                                    #
                                    if terminateReason != 'none':
                                        break

                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Save image')
                                    observatory.mainCamera.saveImgToFile(observatory.filePathLights,frameType,tempSetPoint,objName,filterName,exposure,binning,sequenceNdx)
                                    #############################################################################
                                    # FEATURE ADD:
                                    #   * if plate solve fails, mark exposure as failed do not go to PANIC
                                    #
                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Platesolve')
                                    returnInfo=observatory.plateSolve(0.39*binning)
                                    if not returnInfo['retCode']:
                                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve failed')
                                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",returnInfo['errorCode'])
                                    else:
                                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,"",'Plate solve succeeded')

                                    #############################################################################
                                    # save work done
                                    #
                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Record successfull image')
                                    if kBool_o:
                                        observatory.workList.loc[observatory.workItemRowNdx,'done_o']=sequenceNdx+1
                                    elif kBool_1:
                                        observatory.workList.loc[observatory.workItemRowNdx,'done_1']=sequenceNdx+1
                                    elif kBool_2:
                                        observatory.workList.loc[observatory.workItemRowNdx,'done_2']=sequenceNdx+1
                                    elif kBool_3:
                                        observatory.workList.loc[observatory.workItemRowNdx,'done_3']=sequenceNdx+1
                                    else:
                                        raise Exception('shit 2')

                                    kBool_o=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_o) or (observatory.workList.loc[observatory.workItemRowNdx].done_o.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_o.astype(int))))
                                    kBool_1=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_1) or (observatory.workList.loc[observatory.workItemRowNdx].done_1.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
                                    kBool_2=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_2) or (observatory.workList.loc[observatory.workItemRowNdx].done_2.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
                                    kBool_3=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_3) or (observatory.workList.loc[observatory.workItemRowNdx].done_3.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))

                                    if kBool_o or kBool_1 or kBool_2 or kBool_3:
                                        observatory.workList.loc[observatory.workItemRowNdx,'done']='not done'
                                    else:
                                        observatory.workList.loc[observatory.workItemRowNdx,'done']='done'
                                    observatory.saveWorkList()

                                #############################################################################
                                # Stop the guider
                                #
                                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Stop guider')
                                observatory.guider.stop()

                                #############################################################################
                                # light the observatory
                                #
                                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Light observatory')
                                if observatory.mainControl['leaveLightOn']: observatory.dcPowerSwitch.setSwOn(6)

                                #############################################################################
                                # if nothing happned move to ReadyToObserve to get the next job
                                #
                                if observatory.currentState == 'Observing':
                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToObserve state')
                                    observatory.currentState = 'ReadyToObserve';
