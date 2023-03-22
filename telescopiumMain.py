#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import telescopium
import time
from astropy.time import Time
import math

expMin = 1
expMax = 10
imgAvgADUMax = 64*1024
targetImgAvgADU = imgAvgADUMax*0.5

lastPanicState = ''
thisPanicState = ''

observatory = telescopium.Observatory()

while True:
    #############################################################################
    #
    # Initializing
    #
    if observatory.currentState == 'PreCheck':
       try:
            #############################################################################
            #
            # Set Observatory Object
            #
            observatory = telescopium.Observatory()
            telescopiumMainControl=observatory.getTelescopiumMainControl()
 
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

            observatory.startCheese(telescopiumMainControl['getNewInstance'],telescopiumMainControl['webCamProc'],telescopiumMainControl['webCamApp'])
            observatory.startTheSkyX(telescopiumMainControl['getNewInstance'],telescopiumMainControl['theSkyProc'],telescopiumMainControl['theSkyApp'])
   
            observatory.startWxMonitor(telescopiumMainControl)
            observatory.startDcPowerSwitch(telescopiumMainControl)
            observatory.setAllSwOff(telescopiumMainControl['sleepForAllOff'])
            observatory.setAllSwOn(telescopiumMainControl['leaveLightOn'],telescopiumMainControl['sleepForAllOn'])
            
            observatory.startDomeController(telescopiumMainControl)
            observatory.startParkDetector(telescopiumMainControl)
            
            observatory.startMount(telescopiumMainControl)
            observatory.startMainCamera(telescopiumMainControl)
            observatory.startMainFilter(telescopiumMainControl)
            observatory.startFocuser(telescopiumMainControl)
            observatory.startGuider(telescopiumMainControl)

            observatory.stopCheese(telescopiumMainControl['webCamProc'],telescopiumMainControl['webCamApp'])
            observatory.stopTheSkyX(telescopiumMainControl['theSkyProc'],telescopiumMainControl['theSkyApp'])
            observatory.setAllSwOff(telescopiumMainControl['sleepForAllOff'])
            observatory.closePorts()

            observatory.currentState = 'Initializing';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
       except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';


    #############################################################################
    #
    # Initializing
    #
    if observatory.currentState == 'Initializing':
        try:
            #############################################################################
            # Set Observatory Object
            observatory = telescopium.Observatory()
            observatory.currentState = 'Initializing';
            telescopiumMainControl=observatory.getTelescopiumMainControl()

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
            telescopium.writeLog(True,observatory.currentState,'','Initializing Observatory')

            observatory.startCheese(telescopiumMainControl['getNewInstance'],telescopiumMainControl['webCamProc'],telescopiumMainControl['webCamApp'])
            observatory.startTheSkyX(telescopiumMainControl['getNewInstance'],telescopiumMainControl['theSkyProc'],telescopiumMainControl['theSkyApp'])

            observatory.loadFlatExpBlkList()
            telescopium.writeLog(True,observatory.currentState,'','Making resuts data frame')
            flatDataFrame=pd.DataFrame(columns=['indexInflatExpBlk','exp','imgAvgADU','expProj','done'])
            flatDataFrame['indexInflatExpBlk']=observatory.flatExpBlk.index.values
            flatDataFrame['done']=False

            observatory.currentState = 'IdlePM'
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';

    #############################################################################
    #
    # IdlePM
    #
    if observatory.currentState == 'IdlePM':
        if Time.now()>observatory.timetoEnter_PoweredUp:
            try:
                telescopium.writeLog(True,observatory.currentState,'','Working to enter PoweredUpPM state - Time triggered')
                observatory.startWxMonitor(telescopiumMainControl)
                observatory.startDcPowerSwitch(telescopiumMainControl)
                observatory.setAllSwOff(telescopiumMainControl['sleepForAllOff'])
                observatory.setAllSwOn(telescopiumMainControl['leaveLightOn'],telescopiumMainControl['sleepForAllOn'])
                observatory.setPathsForTonight()

                observatory.currentState = 'PoweredUpPM';
                telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
            except:
                thisPanicState = observatory.currentState
                telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
                observatory.currentState = 'PANIC';
        else:
            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter PoweredUpPM state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_PoweredUp-Time.now())))).strip())
    #############################################################################
    #
    # PoweredUpPM
    #
    elif observatory.currentState == 'PoweredUpPM':
        if telescopiumMainControl['justPowerOn']:
            observatory.currentState = 'PoweredUpAM';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        else:
            if Time.now()>observatory.timetoEnter_AllConnected:
                telescopium.writeLog(True,observatory.currentState,'','Working to enter AllConnectedPM state - Time triggered')
                try:
                    observatory.startDomeController(telescopiumMainControl)
                    observatory.startParkDetector(telescopiumMainControl)
                    observatory.startMount(telescopiumMainControl)
                    observatory.startMainCamera(telescopiumMainControl)
                    observatory.startMainFilter(telescopiumMainControl)
                    observatory.startFocuser(telescopiumMainControl)
                    observatory.startGuider(telescopiumMainControl)

                    observatory.currentState = 'AllConnectedPM';
                    telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
                except:
                    thisPanicState = observatory.currentState
                    telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
                    observatory.currentState = 'PANIC';
            else:
                telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter AllConnectedPM state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_AllConnected-Time.now())))).strip())
    #############################################################################
    #
    # AllConnectedPM
    #
    elif observatory.currentState == 'AllConnectedPM':
        if Time.now()>observatory.timetoEnter_ReadyToOpen:
            observatory.setCameraTempTarget(telescopiumMainControl['deltaTemp'],telescopiumMainControl['a_list'],telescopiumMainControl['b_list'])

            observatory.currentState = 'ReadyToOpen';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        else:
            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter ReadyToOpen state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_ReadyToOpen-Time.now())))).strip())
    #############################################################################
    #
    # ReadyToOpen
    #
    elif observatory.currentState == 'ReadyToOpen':
        if Time.now()>observatory.timetoLeave_ReadyToObserve:
            telescopium.writeLog(True,observatory.currentState,'','Timedout waiting to Wx tobe safe')
            observatory.currentState = 'AllConnectedAM';
            telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
        else:
            if (Time.now()<observatory.timetoEnter_ReadyToFlats) or telescopiumMainControl['forceTakeBias']:
                if telescopiumMainControl['takeBias']:
                    telescopium.writeLog(True,observatory.currentState,'','Taking Bias Frames')
                    #############################################################################
                    # Run Bias Frames
                    if telescopiumMainControl['leaveLightOn']:
                        observatory.dcPowerSwitch.setSwOff(6)
                    for tempSetPointLocal in telescopiumMainControl['a_list']:
                        if tempSetPointLocal >= observatory.tempSetPointForTonight:
                            observatory.mainCamera.setTempSetPoint(True,tempSetPointLocal,True)
                            for sequenceNdx in range(telescopiumMainControl['numbBiasExp']):
                                frameType       = 'Bias'
                                temp            = int(observatory.mainCamera.getTempSetPoint())
                                objName         = 'noObj'
                                filterName      = 'OSC'
                                exposure        = 0
                                binning         = 1
                                sequence        = sequenceNdx
                                autoSaveFile    = False
                                asyncMode       = False
                                observatory.mainCamera.takeBiasFrame(binning,autoSaveFile,asyncMode)
                                observatory.mainCamera.saveImgToFile(observatory.filePathBias,frameType,temp,objName,filterName,exposure,binning,sequence)
                    telescopiumMainControl['takeBias'] = False
                    if telescopiumMainControl['leaveLightOn']:
                        observatory.dcPowerSwitch.setSwOn(6)
                else:
                    telescopium.writeLog(True,observatory.currentState,'','bypassing bias frames (not asked for)')
            else:
                telescopium.writeLog(True,observatory.currentState,'','Too late to take bias frames\n')
            if observatory.wxMonitor.isClear():
                telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Wx is safe, Amb%6.2f Sky%6.2f Diff%6.2f'%(observatory.wxMonitor.ambTemp,observatory.wxMonitor.skyTemp,observatory.wxMonitor.deltaTemp)).strip())
                try:
                    telescopium.writeLog(True,observatory.currentState,'','Opening Roof')
                    observatory.domeController.openRoof()
                    observatory.currentState = 'Open';
                    telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
                except:
                    thisPanicState = observatory.currentState
                    telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
                    observatory.currentState = 'PANIC';
            else:
                telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Wx is not safe, Amb%6.2f Sky%6.2f Diff%6.2f'%(observatory.wxMonitor.ambTemp,observatory.wxMonitor.skyTemp,observatory.wxMonitor.deltaTemp)).strip())
    #############################################################################
    #
    # Open
    #
    elif observatory.currentState == 'Open':
        if not(observatory.wxMonitor.isClear()):
            observatory.currentState = 'NeedToClose';
            telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
        else:
            if True:
                if observatory.isSafeToHome():
                    telescopium.writeLog(True,observatory.currentState,'','is safe to home')
                    if observatory.domeController.isOpen():
                        try:
                            telescopium.writeLog(True,observatory.currentState,'','Homeing Mount')
                            observatory.telescopeMount.home(asyncMode=False)
                            telescopium.writeLog(True,observatory.currentState,'','Slew to safe position')
                            observatory.telescopeMount.slewToSafeCoordinates(observatory.obsLocation)
                            observatory.currentState = 'OpenAndHomed';
                            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
                        except:
                            thisPanicState = observatory.currentState
                            telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
                            observatory.currentState = 'PANIC';
                else:
                    telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Is not safe to home mount, waiting for sun seperation %6.3f > %2.0f '%(observatory.k,observatory.minimumSafeToHomeAngle)).strip())
            else:
                telescopium.writeLog(True,observatory.currentState,'','Home not needed')
                telescopium.writeLog(True,observatory.currentState,'','Slew to safe position')
                observatory.telescopeMount.gotoSafeCoordinates(observatory.obsLocation)
                observatory.currentState = 'OpenAndHomed';
                telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
    #############################################################################
    #
    # OpenAndHomed
    #
    elif observatory.currentState == 'OpenAndHomed':
        if not(observatory.wxMonitor.isClear()):
            observatory.currentState = 'NeedToClose';
            telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
        elif Time.now()>observatory.timetoEnter_ReadyToFlats:
            observatory.currentState = 'TakeFlats';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        else:
            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter TakeFlats state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_ReadyToFlats-Time.now())))).strip())
    #############################################################################
    #
    # Take Flats
    #
    elif observatory.currentState == 'TakeFlats':
        if not(observatory.wxMonitor.isClear()):
            observatory.currentState = 'NeedToClose';
            telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
        elif Time.now()>observatory.timetoEnter_ReadyToObserve:
            observatory.currentState = 'ReadyToObserve';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        elif telescopiumMainControl['takeFlat']:
            if not(flatDataFrame.done.all()):
                telescopium.writeLog(True,observatory.currentState,'','Setting Camera temp')
                observatory.mainCamera.setTempSetPoint(True,observatory.tempSetPointForTonight,True)
                filePrefix = f"{observatory.tempSetPointForTonight}C"
                while not(flatDataFrame.done.all()):
                    telescopium.writeLog(True,observatory.currentState,'','Top of loop')
                    telescopium.writeLog(True,observatory.currentState,'','Slew to flat')
                    observatory.calculateFlatSkyLoc()
                    observatory.slewToFlat()
                    telescopium.writeLog(True,observatory.currentState,'','updating for current time')
                    for indexInD, row in flatDataFrame[(flatDataFrame.done==False)].iterrows():
                        expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
                        expSeqTemp.exp=expMin
                        expSeqTemp.rep=1
                        observatory.mainCamera.takeImgSeq(observatory.mainFilter,False,expSeqTemp,observatory.filePathFlats,filePrefix)
                        imgAvgADU = observatory.mainCamera.getImgAvgADU()
                        #imgAvgADU = min(65000,(30000+7000*mainFilter.filterNdx[expSeqTemp.filterName])*expSeqTemp.exp)
                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp'] = expSeqTemp.exp
                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'imgAvgADU'] = imgAvgADU
                        if (imgAvgADU<0.9*imgAvgADUMax):
                            flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']   = flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp']*targetImgAvgADU/imgAvgADU
                            if flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']>expMax:
                                flatDataFrame.loc[flatDataFrame.index[indexInD], 'done'] = True
                            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('%-2d %-2d %4.2f %1d %5s %6.1f %4.2f'%(indexInD,flatDataFrame.loc[indexInD,'indexInflatExpBlk'],expSeqTemp.exp,expSeqTemp.bin,expSeqTemp.filterName,imgAvgADU,flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj'])).strip())
                    telescopium.writeLog(True,observatory.currentState,'','picking canidates')
                    canidates = flatDataFrame[(flatDataFrame.expProj>=expMin)&(flatDataFrame.done!=True)].index.values
                    telescopium.writeLog(True,observatory.currentState,'','running canidates')
                    for indexInD in canidates:
                        expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
                        expSeqTemp.exp=flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']
                        expSeqTemp.rep=1
                        observatory.mainCamera.takeImgSeq(observatory.mainFilter,False,expSeqTemp,observatory.filePathFlats,filePrefix)
                        imgAvgADU = observatory.mainCamera.getImgAvgADU()
                        #imgAvgADU = min(65000,(30000+7000*mainFilter.filterNdx[expSeqTemp.filterName])*expSeqTemp.exp)
                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp'] = expSeqTemp.exp
                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'imgAvgADU'] = imgAvgADU
                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']   = flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp']*targetImgAvgADU/imgAvgADU
                        telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('%-2d %-2d %4.2f %1d %5s %6.1f %4.2f'%(indexInD,flatDataFrame.loc[indexInD,'indexInflatExpBlk'],expSeqTemp.exp,expSeqTemp.bin,expSeqTemp.filterName,imgAvgADU,flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj'])).strip())
                        expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
                        expSeqTemp.exp=flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']
                        observatory.mainCamera.takeImgSeq(observatory.mainFilter,True,expSeqTemp,observatory.filePathFlats,filePrefix)
                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'done'] = True
                    telescopium.writeLog(True,observatory.currentState,'','pace delay at bottom of loop')
                    time.sleep(10)
            else:
                telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter ReadyToObserve state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_ReadyToObserve-Time.now())))).strip())
        else:
            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter ReadyToObserve state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_ReadyToObserve-Time.now())))).strip())
    #############################################################################
    #
    # ReadyToObserve
    #
    elif observatory.currentState == 'ReadyToObserve':
         if not(observatory.wxMonitor.isClear()):
            observatory.currentState = 'NeedToClose';
            telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
         elif Time.now()>observatory.timetoLeave_ReadyToObserve:
            telescopium.writeLog(True,observatory.currentState,'','Working to enter AllConnectedAM state - Time triggered')
            telescopium.writeLog(True,observatory.currentState,'','Parking Mount')
            observatory.telescopeMount.parkAndDoNotDisconnect()
            if observatory.parkDetector.isParked():
                if not telescopiumMainControl['leaveOpen']:
                    try:
                        telescopium.writeLog(True,observatory.currentState,'','Closing Roof')
                        observatory.domeController.closeRoof()
                    except:
                        thisPanicState = observatory.currentState
                        telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
                        observatory.currentState = 'PANIC';
                observatory.currentState = 'AllConnectedAM';
                telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
         else:
            telescopium.writeLog(True,observatory.currentState,'',f'Setting Camera cooler for tonight {observatory.tempSetPointForTonight}')
            observatory.mainCamera.setTempSetPoint(True,observatory.tempSetPointForTonight,True)
            if telescopiumMainControl['lookForJobs']:
                observatory.loadWorkList()
                if observatory.chooseWorkItem(mode='maxAlt'):
                    observatory.currentState = 'Observing'
                    telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
                else:
                    telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('No Job found, Highest target is %5.3f of %5.3f\n'%(max(observatory.workList.loc[(observatory.workList.done==0)].alt),observatory.usableHorizon)).strip())
    #############################################################################
    #
    # Observing
    #
    elif observatory.currentState == 'Observing':
         if not(observatory.wxMonitor.isClear()):
            observatory.currentState = 'NeedToClose';
            telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
         else:
            telescopium.writeLog(True,observatory.currentState,'','Executing job\n')
            
            telescopium.writeLog(True,observatory.currentState,'','Slewing Mount\n')
            observatory.telescopeMount.slewToRaDec(observatory.workList.loc[observatory.workItemRowNdx].skyCoordRaHrsJNow,observatory.workList.loc[observatory.workItemRowNdx].skyCoordDecValJNow,False)

            telescopium.writeLog(True,observatory.currentState,'','Focus run\n')
            observatory.runFocus()

            telescopium.writeLog(True,observatory.currentState,'','Slewing Mount\n')
            observatory.telescopeMount.slewToRaDec(observatory.workList.loc[observatory.workItemRowNdx].skyCoordRaHrsJNow,observatory.workList.loc[observatory.workItemRowNdx].skyCoordDecValJNow,False)

            telescopium.writeLog(True,observatory.currentState,'','Pointing Correction\n')
            observatory.pointingCorrection()

            for sequenceNdx in range(observatory.workList.loc[observatory.workItemRowNdx].Rep):                   
                if not(observatory.wxMonitor.isClear()):
                   observatory.currentState = 'NeedToClose';
                   telescopium.writeLog(True,observatory.currentState,'',f'Regressing to {observatory.currentState} state')
                   break
               
                # dither can use jog but guideing will erace the move?
                #observatory.dither()

                if sequenceNdx>0 and observatory.workList.loc[observatory.workItemRowNdx].focusBeforeEachExposure:
                    telescopium.writeLog(True,observatory.currentState,'','Focus run\n')
                    observatory.runFocus()
                
                observatory.guider.setExposure(4)
                observatory.guider.takeImage()
                observatory.guider.findStar()
                observatory.guider.start()
                #
                # wait for N good corrections
                #

                frameType       = 'Light'
                temp            = int(observatory.mainCamera.getTempSetPoint())
                objName         = observatory.workList.loc[observatory.workItemRowNdx].objName
                filterName      = 'OSC'
                exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp
                binning         = observatory.workList.loc[observatory.workItemRowNdx].bin

                # I dont have control of calibration groups.
                imageReduction  = 2
                imageReduction  = 0
                sequence        = sequenceNdx
                autoSaveFile    = False
                asyncMode       = False

                if telescopiumMainControl['leaveLightOn']: observatory.dcPowerSwitch.setSwOff(6)

                observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)

                if telescopiumMainControl['leaveLightOn']: observatory.dcPowerSwitch.setSwOn(6)

                observatory.mainCamera.saveImgToFile(observatory.filePathLights,frameType,temp,objName,filterName,exposure,binning,sequence)
                # does this place result back in image file?
                returnInfo=observatory.plateSolve()
                actualRaHrs  = returnInfo['imageCenterRAJ2000']
                actualDecVal = returnInfo['imageCenterDecJ2000']
                deltaRaMin   = (actualRaHrs -observatory.workList.loc[observatory.workItemRowNdx].skyCoordRaHrsJ2000 )*60*(360/24)*math.cos(returnInfo['imageCenterDecJ2000']*math.pi/180.0)
                deltaDecMin  = (actualDecVal-observatory.workList.loc[observatory.workItemRowNdx].skyCoordDecValJ2000)*60
                telescopium.writeLog(True,observatory.currentState,'',f'{observatory.workList.loc[observatory.workItemRowNdx].skyCoordRaHrsJ2000},{actualRaHrs},{deltaRaMin}')
                telescopium.writeLog(True,observatory.currentState,'',f'{observatory.workList.loc[observatory.workItemRowNdx].skyCoordDecValJ2000},{actualDecVal},{deltaDecMin}')

                observatory.guider.stop()

                x=1/0

            if observatory.currentState == 'NeedToClose':
                pass
            else:
                telescopium.writeLog(True,observatory.currentState,'',f'Mark {observatory.workList.loc[observatory.workItemRowNdx].objName} as done\n')
                observatory.workList.loc[observatory.workItemRowNdx,'done']=1
                observatory.workList.to_excel(observatory.telescopiumLibraryPath +'workList.ods',index=False)
    
                if observatory.workList.loc[observatory.workItemRowNdx,'done']==1:
                    observatory.currentState = 'ReadyToObserve';
                    telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
    #############################################################################
    #
    # NeedToClose
    #
    elif observatory.currentState == 'NeedToClose':
        telescopium.writeLog(True,observatory.currentState,'','Parking Mount')
        observatory.telescopeMount.parkAndDoNotDisconnect()
        if observatory.parkDetector.isParked():
            try:
                telescopium.writeLog(True,observatory.currentState,'','Closing Roof')
                observatory.domeController.closeRoof()
            except:
                thisPanicState = observatory.currentState
                telescopium.writeLog(True,observatory.currentState,'',f'Something went wrong in {observatory.currentState} state code')
                observatory.currentState = 'PANIC';
        observatory.currentState = 'ReadyToOpen';
        telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
    #############################################################################
    #
    # AllConnectedAM
    #
    elif observatory.currentState == 'AllConnectedAM':
        if Time.now()>observatory.timetoLeave_AllConnected:
            telescopium.writeLog(True,observatory.currentState,'','Working to enter PoweredUpAM state - Time triggered')
            if observatory.domeControllerPortOpen:
                telescopium.writeLog(True,observatory.currentState,'','Closing Dome Controller')
                observatory.domeController.closePort()
            if observatory.parkDetectorPortOpen:
                telescopium.writeLog(True,observatory.currentState,'','Closing Park Detector')
                observatory.parkDetector.closePort()
            observatory.currentState = 'PoweredUpAM';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        else:
            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter PoweredUpAM state'%(telescopium.deltaTimeTohms((observatory.timetoLeave_AllConnected-Time.now())))).strip())
    #############################################################################
    #
    # PoweredUpAM
    #
    elif observatory.currentState == 'PoweredUpAM':
        if (Time.now()>observatory.timetoLeave_PoweredUp) or telescopiumMainControl['justPowerOn']:
            telescopium.writeLog(True,observatory.currentState,'','Working to enter PoweredUpAM state - Time triggered')
            if not(telescopiumMainControl['leavePowerOn']):
                telescopium.writeLog(True,observatory.currentState,'','Turn DC Power off')
                observatory.setAllSwOff(0)
            if observatory.dcPowerSwitchPortOpen:
                telescopium.writeLog(True,observatory.currentState,'','Close serial port to DC power switch')
                observatory.dcPowerSwitch.closePort()
            observatory.calculateNight()
            observatory.currentState = 'IdlePM';
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')
        else:
            telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter IdlePM state'%(telescopium.deltaTimeTohms((observatory.timetoLeave_PoweredUp-Time.now())))).strip())
    #############################################################################
    #
    # PANIC
    #
    elif observatory.currentState == 'PANIC':
        telescopium.writeLog(True,observatory.currentState,'','Shit, Arrived at PANIC state')

        try:
            telescopium.writeLog(True,observatory.currentState,'','Trying to resolve observaory')
            observatory.closePorts()
            observatory = telescopium.Observatory()
            observatory.currentState = 'PANIC'
            telescopiumMainControl=observatory.getTelescopiumMainControl()
            telescopiumMainControl['debugLevel']            = True     # (False) True to log debugging information
            telescopiumMainControl['leaveLightOn']          = True      # (False)

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

            observatory.startCheese(telescopiumMainControl['getNewInstance'],telescopiumMainControl['webCamProc'],telescopiumMainControl['webCamApp'])
            observatory.startTheSkyX(telescopiumMainControl['getNewInstance'],telescopiumMainControl['theSkyProc'],telescopiumMainControl['theSkyApp'])
            observatory.setPathsForTonight()
            observatory.startWxMonitor(telescopiumMainControl)
            observatory.startDcPowerSwitch(telescopiumMainControl)
            observatory.setAllSwOff(telescopiumMainControl['sleepForAllOff'])
            observatory.setAllSwOn(telescopiumMainControl['leaveLightOn'],telescopiumMainControl['sleepForAllOn'])
            observatory.startDomeController(telescopiumMainControl)
            observatory.startParkDetector(telescopiumMainControl)

            #############################################################################
            # Start Mount

            domeController_isClosed = observatory.domeController.isClosed()
            domeController_isOpen = observatory.domeController.isOpen()
            parkDetector_isParked = observatory.parkDetector.isParked()

            while(not(domeController_isClosed and parkDetector_isParked)):
                if(domeController_isOpen and parkDetector_isParked):
                    telescopium.writeLog(True,observatory.currentState,'','Was Open and Parked')
                    telescopium.writeLog(True,observatory.currentState,'','-> Closing Roof')
                    observatory.domeController.closeRoof()

                if(domeController_isOpen and not parkDetector_isParked):
                    telescopium.writeLog(True,observatory.currentState,'','Was Open and Not Parked')
                    if observatory.isSafeToHome():
                        telescopium.writeLog(True,observatory.currentState,'','-> Connect Mount')
                        observatory.startMount(telescopiumMainControl)
                        telescopium.writeLog(True,observatory.currentState,'','-> Homeing Mount')
                        observatory.telescopeMount.home(False)
                        telescopium.writeLog(True,observatory.currentState,'','-> Parking Mount')
                        observatory.telescopeMount.park()
                    else:
                        telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Is not safe to home mount, waiting for sun seperation %6.3f > %2.0f '%(observatory.k,observatory.minimumSafeToHomeAngle)).strip())
                        telescopium.writeLog(True,observatory.currentState,'','Wait 1 minute')
                        time.sleep(60)

                if(domeController_isClosed and not parkDetector_isParked):
                    telescopium.writeLog(True,observatory.currentState,'','Was Closed and Not Parked')
                    observatory.parkDetector.FrcPPOn()
                    
                    if observatory.wxMonitor.isClear() or True:
                        telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Wx is safe, Amb%6.2f Sky%6.2f Diff%6.2f'%(observatory.wxMonitor.ambTemp,observatory.wxMonitor.skyTemp,observatory.wxMonitor.deltaTemp)).strip())
                        telescopium.writeLog(True,observatory.currentState,'','-> Opening Roof')
                        observatory.domeController.openRoof()
                    else:
                        x=1/0
                    
                    telescopium.writeLog(True,observatory.currentState,'','-> Delay for Mount to power up')
                    time.sleep(10)
                    observatory.parkDetector.FrcPPOff()

                domeController_isClosed = observatory.domeController.isClosed()
                domeController_isOpen = observatory.domeController.isOpen()
                parkDetector_isParked = observatory.parkDetector.isParked()


            telescopium.writeLog(True,observatory.currentState,'','Was Closed and Parked!!')

            observatory.stopCheese(telescopiumMainControl['webCamProc'],telescopiumMainControl['webCamApp'])
            observatory.stopTheSkyX(telescopiumMainControl['theSkyProc'],telescopiumMainControl['theSkyApp'])


            telescopium.writeLog(True,observatory.currentState,'','Turn DC Power Off')
            observatory.setAllSwOff(telescopiumMainControl['sleepForAllOff'])

            observatory.closePorts()

            #
            # If we have arrived here....
            #   Parked
            #   Closed
            #   Cheese is stopped
            #   TheSky is stopped
            #   All powered off
            #   Comports closed
            #   observaroty varianle is dispossable
            #

            observatory = telescopium.Observatory()
            telescopium.writeLog(True,observatory.currentState,'',f'Advancing to {observatory.currentState} state')

            if thisPanicState == lastPanicState:
                telescopium.writeLog(True,observatory.currentState,'','seems to be in a failure loop')
                break

            lastPanicState = thisPanicState

        except:
            telescopium.writeLog(True,observatory.currentState,'','Failed to resolve observaory')
            break
    #############################################################################
    #
    # IdleAM
    #
    elif observatory.currentState == 'IdleAM':
        break
    #############################################################################
    #
    # State1
    #
    elif observatory.currentState == 'ExitMainLoop':
        break
    #############################################################################
    #
    # pace delay at rottom of loop
    #
    observatory.sleep(telescopiumMainControl['sleepAtLoopEnd'])





