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
import json
import sys
import traceback
import astropy.units as u

expMin = 1
expMax = 10
imgAvgADUMax = 64*1024
targetImgAvgADU = imgAvgADUMax*0.5

lastPanicState = ''
thisPanicState = ''

observatory = telescopium.Observatory()

while True:
    #############################################################################
    # Initializing
    #
    if observatory.currentState == 'PreCheck':
       try:
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
            # Start items needed to be powered up
            #
            observatory.startDomeController()
            observatory.startParkDetector()
            observatory.startMainCamera()
            observatory.startMainFilter()
            observatory.startFocuser()
            observatory.startGuider()

            #############################################################################
            # incase the observatory was left in non-closed, non-parked call the solver
            #
            if observatory.solveUnkState():
                #############################################################################
                # stop and close ports
                #
                observatory.stopCheese()
                observatory.stopTheSkyX()
                observatory.setAllSwOff()
                observatory.closePorts()
    
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to Initializing state')
                observatory.currentState = 'Initializing';
            else:
                observatory.setAllSwOff()
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Exit main loop, solveUnkState failed')
                break
       except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # Initializing
    #
    if observatory.currentState == 'Initializing':
        try:
            #############################################################################
            # Set Observatory Object
            #
            observatory = telescopium.Observatory()
            observatory.currentState = 'Initializing';
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

            observatory.loadFlatExpBlkList()
            flatDataFrame=pd.DataFrame(columns=['indexInflatExpBlk','exp','imgAvgADU','expProj','done'])
            flatDataFrame['indexInflatExpBlk']=observatory.flatExpBlk.index.values
            flatDataFrame['done']=False

            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to IdlePM state')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Waiting until {(observatory.timetoEnter_PoweredUp-observatory.hourOffset*u.hour).strftime("%Y-%m-%d %H:%M:%S")}')
            observatory.currentState = 'IdlePM'
            
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # IdlePM
    #
    if observatory.currentState == 'IdlePM':
        try:
            if Time.now()>observatory.timetoEnter_PoweredUp:
                #############################################################################
                # Start items not needed to be powered up and Cycle Power
                #
                observatory.startWxMonitor()
                observatory.startDcPowerSwitch()
                observatory.setAllSwOff()
                observatory.setAllSwOn()
                
                observatory.setPathsForTonight()

                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to PoweredUpPM state')
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Waiting until {(observatory.timetoEnter_AllConnected-observatory.hourOffset*u.hour).strftime("%Y-%m-%d %H:%M:%S")}')
                observatory.currentState = 'PoweredUpPM';

        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # PoweredUpPM
    #
    elif observatory.currentState == 'PoweredUpPM':
        try:
            if observatory.mainControl['justPowerOn']:
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to PoweredUpAM state')
                observatory.currentState = 'PoweredUpAM';
            else:
                if Time.now()>observatory.timetoEnter_AllConnected:
                    #############################################################################
                    # Start the items that were powered up
                    #
                    observatory.startDomeController()
                    observatory.startParkDetector()
                    observatory.startMount()
                    observatory.startMainCamera()
                    observatory.startMainFilter()
                    observatory.startFocuser()
                    observatory.startGuider()

                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to AllConnectedPM state')
                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Waiting until {(observatory.timetoEnter_ReadyToOpen-observatory.hourOffset*u.hour).strftime("%Y-%m-%d %H:%M:%S")}')
                    observatory.currentState = 'AllConnectedPM';
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # AllConnectedPM
    #
    elif observatory.currentState == 'AllConnectedPM':
        try:
            if Time.now()>observatory.timetoEnter_ReadyToOpen:
    
                #############################################################################
                # Select target CCD temperature
                # FEATURE ADD:
                #   * control camera temperature ramp (warm up)
                #
                observatory.setCameraTempTarget()
    
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToOpen state')
                observatory.currentState = 'ReadyToOpen';
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # ReadyToOpen
    #
    elif observatory.currentState == 'ReadyToOpen':
        try:
            if Time.now()>observatory.timetoLeave_ReadyToObserve:
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to AllConnectedAM state')
                observatory.currentState = 'AllConnectedAM';
            else:
                #if (Time.now()<observatory.timetoEnter_ReadyToFlats):
                    #if observatory.mainControl['takeBias']:
                        #############################################################################
                        # Run Bias Frames
                        # Does not work because theSkyX forces user intervention to cover the objective.
                        #
                        # if observatory.mainControl['leaveLightOn']:
                        #     observatory.dcPowerSwitch.setSwOff(6)
                        # for tempSetPointLocal in observatory.mainControl['a_list']:
                        #     if tempSetPointLocal >= observatory.tempSetPointForTonight:
                        #         observatory.mainCamera.setTempSetPoint(True,tempSetPointLocal,True,observatory.mainControl['waitTimeMin'])
                        #         for sequenceNdx in range(observatory.mainControl['numbBiasExp']):
                        #             frameType       = 'Bias'
                        #             tempSetPoint    = int(observatory.mainCamera.getTempSetPoint())
                        #             objName         = 'noObj'
                        #             filterName      = 'OSC'
                        #             exposure        = 0
                        #             binning         = 1
                        #             sequence        = sequenceNdx
                        #             autoSaveFile    = False
                        #             asyncMode       = False
                        #             observatory.mainCamera.takeImage(frameType,binning,autoSaveFile,asyncMode)
                        #             observatory.mainCamera.saveImgToFile(observatory.filePathBias,frameType,tempSetPoint,objName,filterName,exposure,binning,sequence)
                        #observatory.mainControl['takeBias'] = False
                        #if observatory.mainControl['leaveLightOn']:
                        #    observatory.dcPowerSwitch.setSwOn(6)
    
                #############################################################################
                # If it is clear open the roof
                #
                if observatory.wxMonitor.isClear():
                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Open roof')
                    observatory.domeController.openRoof()
                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to Open state')
                    observatory.currentState = 'Open';
                else:
                    #telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Weather not clear')
                    pass                    
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # Open
    #
    elif observatory.currentState == 'Open':
        try:
            if not(observatory.wxMonitor.isClear()):
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                observatory.currentState = 'NeedToClose';
            else:    
                #############################################################################
                # If it is safe to hmoe, home the mount, and slre to safeCoords and cool camera
                #
                if observatory.isSafeToHome():
                    if observatory.domeController.isOpen():
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Home mount')
                        observatory.telescopeMount.home(asyncMode=False)

                        #############################################################################
                        # Slew to safe position if need to wait to enter ready to observe
                        #
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Slew to safe coordinates')
                        observatory.telescopeMount.slewToSafeCoord(observatory.obsLocation)

                        #############################################################################
                        # Set and wait for mainCamera to cool
                        #
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Set main camera temperature set point')
                        observatory.mainCamera.setTempSetPoint(True,observatory.tempSetPointForTonight,True,observatory.mainControl['waitTimeMin'])    

                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to OpenAndHomed state')
                        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Waiting until {(observatory.timetoEnter_ReadyToFlats-observatory.hourOffset*u.hour).strftime("%Y-%m-%d %H:%M:%S")}')
                        observatory.currentState = 'OpenAndHomed';

        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # OpenAndHomed
    #
    elif observatory.currentState == 'OpenAndHomed':
        try:
            if not(observatory.wxMonitor.isClear()):
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                observatory.currentState = 'NeedToClose';
            elif Time.now()>observatory.timetoEnter_ReadyToFlats:
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Waiting until {(observatory.timetoEnter_ReadyToObserve-observatory.hourOffset*u.hour).strftime("%Y-%m-%d %H:%M:%S")}')
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to TakeFlats state')
                observatory.currentState = 'TakeFlats';
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # Take Flats
    #
    elif observatory.currentState == 'TakeFlats':
        try:
            if not(observatory.wxMonitor.isClear()):
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                observatory.currentState = 'NeedToClose';
            elif Time.now()>observatory.timetoEnter_ReadyToObserve:
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadyToObserve state')
                observatory.currentState = 'ReadyToObserve';
            elif observatory.mainControl['takeFlat']:
                #############################################################################
                # FEATURE ADD:
                #   * remake flats for OSC? and filtered?
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


                    if not(flatDataFrame.done.all()):
                        observatory.mainCamera.setTempSetPoint(True,observatory.tempSetPointForTonight,True,observatory.mainControl['waitTimeMin'])
                        filePrefix = f"{observatory.tempSetPointForTonight}C"
                        while not(flatDataFrame.done.all()):
                            observatory.calculateFlatSkyLoc()
                            observatory.slewToFlat()
                            for indexInD, row in flatDataFrame[(flatDataFrame.done==False)].iterrows():
                                expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
                                expSeqTemp.exp=expMin
                                expSeqTemp.rep=1
                                observatory.mainCamera.takeImgSeq(observatory.mainFilter,False,expSeqTemp,observatory.filePathFlats,filePrefix)
                                imgAvgADU = observatory.mainCamera.getImgAvgADU()
                                flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp'] = expSeqTemp.exp
                                flatDataFrame.loc[flatDataFrame.index[indexInD], 'imgAvgADU'] = imgAvgADU
                                if (imgAvgADU<0.9*imgAvgADUMax):
                                    flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']   = flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp']*targetImgAvgADU/imgAvgADU
                                    if flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']>expMax:
                                        flatDataFrame.loc[flatDataFrame.index[indexInD], 'done'] = True
                                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',telescopium.ptos('%-2d %-2d %4.2f %1d %5s %6.1f %4.2f'%(indexInD,flatDataFrame.loc[indexInD,'indexInflatExpBlk'],expSeqTemp.exp,expSeqTemp.bin,expSeqTemp.filterName,imgAvgADU,flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj'])).strip())
                            canidates = flatDataFrame[(flatDataFrame.expProj>=expMin)&(flatDataFrame.done!=True)].index.values
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
                                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',telescopium.ptos('%-2d %-2d %4.2f %1d %5s %6.1f %4.2f'%(indexInD,flatDataFrame.loc[indexInD,'indexInflatExpBlk'],expSeqTemp.exp,expSeqTemp.bin,expSeqTemp.filterName,imgAvgADU,flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj'])).strip())
                                expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
                                expSeqTemp.exp=flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']
                                observatory.mainCamera.takeImgSeq(observatory.mainFilter,True,expSeqTemp,observatory.filePathFlats,filePrefix)
                                flatDataFrame.loc[flatDataFrame.index[indexInD], 'done'] = True
                            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','pace delay at bottom of loop')
                            time.sleep(10)
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # ReadyToObserve
    #
    elif observatory.currentState == 'ReadyToObserve':
        try:
            if not(observatory.wxMonitor.isClear()):
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                observatory.currentState = 'NeedToClose';
            elif Time.now()>observatory.timetoLeave_ReadyToObserve:
               observatory.telescopeMount.parkAndDoNotDisconnect()
               if observatory.parkDetector.isParked():
                    if not observatory.mainControl['leaveOpen']:
                        observatory.domeController.closeRoof()
                    telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to AllConnectedAM state')
                    observatory.currentState = 'AllConnectedAM';
            else:    
               #############################################################################
               # load the work list
               #
               if observatory.mainControl['lookForJobs']:
                   observatory.loadWorkList()
    
                   #############################################################################
                   # Choose a work item
                   #
                   if observatory.chooseWorkItem():
                       telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to Observing state')
                       observatory.currentState = 'Observing'
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # Observing
    #
    elif observatory.currentState == 'Observing':
        try:
            if not(observatory.wxMonitor.isClear()):
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to NeedToClose state')
                observatory.currentState = 'NeedToClose';
            else:

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
                    # Return to object
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
                        #   * how to monitor guider performance?
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
                                #   * detect if calibration frame group exists and handle if not
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
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # NeedToClose
    #
    elif observatory.currentState == 'NeedToClose':
        try:
            observatory.telescopeMount.parkAndDoNotDisconnect()
            if observatory.parkDetector.isParked():
                observatory.domeController.closeRoof()
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to ReadtToOpen state')
            observatory.currentState = 'ReadyToOpen';
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # AllConnectedAM
    #
    elif observatory.currentState == 'AllConnectedAM':
        try:
            if Time.now()>observatory.timetoLeave_AllConnected:
                if observatory.domeControllerPortOpen:
                    observatory.domeController.closePort()
                if observatory.parkDetectorPortOpen:
                    observatory.parkDetector.closePort()
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to PoweredUpAM state')
                observatory.currentState = 'PoweredUpAM';
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # PoweredUpAM
    #
    elif observatory.currentState == 'PoweredUpAM':
        try:
            if (Time.now()>observatory.timetoLeave_PoweredUp) or observatory.mainControl['justPowerOn']:
                if not(observatory.mainControl['leavePowerOn']):
                    observatory.setAllSwOff()
                if observatory.dcPowerSwitchPortOpen:
                    observatory.dcPowerSwitch.closePort()
                observatory.calculateNight()
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to IdlePM state')
                observatory.currentState = 'IdlePM';
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,' '+observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # PANIC
    #
    elif observatory.currentState == 'PANIC':

        try:
            observatory.closePorts()
            observatory = telescopium.Observatory()
            observatory.currentState = 'PANIC'
            observatory.getMainControl()
            observatory.setPathsForTonight()
            observatory.mainControl['debugLevel']            = True     # (False) True to log debugging information
            observatory.mainControl['leaveLightOn']          = True      # (False)
            observatory.setObsLocation()
            observatory.calculateNight()
            observatory.startCheese()
            observatory.startTheSkyX()
            observatory.startWxMonitor()
            observatory.startDcPowerSwitch()
            observatory.setAllSwOff()
            observatory.setAllSwOn()
            observatory.startDomeController()
            observatory.startParkDetector()

            if observatory.solveUnkState():
                observatory.stopCheese()
                observatory.stopTheSkyX()
                observatory.setAllSwOff()
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
                observatory.getMainControl()
                observatory.setPathsForTonight()
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Advancing to Initializing state')
                observatory.currentState = 'Initializing';
                if thisPanicState == lastPanicState:
                    break
                lastPanicState = thisPanicState
            else:
                observatory.setAllSwOff()
                telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Exit main loop, solveUnkState failed')
                break
        except:
            thisPanicState = observatory.currentState
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'',f'Something went wrong in {observatory.currentState} state code')
            observatory.currentState = 'PANIC';
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception type : {ex_type.__name__}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Exception message : {ex_value}')
            telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,telescopium.currentFuncName(),f'Stack trace : {stack_trace}')

    #############################################################################
    # State1
    #
    elif observatory.currentState == 'ExitMainLoop':
        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','Exit main loop')
        break

    #############################################################################
    # Load json for gracefull trigger stop
    #
    with open(observatory.mainControl['telescopiumLibraryPath']+'telescopium.json', 'r') as f:
      data = json.load(f)
      
      observatory.mainControl['stopTelescopium']= data['stopTelescopium']
      observatory.mainControl['debugLevel']= data['debugLevel']
      observatory.mainControl['debugCommLevel']= data['debugCommLevel']      
      
    if(observatory.mainControl['stopTelescopium']):
        telescopium.writeLog(True,observatory.currentState,observatory.deviceKind,'','User triggered exit')
        observatory.currentState = 'ExitMainLoop';
    #############################################################################
    # pace delay at rottom of loop
    #
    observatory.sleep(observatory.mainControl['sleepAtLoopEnd'])





