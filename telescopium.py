import io
import numpy as np
import os
import pandas as pd
import platform
import psutil
import serial
import socket
import subprocess
import time
import random
import math
import numpy
import matplotlib.pyplot as plt
import sys
import traceback
#from datetime import datetime
import datetime

from astropy.coordinates import FK5
from astropy.time import Time
from astropy.coordinates import AltAz
from astropy.coordinates import EarthLocation
from astropy.coordinates import get_moon
from astropy.coordinates import get_sun
from astropy.coordinates import ICRS
from astropy.coordinates import SkyCoord
from astropy.visualization import astropy_mpl_style, quantity_support
import astropy.units as u

plt.style.use(astropy_mpl_style)
quantity_support()

filePathLog = '/home/acomeau/Library/Telescopium/'

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

#############################################################################
#
# Observatory Class
#
class Observatory:
    def __init__(self):
        self.dcPowerSwitchPortOpen       = False
        self.wxMonitorPortOpen           = False
        self.observatoryIsPoweredUp      = False
        self.domeControllerPortOpen      = False
        self.parkDetectorPortOpen        = False
        self.wxBackgroundTaskStarted     = False

        self.deviceKind = 'Observatory'
        self.verboseLevel = 1
        self.debugCommLevel = False
        self.currentState = 'PreCheck';

    #############################################################################
    # Method
    #
    def getMainControl(self):
        self.mainControl = {}

        #############################################################################
        # debug Level Control
        self.mainControl['stopTelescopium']       = False       # json active while running
        self.mainControl['verboseLevel']          = 1           # json active while running
        self.mainControl['debugCommLevel']        = False       # json active while running

        #############################################################################
        # Serial port pacing
        self.mainControl['serialPortPaceDelay']    = 0.1          # json active while running
        self.mainControl['theSkyXPaceDelay']       = 0.1          # json active while running

        #############################################################################
        # Application suport
        self.mainControl['getNewInstance']        = True

        self.mainControl['sleepForAllOff']        = 30          # json active while running
        self.mainControl['sleepForAllOn']         = 10          # json active while running
        self.mainControl['sleepForMount']         = 10          # json active while running
        self.mainControl['sleepAtLoopEnd']        = 10          # json active while running

        #############################################################################
        # Run Control
        self.mainControl['normalScheduling']      = True
        self.mainControl['manualObservation']     = False

        self.mainControl['justPowerOn']           = False       # json active while running
        self.mainControl['leavePowerOn']          = False       # json active while running
        self.mainControl['leaveOpen']             = False       # json active while running
        self.mainControl['leaveLightOn']          = True        # json active while running
        self.mainControl['allowOpenInBadWx']      = False       # json active while running

        self.mainControl['lookForJobs']           = True        # json active while running

        self.mainControl['sunDownDegrees']        = -18         # json active while running
        self.mainControl['sunDownDegrees']        = -12         # json active while running
        self.mainControl['sunDownDegrees']        = -6         # json active while running
        self.mainControl['moonDownDegrees']       = -5          # json active while running

        self.mainControl['takeBias']              = False
        self.mainControl['takeDarks']             = False

        self.mainControl['numbBiasExp']           = 50
        self.mainControl['numbDarkExp']           = 12*2
        self.mainControl['darkExpRange']          = [300]

        self.mainControl['takeFlat']              = False
        self.mainControl['flatSpotAltitude']      = 75

        #############################################################################
        # Camera Cooler Control
        self.mainControl['deltaTemp']               = 30
        self.mainControl['a_list']                  = [-20,-10,0]
        self.mainControl['b_list']                  = [0,0,-10,-20]
        self.mainControl['waitTimeMin']             = 7

        #############################################################################
        # Focuser Control
        self.mainControl['telescopiumFocuserDataSet']       = 'telescopiumFocuser.ods'
        self.mainControl['telescopiumPointingDataSet']      = 'telescopiumPointing.ods'
        self.mainControl['telescopiumWorkList']             = 'telescopiumWorkList.ods'
        self.mainControl['numbDwell']               = 10          # json active while running
        self.mainControl['positionMax']             = 9000        # json active while running
        
        #############################################################################
        # Observatory Location
        self.mainControl['lat']                     = '45d04m57s'
        self.mainControl['lon']                     = '-75d42m33s'

        self.mainControl['homeLocAlt']              = 37.697      # json active while running
        self.mainControl['homeLocAz']               = 219.191     # json active while running

        #############################################################################
        # Avoid Sun, Horizon, Wx threshold
        self.mainControl['minimumSafeToHomeAngle']  = 20          # json active while running
        self.mainControl['usableHorizon']           = 30          # json active while running
        self.mainControl['wxMonitorTempThreshold']  = 15          # json active while running

        self.mainControl['workLoadSearchMethon']    = 'maxAlt'    # json active while running
        self.mainControl['maxExposureBlock_hr']     = 0.75

        #############################################################################
        # Set Com Ports
        if platform.system() == "Linux" :
            self.mainControl['dcPowerSwitchSerialPortStr']    ='/dev/K8090'
            self.mainControl['parkDetectorSerialPortStr']     ='/dev/ParkDetector'
            self.mainControl['wxMonitorSerialPortStr']        ='/dev/WxMonitor'
            self.mainControl['domeControllerSerialPortStr']   ='/dev/DomeController'
            self.mainControl['telescopiumLibraryPath']        = '/home/acomeau/Library/Telescopium/'
            self.mainControl['webCamProc']                    = 'cheese'
            self.mainControl['webCamApp']                     = '/bin/cheese'
            self.mainControl['theSkyProc']                    = 'TheSkyX'
            self.mainControl['theSkyApp']                     = '/home/acomeau/TheSkyX13507/TheSkyX'
        else :
            self.mainControl['dcPowerSwitchSerialPortStr']    ='COM12'
            self.mainControl['parkDetectorSerialPortStr']     ='COM5'
            self.mainControl['wxMonitorSerialPortStr']        ='COM9'
            self.mainControl['domeControllerSerialPortStr']   ='COM11'
            self.mainControl['telescopiumLibraryPath']        = 'C:/Users/Adrien/Documents/Library/Telescopium/'
            self.mainControl['webCamProc']                    = 'LogitechCamera.exe'
            self.mainControl['webCamApp']                     = 'C:/Program Files (x86)/Common Files/LogiShrd/LogiUCDpp/LogitechCamera.exe'
            self.mainControl['theSkyProc']                    = 'TheSky64.exe'
            self.mainControl['theSkyApp']                     = 'C:/Program Files (x86)/Software Bisque/TheSkyX Professional Edition/TheSky64/TheSky64.exe'

        self.theSkyXPaceDelay       = self.mainControl['theSkyXPaceDelay']          # json active while running

        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def setVerboseLevel(self,verboseLevel):
        writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
        self.verboseLevel = verboseLevel
        retInfo = True
        return retInfo

    #############################################################################
    # webcam monitor related methods
    #
    def startCheese(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            getNewInstance=self.mainControl['getNewInstance']
            appProc=self.mainControl['webCamProc']
            appPath=self.mainControl['webCamApp']
            subProc = self._startNew(getNewInstance,appProc,appPath)
            self.subProcCheese = subProc
            if not(checkIfProcessRunning(appProc)):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def stopCheese(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            appProc=self.mainControl['webCamProc']
            appPath=self.mainControl['webCamApp']
            self._stopProc(appProc,appPath)
            if checkIfProcessRunning(appProc):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def _startNew(self,getNewInstance,procName,cmdStr):
        if checkIfProcessRunning(procName):
            if(getNewInstance):
                theskyXProc = getProcessRunning(procName)
                theskyXProc.terminate()
                theskyXProc.wait()
                time.sleep(10)
                if checkIfProcessRunning(procName):
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Could not terminate '+procName)
                    raise Exception('Could not terminate '+procName)
                    subProc = 0
                else:
                    if platform.system() == "Linux" :
                        #subProc = subprocess.Popen(cmdStr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        subProc = subprocess.Popen(cmdStr, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    else :
                        subProc = subprocess.Popen(cmdStr)
                    time.sleep(10)
            else:
                pass
        else:
            if platform.system() == "Linux" :
                #subProc = subprocess.Popen(cmdStr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subProc = subprocess.Popen(cmdStr, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            else :
                subProc = subprocess.Popen(cmdStr)
            time.sleep(10)
        subProc=getProcessRunning(procName)
        #if not(checkIfProcessRunning(procName)):
        #    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Could not start '+procName)
        #    raise Exception('Could not start '+procName)
        #    subProc = 0
        retInfo = subProc
        return retInfo

    #############################################################################
    # Method
    #
    def _stopProc(self,procName,cmdStr):
        if checkIfProcessRunning(procName):
            theskyXProc = getProcessRunning(procName)
            theskyXProc.terminate()
            theskyXProc.wait()
            time.sleep(10)
            if checkIfProcessRunning(procName):
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Could not terminate '+procName)
                raise Exception('Could not terminate '+procName)
        retInfo = True
        return retInfo

    #############################################################################
    # theSkyX related methods
    #
    def startTheSkyX(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            getNewInstance=self.mainControl['getNewInstance']
            appProc=self.mainControl['theSkyProc']
            appPath=self.mainControl['theSkyApp']
            subProc = self._startNew(getNewInstance,appProc,appPath)
            self.subProcTheSkyX = subProc
            if not(checkIfProcessRunning(appProc)):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def stopTheSkyX(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            appProc=self.mainControl['theSkyProc']
            appPath=self.mainControl['theSkyApp']
            self._stopProc(appProc,appPath)
            if checkIfProcessRunning(appProc):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # weathermonitor related methods
    #
    def startWxMonitor(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.wxMonitor = WxMonitor()
            self.wxMonitor.serialPortPaceDelay=self.mainControl['serialPortPaceDelay']
            self.wxMonitor.verboseLevel=self.mainControl['verboseLevel']
            self.wxMonitor.debugCommLevel=self.mainControl['debugCommLevel']

            self.wxMonitor.setSerialPortStr(self.mainControl['wxMonitorSerialPortStr'])
            self.wxMonitor.setTempThreshold(self.mainControl['wxMonitorTempThreshold'])
            self.wxMonitor.openPort()
            self.wxMonitor.checkIdent()
            self.wxMonitorPortOpen = True
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # DC power switch related methods
    #
    def startDcPowerSwitch(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.dcPowerSwitch = DCPowerSwitch()
            self.dcPowerSwitch.serialPortPaceDelay=self.mainControl['serialPortPaceDelay']
            self.dcPowerSwitch.verboseLevel=self.mainControl['verboseLevel']
            self.dcPowerSwitch.debugCommLevel=self.mainControl['debugCommLevel']

            self.dcPowerSwitch.setSerialPortStr(self.mainControl['dcPowerSwitchSerialPortStr'])
            self.dcPowerSwitch.openPort()
            self.dcPowerSwitch.checkIdent()
            self.dcPowerSwitchPortOpen = True
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setAllSwOff(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            sleepTime=self.mainControl['sleepForAllOff']
            self.dcPowerSwitch.setSwOff(0)
            self.dcPowerSwitch.setSwOff(1)
            self.dcPowerSwitch.setSwOff(2)
            self.dcPowerSwitch.setSwOff(3)
            self.dcPowerSwitch.setSwOff(4)
            self.dcPowerSwitch.setSwOff(5)
            self.dcPowerSwitch.setSwOff(6)
            self.dcPowerSwitch.setSwOff(7)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Sleep {sleepTime:.1f} seconds for all to settle')
            time.sleep(sleepTime)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setAllSwOn(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            leaveLightOn=self.mainControl['leaveLightOn']
            sleepTime=self.mainControl['sleepForAllOn']
            self.dcPowerSwitch.setSwOn(0)
            self.dcPowerSwitch.setSwOn(1)
            self.dcPowerSwitch.setSwOn(2)
            self.dcPowerSwitch.setSwOn(3)
            self.dcPowerSwitch.setSwOn(4)
            self.dcPowerSwitch.setSwOn(5)
            self.dcPowerSwitch.setSwOn(6)
            self.dcPowerSwitch.setSwOn(7)
            if leaveLightOn:
                self.dcPowerSwitch.setSwOn(6)
            else:
                self.dcPowerSwitch.setSwOff(6)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Sleep {sleepTime:.1f} seconds for all to settle')
            time.sleep(sleepTime)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # dome related methods
    #
    def startDomeController(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.domeController = DomeController()
            self.domeController.serialPortPaceDelay=self.mainControl['serialPortPaceDelay']
            self.domeController.verboseLevel=self.mainControl['verboseLevel']
            self.domeController.debugCommLevel=self.mainControl['debugCommLevel']

            self.domeController.setSerialPortStr(self.mainControl['domeControllerSerialPortStr'])
            self.domeController.openPort()
            self.domeController.checkIdent()
            self.domeController.Activate=True
            self.domeControllerPortOpen = True
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # park detector related methods
    #
    def startParkDetector(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.parkDetector = ParkDetector()
            self.parkDetector.serialPortPaceDelay=self.mainControl['serialPortPaceDelay']
            self.parkDetector.verboseLevel=self.mainControl['verboseLevel']
            self.parkDetector.debugCommLevel=self.mainControl['debugCommLevel']

            self.parkDetector.setSerialPortStr(self.mainControl['parkDetectorSerialPortStr'])
            self.parkDetector.openPort()
            self.parkDetector.checkIdent()
            self.parkDetectorPortOpen = True
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f"Sleep {self.mainControl['sleepForMount']:.1f} seconds for Mount to power up")
            self.sleep(self.mainControl['sleepForMount'])
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # mount related methods
    #
    def startMount(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.telescopeMount = Mount()
            self.telescopeMount.verboseLevel=self.mainControl['verboseLevel']
            self.telescopeMount.debugCommLevel=self.mainControl['debugCommLevel']
            self.telescopeMount.theSkyXPaceDelay=self.mainControl['theSkyXPaceDelay']

            self.telescopeMount.connectDoNotUnpark()
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setObsLocation(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            latIn=self.mainControl['lat']
            lonIn=self.mainControl['lon']
            heightIn=0
            self.obsLocation = EarthLocation(lat=latIn, lon=lonIn, height=heightIn*u.m)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('ObsLocation = lat:%10s lon:%10s '%(self.obsLocation.lat.to_string(), self.obsLocation.lon.to_string())).strip())
            if not((str(self.obsLocation.lat)==latIn)and(str(self.obsLocation.lon)==lonIn)):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isSafeToHome(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Checking if safeToHome')
            timeNowUTC = Time.now()
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'TimeNowUT  ={timeNowUTC}')
            self.mountHome = AltAz(alt=self.mainControl['homeLocAlt']*u.deg,az=self.mainControl['homeLocAz']*u.deg,obstime=timeNowUTC, location=self.obsLocation)
            self.mountHome = self.mountHome.transform_to(ICRS())
            self.mountHome = SkyCoord(self.mountHome.ra.value, self.mountHome.dec.value, frame='icrs', unit='deg')
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Mx Home    ={self.mountHome.to_string("hmsdms")}')
            sun=get_sun(timeNowUTC)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Sun        ={sun.to_string("hmsdms")}')
            self.k=sun.separation(self.mountHome).deg
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Seperation ={self.k:.1f}')
            retInfo = self.k > self.mainControl['minimumSafeToHomeAngle']
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def pointingCorrection(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            frameType       = 'Light'
            temp            = int(self.mainCamera.getTempSetPoint())
            objName         = self.workList.loc[self.workItemRowNdx].ObjName+'PointingExp'
            filterName      = 'OSC'
            exposure        = 10
            binning         = 2
            reductionKind   = 'No'
            reductionGrp    = ''
            sequence        = 0
            autoSaveFile    = False
            asyncMode       = False

            self.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
            self.mainCamera.saveImgToFile(self.filePathLights,frameType,temp,objName,filterName,exposure,binning,sequence)
            returnInfo=self.plateSolve(0.78)
            if not returnInfo['retCode']:
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Plate solve failed')
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),returnInfo['errorCode'])
                retInfo = False
            else:
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Plate solve succeeded')
                actualRaHrs  = returnInfo['imageCenterRAJ2000']
                actualDecVal = returnInfo['imageCenterDecJ2000']
    
                deltaRaMin   = (actualRaHrs -self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000 )*60*(360/24)*math.cos(returnInfo['imageCenterDecJ2000']*math.pi/180.0)
                deltaDecMin  = (actualDecVal-self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000)*60
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'{self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000},{actualRaHrs},{deltaRaMin}')
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'{self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000},{actualDecVal},{deltaDecMin}')
    
                self.telescopeMount.loadPointingDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumPointingDataSet'])
                self.telescopeMount.pointingDataSet.loc[len(self.telescopeMount.pointingDataSet)] = {'DateTime':Time.now(), 'deltaRaMin':deltaRaMin, 'deltaDecMin':deltaDecMin}
                self.telescopeMount.savePointingDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumPointingDataSet'])

                self.telescopeMount.jogRa(-deltaRaMin)
                self.telescopeMount.jogDec(-deltaDecMin)
    
                sequence        = 1
                self.mainCamera.takeImage(frameType,exposure,binning,reductionKind,reductionGrp,autoSaveFile,asyncMode)
                self.mainCamera.saveImgToFile(self.filePathLights,frameType,temp,objName,filterName,exposure,binning,sequence)
                returnInfo=self.plateSolve(0.78)
                if not returnInfo['retCode']:
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Plate solve failed')
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),returnInfo['errorCode'])
                    retInfo = False
                else:
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Plate solve succeeded')
                    actualRaHrs  = returnInfo['imageCenterRAJ2000']
                    actualDecVal = returnInfo['imageCenterDecJ2000']
                    deltaRaMin   = (actualRaHrs -self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000 )*60*(360/24)*math.cos(returnInfo['imageCenterDecJ2000']*math.pi/180.0)
                    deltaDecMin  = (actualDecVal-self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000)*60
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'{self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000},{actualRaHrs},{deltaRaMin}')
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'{self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000},{actualDecVal},{deltaDecMin}')
                    #############################################################################
                    # FEATURE ADD:
                    #   * Measure a good correction
                    #
                    retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def dither(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            minDitherArcSec = 4
            maxDitherArcSec = 10
            DitherXarcMin = ((random.random() * (maxDitherArcSec - minDitherArcSec +1)) + minDitherArcSec) / 60
            DitherYarcMin = ((random.random() * (maxDitherArcSec - minDitherArcSec +1)) + minDitherArcSec) / 60
            if (math.floor(random.random() * 2)) == 0:
                NorS = 'N'
            else:
                NorS = 'S'
            if (math.floor(random.random() * 2)) == 0:
                EorW = 'E'
            else:
                EorW = 'W'
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'{60*DitherXarcMin:.1f}"{NorS} {60*DitherYarcMin:.1f}"{EorW}')
            self.telescopeMount.jog(DitherXarcMin, NorS, DitherYarcMin, EorW)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # focuser related methods
    #
    def startFocuser(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            #############################################################################
            # get an instance and set control values
            #
            self.mainFocuser = Focuser()
            self.mainFocuser.verboseLevel=self.mainControl['verboseLevel']
            self.mainFocuser.debugCommLevel=self.mainControl['debugCommLevel']
            self.mainFocuser.theSkyXPaceDelay=self.mainControl['theSkyXPaceDelay']

            self.mainFocuser.numbDwell = self.mainControl['numbDwell']
            self.mainFocuser.positionMax=self.mainControl['positionMax']

            self.mainFocuser.connect()

            #############################################################################
            # Load temperature curve and place focuser on it
            #
            #############################################################################
            # FEATURE ADD:
            #   * needs to cope with an empty cal info set
            #   * needs to allow for different hw setups
            #
            self.mainFocuser.loadFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])
            self.mainFocuser.setTempCurve()
            self.mainFocuser.moveToTempCurve()

            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def findLostFocuser(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            offsetList=200*np.array([1,-1,-2,2,3,-3,-4,4,5,-5,-6,6,7,-7,-8,8,9,-9,-10,10])
            self.mainFocuser.loadFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])
            self.mainFocuser.setTempCurve()
            for offset in offsetList:
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Trying {offset}')
                self.mainFocuser.moveToTempCurve()
                self.mainFocuser.move(offset)
                focusFound = self.mainFocuser.focus2()
                if focusFound:
                    break
            if focusFound:
                #############################################################################
                # Found it!
                self.mainFocuser.mainFocuserDataSet.drop(self.mainFocuser.mainFocuserDataSet.index,inplace=True)
                self.mainFocuser.mainFocuserDataSet.loc[len(self.mainFocuser.mainFocuserDataSet)] = {'DateTime':Time.now(), 'Temperature':self.mainFocuser.getTemp(),'Step':self.mainFocuser.getPosition()}
                self.mainFocuser.mainFocuserDataSet.loc[len(self.mainFocuser.mainFocuserDataSet)] = {'DateTime':Time.now(), 'Temperature':self.mainFocuser.getTemp()+0.0001,'Step':self.mainFocuser.getPosition()}
                self.mainFocuser.saveFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])
                retInfo = True
            else:
                retInfo = False                
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def runFocus(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            #############################################################################
            # FEATURE ADD:
            #   * Measure imafe FWHM, reject if > ???
            #
            retInfo = True
            self.mainFocuser.loadFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])
            self.mainFocuser.setTempCurve()
            self.mainFocuser.moveToTempCurve()
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Test Focuser')
            if not self.mainFocuser.focus2():
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Test focus failed, trying to find lost focuser')
                if not self.findLostFocuser():
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Failed to find lost focuser')                    
                    retInfo = False
                    return retInfo
                else:
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Found lost focuser')                           
                    self.mainFocuser.loadFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])
                    self.mainFocuser.setTempCurve()
                
            self.mainFocuser.meanFocusPosition = 0
            for sequenceNdx in range(self.mainFocuser.numbDwell):
                #############################################################################
                # FEATURE ADD:
                #   * check weather
                #   * check user exit
                #

                self.mainFocuser.moveToTempCurve()
                if not self.mainFocuser.focus2():
                    retInfo = False
                    break

                self.mainFocuser.loadFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])
                self.mainFocuser.mainFocuserDataSet.loc[len(self.mainFocuser.mainFocuserDataSet)] = {'DateTime':Time.now(), 'Temperature':self.mainFocuser.getTemp(), 'Step':self.mainFocuser.getPosition()}
                self.mainFocuser.saveFocuserDataSet(self.mainControl['telescopiumLibraryPath'],self.mainControl['telescopiumFocuserDataSet'])

                self.mainFocuser.setTempCurve()
                self.mainFocuser.meanFocusPosition += self.mainFocuser.getPosition()/self.mainFocuser.numbDwell
            if retInfo:
                self.mainFocuser.moveTo(self.mainFocuser.meanFocusPosition)
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # main filter related methods
    #
    def startMainFilter(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.mainFilter = MainFilter()
            self.mainFilter.verboseLevel=self.mainControl['verboseLevel']
            self.mainFilter.debugCommLevel=self.mainControl['debugCommLevel']
            self.mainFilter.theSkyXPaceDelay=self.mainControl['theSkyXPaceDelay']

            command = ''\
                    + "var temp=SelectedHardware.filterWheelModel;" \
                    + "var Out;" \
                    + "Out=temp;"
            skyXresult = skyXcmd(self.mainFilter,command,True)
            skyXparts = skyXresult.split("|")
            if 'No Filter Wheel Selected' in skyXparts[0]:
                self.mainFilter.kind = 'OSC'
            else:
                self.mainFilter.kind = 'Filtered'
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'MainFilter is {self.mainFilter.kind}')

            self.mainFilter.connect()
            self.mainFilter.getNumbFilters()
            self.mainFilter.getFilterNames()
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # main camera related methods
    #
    def startMainCamera(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.mainCamera = MainCamera()
            self.mainCamera.verboseLevel=self.mainControl['verboseLevel']
            self.mainCamera.debugCommLevel=self.mainControl['debugCommLevel']
            self.mainCamera.theSkyXPaceDelay=self.mainControl['theSkyXPaceDelay']

            self.mainCamera.connect()
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setCameraTempTarget(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            deltaTemp=self.mainControl['deltaTemp']
            a_list=self.mainControl['a_list']
            b_list=self.mainControl['b_list']
            self.tempSetPointForTonight=([item for item in a_list if item >= (self.wxMonitor.getAmbTemp()-deltaTemp)])
            self.tempSetPointForTonight=b_list[len(self.tempSetPointForTonight)]
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Amb %5.1f, MinSetPoint %5.1f, Selected SetPt %5.1f '%(self.wxMonitor.getAmbTemp(),self.wxMonitor.getAmbTemp()-deltaTemp,self.tempSetPointForTonight)).strip())
            if (self.tempSetPointForTonight<-20) or (self.tempSetPointForTonight>0):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def plateSolve(self,imageScale):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            if os.path.exists(self.mainCamera.lastSaveFilePath+'/'+self.mainCamera.lastFileName.split('.')[0]+'.SRC'):
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Remove old SRC file')
                os.remove(self.mainCamera.lastSaveFilePath+'/'+self.mainCamera.lastFileName.split('.')[0]+'.SRC')
    
            #############################################################################
            # FEATURE ADD:
            #   * solve hardcoced imagescale
            #   * should use insertWCS?
            #
            
            self.imageScale=imageScale
            command = ''\
                    + f"ImageLink.pathToFITS = '{self.mainCamera.lastSaveFilePath}/{self.mainCamera.lastFileName}';" \
                    + f"ImageLink.scale = {self.imageScale};" \
                    + "ImageLink.unknownScale = 1;" \
                    + "ImageLink.execute();" \
                    + "Out = ImageLinkResults.errorCode;" \
                    + "Out += '|' + ImageLinkResults.succeeded;" \
                    + "Out += '|' + ImageLinkResults.searchAborted;" \
                    + "Out += '|' + ImageLinkResults.errorText;" \
                    + "Out += '|' + ImageLinkResults.imageScale;" \
                    + "Out += '|' + ImageLinkResults.imagePositionAngle;" \
                    + "Out += '|' + ImageLinkResults.imageCenterRAJ2000;" \
                    + "Out += '|' + ImageLinkResults.imageCenterDecJ2000;" \
                    + "Out += '|' + ImageLinkResults.imageFWHMInArcSeconds;" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),skyXresult)
            skyXparts = skyXresult.split("|")
            if len(skyXparts) == 2:
                retInfo = {}
                retInfo['retCode'] = False                
                retInfo['errorCode'] = (skyXparts[0])                
                retInfo['succeeded'] = (skyXparts[1])
            elif len(skyXparts) == 10:
                retInfo = {}
                retInfo['retCode'] = True                
                retInfo['errorCode'] = (skyXparts[0])
                retInfo['succeeded'] = (skyXparts[1])
                retInfo['searchAborted'] = (skyXparts[2])
                retInfo['errorText'] = (skyXparts[3])
                retInfo['imageScale'] = float(skyXparts[4])
                retInfo['imagePositionAngle'] = float(skyXparts[5])
                retInfo['imageCenterRAJ2000'] = float(skyXparts[6])
                retInfo['imageCenterDecJ2000'] = float(skyXparts[7])
                retInfo['imageFWHMInArcSeconds'] = float(skyXparts[8])
            else:
                x=1/0
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def plateSolve2(self,imageScale):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            if os.path.exists(self.mainCamera.lastSaveFilePath+'/'+self.mainCamera.lastFileName.split('.')[0]+'.SRC'):
                writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Remove old SRC file')
                os.remove(self.mainCamera.lastSaveFilePath+'/'+self.mainCamera.lastFileName.split('.')[0]+'.SRC')

            self.imageScale=imageScale
            command = ''\
                    + "img = ccdsoftCameraImage;" \
                    + f'img.Path = "{self.mainCamera.lastSaveFilePath}/{self.mainCamera.lastFileName}";' \
                    + 'img.Open();' \
                    + f'img.ScaleInArcsecondsPerPixel={self.imageScale};' \
                    + 'img.InsertWCS(true);' \
                    + 'img.Save();' \
                    + 'img.Close();' \
                    + "var Out=12;" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),skyXresult)
            skyXparts = skyXresult.split("|")
            if skyXparts[0] == '0':
                retInfo = {}
                retInfo['retCode'] = True                
                retInfo['errorCode'] = (skyXparts[0])                
                retInfo['succeeded'] = (skyXparts[1])
            else:
                x=1/0
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # guider related methods
    #
    def startGuider(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.guider = Guider()
            self.guider.verboseLevel=self.mainControl['verboseLevel']
            self.guider.debugCommLevel=self.mainControl['debugCommLevel']
            self.guider.theSkyXPaceDelay=self.mainControl['theSkyXPaceDelay']

            self.guider.connect()
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # handle the lost observatory
    #
    def solveUnkState(self):
        writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
        retInfo = True
        domeController_isClosed = self.domeController.isClosed()
        domeController_isOpen = self.domeController.isOpen()
        parkDetector_isParked = self.parkDetector.isParked()
        while(not(domeController_isClosed and parkDetector_isParked)):
            if(domeController_isOpen and parkDetector_isParked):
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'Was Open and Parked')
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'-> Closing Roof')
                self.domeController.closeRoof()
            if(domeController_isOpen and not parkDetector_isParked):
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'Was Open and Not Parked')
                if self.isSafeToHome():
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'-> Connect Mount')
                    self.startMount()
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'-> Homeing Mount')
                    self.telescopeMount.home(False)
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'-> Parking Mount')
                    self.telescopeMount.park()
                else:
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ptos('Is not safe to home mount, waiting for sun seperation %6.3f > %2.0f '%(self.k,self.mainControl['minimumSafeToHomeAngle'])).strip())
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'Wait 1 minute')
                    time.sleep(60)
            if(domeController_isClosed and not parkDetector_isParked):
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'Was Closed and Not Parked')
                if self.wxMonitor.isClear():
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ptos('Wx is safe, Amb%6.2f Sky%6.2f Diff%6.2f'%(self.wxMonitor.ambTemp,self.wxMonitor.skyTemp,self.wxMonitor.deltaTemp)).strip())
                    self.parkDetector.FrcPPOn()
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'-> Opening Roof')
                    self.domeController.openRoof()
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'-> Delay 10seconds for Mount to power up')
                    time.sleep(10)
                    self.parkDetector.FrcPPOff()
                else:
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),"Was Closed and Not Parked and Wx is bad")
                    retInfo = False
                    break
            domeController_isClosed = self.domeController.isClosed()
            domeController_isOpen = self.domeController.isOpen()
            parkDetector_isParked = self.parkDetector.isParked()
        if retInfo:
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),'Was Closed and Parked!!')
        return retInfo

    #############################################################################
    # flats related methods
    #
    def loadFlatExpBlkList(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.flatExpBlk = pd.read_pickle(self.mainControl['telescopiumLibraryPath']+'/flatExpBlk.pkl')
            retInfo = True
            return retInfo

        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def calculateFlatSkyLoc(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')

            timeNowUTC = Time.now()
            frames = AltAz(obstime=timeNowUTC, location=self.obsLocation)
            sun  = get_sun (timeNowUTC)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun  (RaDec)=',sun.to_string('hmsdms')).strip())

            sunAzAlt  = get_sun (timeNowUTC).transform_to(frames)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun  (AzAlt)=',sunAzAlt.to_string('hmsdms')).strip())

            self.flatSpot = AltAz(alt=self.mainControl['flatSpotAltitude']*u.deg,az=(sunAzAlt.az.value+180)*u.deg,obstime=timeNowUTC, location=self.obsLocation)
            self.flatSpot = self.flatSpot.transform_to(ICRS())
            self.flatSpot = SkyCoord(self.flatSpot.ra.value, self.flatSpot.dec.value, frame='icrs', unit='deg')

            flatSpotAzAlt  = self.flatSpot.transform_to(frames)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Flat (AzAlt)=',flatSpotAzAlt.to_string('hmsdms')).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Flat (RaDec)=',self.flatSpot.to_string('hmsdms')).strip())
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def slewToFlat(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.telescopeMount.slewToRaDec(self.flatSpot.ra.hour, self.flatSpot.dec.value, False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # night related methods
    #
    def setPathsForTonight(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            dateStringForTonight = datetime.datetime.now().strftime("%Y%m%d")
            self.filePathBias    = self.mainControl['telescopiumLibraryPath'] + 'Bias/'      + dateStringForTonight
            self.filePathFlats   = self.mainControl['telescopiumLibraryPath'] + 'Flats/'     + dateStringForTonight
            self.filePathDarks   = self.mainControl['telescopiumLibraryPath'] + 'Darks/'     + dateStringForTonight
            self.filePathLights  = self.mainControl['telescopiumLibraryPath'] + 'Lights/'    + dateStringForTonight

            self.filePathBias    = self.mainControl['telescopiumLibraryPath'] + dateStringForTonight
            self.filePathFlats   = self.mainControl['telescopiumLibraryPath'] + dateStringForTonight
            self.filePathDarks   = self.mainControl['telescopiumLibraryPath'] + dateStringForTonight
            self.filePathLights  = self.mainControl['telescopiumLibraryPath'] + dateStringForTonight
            global filePathLog
            filePathLog          = self.mainControl['telescopiumLibraryPath'] + dateStringForTonight
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def calculateNight(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            
            now = Time(datetime.datetime((datetime.datetime.now()+datetime.timedelta(days=1)).year, (datetime.datetime.now()+datetime.timedelta(days=1)).month, (datetime.datetime.now()+datetime.timedelta(days=1)).day, (datetime.datetime.now()+datetime.timedelta(days=1)).hour, (datetime.datetime.now()+datetime.timedelta(days=1)).minute, (datetime.datetime.now()+datetime.timedelta(days=1)).second))            
            self.hourOffset=int((24*(Time.now()-now).value)%24)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Time offset is {self.hourOffset:.1f}hours')
            
            delta_midnight = np.linspace(-12, 12, 1000)*u.hour
            midnightLocal = Time(datetime.datetime((datetime.datetime.now()+datetime.timedelta(days=1)).year, (datetime.datetime.now()+datetime.timedelta(days=1)).month, (datetime.datetime.now()+datetime.timedelta(days=1)).day, 0, 0, 0))
            utcoffset = -self.hourOffset*u.hour  # Eastern Daylight Time
            midnight = midnightLocal - utcoffset
            times = midnight + delta_midnight
            frames = AltAz(obstime=times, location=self.obsLocation)

            sunaltazs  = get_sun (times).transform_to(frames)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Get sun complete')
            #moonaltazs = get_moon(times).transform_to(frames)

            self.sunSet       = midnight+delta_midnight[sunaltazs.alt.value<0][0]
            self.sunSetFlats  = midnight+delta_midnight[sunaltazs.alt.value<1][0]
            self.sunSetAstro  = midnight+delta_midnight[sunaltazs.alt.value<self.mainControl['sunDownDegrees']][0]
            self.sunRiseAstro = midnight+delta_midnight[sunaltazs.alt.value<self.mainControl['sunDownDegrees']][-1]
            self.sunRise      = midnight+delta_midnight[sunaltazs.alt.value<0][-1]

            if self.mainControl['normalScheduling']:
                self.timetoEnter_PoweredUp          = self.sunSetFlats - 2*u.h
                self.timetoEnter_AllConnected       = self.sunSetFlats - 1*u.h
                self.timetoEnter_ReadyToOpen        = self.sunSetFlats - 0.5*u.h
                self.timetoEnter_ReadyToFlats       = self.sunSetFlats
                self.timetoEnter_ReadyToObserve     = self.sunSetAstro
                self.timetoLeave_ReadyToObserve     = self.sunRiseAstro
                self.timetoLeave_AllConnected       = self.sunRise
                self.timetoLeave_PoweredUp          = self.sunRise +1*u.h
            else:
                self.timetoEnter_PoweredUp          = Time.now()
                self.timetoEnter_AllConnected       = Time.now()
                self.timetoEnter_ReadyToOpen        = Time.now()
                self.timetoEnter_ReadyToFlats       = Time.now()
                self.timetoEnter_ReadyToObserve     = Time.now()
                self.timetoLeave_ReadyToObserve     = self.sunRiseAstro
                self.timetoLeave_AllConnected       = self.sunRise
                self.timetoLeave_PoweredUp          = self.sunRise +1*u.h

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun set                     ',self.sunSet).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun set  Flats              ',self.sunSetFlats).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun set  astro              ',self.sunSetAstro).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun rise astro              ',self.sunRiseAstro).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('Sun rise                    ',self.sunRise).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoEnter_PoweredUp       ',self.timetoEnter_PoweredUp).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoEnter_AllConnected    ',self.timetoEnter_AllConnected).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoEnter_ReadyToOpen     ',self.timetoEnter_ReadyToOpen).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoEnter_ReadyToFlats    ',self.timetoEnter_ReadyToFlats).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoEnter_ReadyToObserve  ',self.timetoEnter_ReadyToObserve).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoLeave_ReadyToObserve  ',self.timetoLeave_ReadyToObserve).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoLeave_AllConnected    ',self.timetoLeave_AllConnected).strip())
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),ptos('TimetoLeave_PoweredUp       ',self.timetoLeave_PoweredUp).strip())
            if ((self.timetoLeave_PoweredUp-self.timetoEnter_PoweredUp).value)>1:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def calculateNight2(self):
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')

            now = Time(datetime.datetime((datetime.datetime.now()+datetime.timedelta(days=1)).year, (datetime.datetime.now()+datetime.timedelta(days=1)).month, (datetime.datetime.now()+datetime.timedelta(days=1)).day, (datetime.datetime.now()+datetime.timedelta(days=1)).hour, (datetime.datetime.now()+datetime.timedelta(days=1)).minute, (datetime.datetime.now()+datetime.timedelta(days=1)).second))            
            self.hourOffset=int((24*(Time.now()-now).value)%24)
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Time offset is {self.hourOffset:.1f}hours')


            self.midnightLocal = Time(datetime.datetime((datetime.datetime.now()+datetime.timedelta(days=1)).year, (datetime.datetime.now()+datetime.timedelta(days=1)).month, (datetime.datetime.now()+datetime.timedelta(days=1)).day, 0, 0, 0))
            self.utcoffset = -self.hourOffset*u.hour  # Eastern Daylight Time
            self.midnight = self.midnightLocal - self.utcoffset
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Calculate frames over night')
            self.delta_midnight = np.linspace(-12, 12, 1+(24)*4)*u.hour
            self.times = self.midnight + self.delta_midnight
            self.frames = AltAz(obstime=self.times, location=self.obsLocation)


            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Calculate sun location over night')
            self.sunaltazs = get_sun(self.times).transform_to(self.frames)

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Calculate moon location over night')
            self.moonaltazs= get_moon(self.times).transform_to(self.frames)

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Calculate sun/moon/joint down times over night')
            self.sunIsDown  = self.sunaltazs.alt.value<self.mainControl['sunDownDegrees']
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Sun is down (below {self.mainControl["sunDownDegrees"]:.1f}) for {self.sunIsDown.sum()*0.25:.1f} hours')
            self.moonIsDown = self.moonaltazs.alt.value<self.mainControl['moonDownDegrees']
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Moon is down (below {self.mainControl["moonDownDegrees"]:.1f}) for {self.moonIsDown.sum()*0.25:.1f} hours')
            self.sunAndMoonAreDown = self.sunIsDown * self.moonIsDown
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Both are down for {self.sunAndMoonAreDown.sum()*0.25:.1f} hours')

            self.timesItIsDark = self.times[self.sunAndMoonAreDown]

            makePlots=True
            if makePlots:
                plt.plot(self.delta_midnight, self.sunaltazs.alt, color='r', label='Sun')
                plt.plot(self.delta_midnight, self.moonaltazs.alt, color=[0.75]*3, ls='--', label='Moon')
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(self.mainControl['sunDownDegrees']*u.deg, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Calculate all workListItems location over night')

            self.workListSkyCoords = SkyCoord(self.workList.skyCoordRaHrsJ2000[:]*u.hour, self.workList.skyCoordDecValJ2000[:]*u.deg, frame='icrs')
            self.workListAltaz = self.workListSkyCoords[:, np.newaxis].transform_to(self.frames[np.newaxis])

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Numb Objects                    {self.workListAltaz.shape[0]:.1f}')

            if makePlots:
                plt.plot(self.delta_midnight, self.workListAltaz[:].alt.degree.T, marker='', alpha=0.5)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(0, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

                plt.plot(self.delta_midnight[self.sunAndMoonAreDown], self.workListAltaz[:,self.sunAndMoonAreDown].alt.degree.T, marker='', alpha=0.5)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(0*u.deg, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Calculate times each object is observable')

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f"Useable horizon is {self.mainControl['usableHorizon']:.1f}")

            # Calculate while the sun is down what frames for each object that are above the useable horizon
            self.pointersToAboveHorizon=self.workListAltaz[:,self.sunAndMoonAreDown].alt.degree>self.mainControl['usableHorizon']

            # the usable time is the net sum of time each object is above the horizon
            self.durationAboveHorizon_hrs=(self.pointersToAboveHorizon).sum(axis=1)*0.25


            # minimum time is met if time above the horizon exceeds the needed time
            self.pointersToitemsWithEnoughTime = self.durationAboveHorizon_hrs>(self.workList['NetTimeMin']/60)


            self.workListWithEnoughTimeAltaz=self.workListAltaz[self.pointersToitemsWithEnoughTime]

            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'Numb Objects with ehough time   {self.workListWithEnoughTimeAltaz.shape[0]:.1f}')

            self.dunno=self.pointersToAboveHorizon[self.pointersToitemsWithEnoughTime,:]
            self.dunno.shape

            self.earlyStartTime = np.zeros((self.pointersToitemsWithEnoughTime.sum()))
            self.lastEndTime = np.zeros((self.pointersToitemsWithEnoughTime.sum()))

            for rowNdx in range(self.dunno.shape[0]):
                row=self.dunno[rowNdx,:]
                self.earlyStartTime[rowNdx]=np.min(np.nonzero(row==True)[0])
                self.lastEndTime[rowNdx]=np.max(np.nonzero(row==True)[0])

            self.earlyStartTime = self.timesItIsDark[self.earlyStartTime.astype(int)]
            self.lastEndTime = self.timesItIsDark[self.lastEndTime.astype(int)]
            self.lastStartTime = self.lastEndTime-(self.workList[self.pointersToitemsWithEnoughTime]['NetTimeMin']).values.tolist()*u.min

            print(f'delts_midlight                  {self.delta_midnight.shape}')
            print(f'times                           {self.times.shape}')
            print(f'sunIsDown                       {self.sunIsDown.shape}')
            print(f'moonIsDown                      {self.moonIsDown.shape}')
            print(f'sunAndMoonAreDown               {self.sunAndMoonAreDown.shape}')
            print(f'workListAltaz                   {self.workListAltaz.shape}')
            print(f'pointersToAboveHorizon          {self.pointersToAboveHorizon.shape}')
            print(f'durationAboveHorizon_hrs        {self.durationAboveHorizon_hrs.shape}')
            print(f'pointersToitemsWithEnoughTime   {self.pointersToitemsWithEnoughTime.shape}')
            print(f'workListWithEnoughTimeAltaz     {self.workListWithEnoughTimeAltaz.shape}')
            print(f'dunno                           {self.dunno.shape}')
            print(f'earlyStartTime                  {self.earlyStartTime.shape}')
            print(f'lastEndTime                     {self.lastEndTime.shape}')
            print(f'lastStartTime                   {self.lastStartTime.shape}')

            if makePlots+True:
                plt.plot(self.delta_midnight[self.sunAndMoonAreDown], self.workListWithEnoughTimeAltaz[:,self.sunAndMoonAreDown].alt.degree.T, marker='', alpha=0.5)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.mainControl['sunDownDegrees']*u.deg, 90*u.deg, self.sunaltazs.alt < self.mainControl['sunDownDegrees']*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(0*u.deg, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

    #############################################################################
    # Workload related methods
    #
    def loadWorkList(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            #self.workList = pd.read_pickle(self.mainControl['telescopiumLibraryPath']+'WorkList/'+'workList.pkl')
            self.workList = pd.read_excel(self.mainControl['telescopiumLibraryPath'] + self.mainControl['telescopiumWorkList'])
            if self.workList.shape[0]==0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def chooseWorkItem(self):
        #############################################################################
        # FEATURE ADD:
        #   * Add moon down condition
        #   * Add west of Mederian
        #
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            match self.mainControl['workLoadSearchMethon']:
                case 'maxAlt':
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f'{self.workList.shape[0]:.1f} items to look over')

                    #############################################################################
                    # make all data current
                    #
                    writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Measure what where now')
                    aa = AltAz(location=self.obsLocation, obstime=Time.now())
                    for index, row in self.workList.iterrows():
                        skyCoordJ2000 = SkyCoord.from_name(row.ObjName)
                        skyCoordJNow  = skyCoordJ2000.transform_to(FK5(equinox='J2023'))

                        self.workList.loc[index,'skyCoordRaHrsJ2000'] = skyCoordJ2000.ra.hour
                        self.workList.loc[index,'skyCoordDecValJ2000'] = skyCoordJ2000.dec.value
                        self.workList.loc[index,'skyCoordRaHrsJNow'] = skyCoordJNow.ra.hour
                        self.workList.loc[index,'skyCoordDecValJNow'] = skyCoordJNow.dec.value

                        workItemSkyCoord = SkyCoord(self.workList.loc[index,'skyCoordRaHrsJNow']*u.hour, self.workList.loc[index,'skyCoordDecValJNow']*u.deg, frame='icrs')

                        self.workList.loc[index,'altNow'] = workItemSkyCoord.transform_to(aa).alt.value
                        self.workList.loc[index,'azNow'] = workItemSkyCoord.transform_to(aa).az.value

                    #############################################################################
                    # test Horizon,...
                    #
                    self.workList['altMet'] = self.workList['altNow']>self.workList['AltMin']
                    self.workList = self.workList.replace(True,'met')
                    self.workList = self.workList.replace(False,'not met')

                    #############################################################################
                    # evaluate strict conditions, Not Done, above min Alt, Filter/OSC match
                    #
                    self.workList['strictConditionsMet'] = (self.workList['done']=='not done') & (self.workList['altMet']=='met') & (self.workList['Kind']==self.mainFilter.kind)
                    self.workList = self.workList.replace(True,'met')
                    self.workList = self.workList.replace(False,'not met')

                    #############################################################################
                    # Sort by Priority, alt
                    #
                    foo=self.workList.sort_values(by=['strictConditionsMet','Pri','altNow'],ascending=[True,False,False])
                    self.workList=foo
                    #print(self.workList.T)
                    if self.workList.iloc[0]['strictConditionsMet']  == 'met':
                        self.workItemRowNdx = self.workList.index[0]
                        writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),f"Found {self.workList.loc[self.workItemRowNdx]['ObjName']} {self.workList.loc[self.workItemRowNdx]['CommonName']}, Pri {self.workList.loc[self.workItemRowNdx]['Pri']:.1f} in work list at {self.workList.loc[self.workItemRowNdx]['altNow']:.1f}deg")
                        return True
                    else:
                        self.workItemRowNdx = float("nan")
                        writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'No work found in work list')
                        return False
                case _:
                    ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                    writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
                    raise Exception(ExcMsg)
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def saveWorkList(self):
        try:
            writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
            self.workList.to_excel(self.mainControl['telescopiumLibraryPath'] + self.mainControl['telescopiumWorkList'],index=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,self.currentState,self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Time related methods
    #
    def sleep(self,sleepTimeSec):
        time.sleep(sleepTimeSec)
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def pause(self):
        writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Pause... ')
        input('pause')
        retInfo = True
        return retInfo

    #############################################################################
    # serial port related methods
    #
    def closePorts(self):
        writeLog(self.verboseLevel>0,self.currentState,self.deviceKind,currentFuncName(),'Enter method')
        if self.wxMonitorPortOpen:
            self.wxMonitor.closePort()
        if self.dcPowerSwitchPortOpen:
            self.dcPowerSwitch.closePort()
        if self.domeControllerPortOpen:
            self.domeController.closePort()
        if self.parkDetectorPortOpen:
            self.parkDetector.closePort()
        retInfo = True
        return retInfo

#############################################################################
# Method
#
def writeLog(verboseLevel,ObsState,device,method,logcomment):
    logLine = ptos(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),' | %15s | %15s | %20s | %s'%(ObsState, device, method,logcomment))

    if verboseLevel:print(logLine.strip())

    if not os.path.exists(filePathLog):os.makedirs(filePathLog)
    with open(filePathLog+'/telescopium.log', 'a') as the_file:the_file.write(logLine)

    retInfo = True
    return retInfo

#############################################################################
#
# DCPowerSwitch Class
#
class DCPowerSwitch:
    def __init__(self):
        self.deviceKind = 'DC Power Switch'

    #############################################################################
    # Method
    #
    def setSerialPortStr(self,serialPortString):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.serialPortStr = serialPortString
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def openPort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 19200
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def closePort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort.close()
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def checkIdent(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.getSw(0)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setSwOff(self,id):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            buffer = [4,18,2**id,0,0,0,15]
            buffer[5] = (((buffer[0]+buffer[1]+buffer[2])^255) & 255) + 1
            self.serPort.write(bytes(buffer))
            time.sleep(self.serialPortPaceDelay)
            writeLog(self.debugCommLevel,'',self.deviceKind,currentFuncName(),'    SENT : >'+ptos(buffer).strip()+'<')
            if not(self.getSw(id)==0):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setSwOn(self,id):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            buffer = [4,17,2**id,0,0,0,15]
            buffer[5] = (((buffer[0]+buffer[1]+buffer[2])^255) & 255) + 1
            self.serPort.write(bytes(buffer))
            time.sleep(self.serialPortPaceDelay)
            writeLog(self.debugCommLevel,'',self.deviceKind,currentFuncName(),'    SENT : >'+ptos(buffer).strip()+'<')
            if not(self.getSw(id)==1):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getSw(self,id):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            buffer = [4,24,0,0,0,0,15]
            buffer[5] = (((buffer[0]+buffer[1]+buffer[2])^255) & 255) + 1
            self.serPort.reset_input_buffer()
            self.serPort.write(bytes(buffer))
            time.sleep(self.serialPortPaceDelay)
            writeLog(self.debugCommLevel,'',self.deviceKind,currentFuncName(),'    SENT : >'+ptos(buffer).strip()+'<')

            self.responce=self.serPort.read(7)

            buffer[0]=self.responce[0]
            buffer[1]=self.responce[1]
            buffer[2]=self.responce[2]
            buffer[3]=self.responce[3]
            buffer[4]=self.responce[4]
            buffer[5]=self.responce[5]
            buffer[6]=self.responce[6]

            writeLog(self.debugCommLevel,'',self.deviceKind,currentFuncName(),'    RXED : >'+ptos(buffer).strip()+'<')

            if not(buffer[5] == (((buffer[0]+buffer[1]+buffer[2]+buffer[3])^255) & 255) + 1):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)

            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Switch '+ str(id) +' state is ' + str(((buffer[3]>>id) & 1)))
            retInfo = ((buffer[3]>>id) & 1)
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# ParkDetector Class
#
class ParkDetector:
    def __init__(self):
        self.deviceKind = 'Park Detector'
        self.sleepTimeForUserInput = 1

    #############################################################################
    # Method
    #
    def setSerialPortStr(self,serialPortString):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.serialPortStr = serialPortString
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def openPort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 9600
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def closePort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort.close()
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def checkIdent(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'IDENT','ParkDetector')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def FrcMntOn(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'FrcMntOn','FrcMntOn')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def FrcMntOff(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'FrcMntOff','FrcMntOff')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def FrcPPOn(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'FrcPPOn','FrcPPOn')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def FrcPPOff(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'FrcPPOff','FrcPPOff')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getAll(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'Getting all data ={self.responce}')
            return self.responce
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isParked(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            isParked = serialExpect(self,'isParked','Parked')
            if isParked:
                writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Checking is parked = parked')
            else:
                writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Checking is parked = not parked')
            retInfo = isParked
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# DomeController Class
#
class DomeController:
    def __init__(self):
        self.deviceKind = 'Dome Controller'
        self.verboseLevel = 0
        self.debugCommLevel = False

    #############################################################################
    # Method
    #
    def setVerboseLevel(self,verboseLevel):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.verboseLevel = verboseLevel
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def setDebugCommLevel(self,debugCommLevel):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.debugCommLevel = debugCommLevel
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def setSerialPortStr(self,serialPortString):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.serialPortStr = serialPortString
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def setPaceDelay(self,serialPortPaceDelay):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.serialPortPaceDelay = serialPortPaceDelay
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def openPort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 9600
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def closePort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort.close()
            if self.serPort.isOpen():
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def checkIdent(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'IDENT#','RoofRoller')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def openRoof(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if self.Activate:
                if not(serialSend(self,'QUERYROOF#')=='is Open'):
                    if not(serialExpect(self,'OPENROOF#','OPENROOF Ack')):
                        ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),ExcMsg)
                        raise Exception(ExcMsg)
                    time.sleep(1)
                    while serialExpect(self,'QUERYROOF#','is Opening'):
                        time.sleep(5)
                    time.sleep(1)
                    if not(serialExpect(self,'QUERYROOF#','is Open')):
                        ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),ExcMsg)
                        raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def closeRoof(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if self.Activate:
                if not(serialSend(self,'QUERYROOF#')=='is Closed'):
                    if not(serialExpect(self,'CLOSEROOF#','CLOSEROOF Ack')):
                        ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),ExcMsg)
                        raise Exception(ExcMsg)
                    time.sleep(1)
                    while serialExpect(self,'QUERYROOF#','is Closing'):
                        time.sleep(5)
                    time.sleep(1)
                    if not(serialExpect(self,'QUERYROOF#','is Closed')):
                        ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),ExcMsg)
                        raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def queryRoof(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.responce = serialSend(self,'QUERYROOF#')
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo =  self.responce
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isOpen(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo =  serialExpect(self,'QUERYROOF#','is Open')
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isClosed(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo =  serialExpect(self,'QUERYROOF#','is Closed')
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# WxMonitor Class
#
class WxMonitor:
    def __init__(self):
        self.deviceKind = 'Wx Monitor'

        self.deltaTemp = 99
        self.ambTemp = 99
        self.skyTemp = 99

        self.isClearBool = True
        self.isClearNow = True

        self.timeBecameClear = Time.now()-u.s*120

        self.safeToOpenDelay_sec = 60
        
        self.tempThreshold=20.0

    #############################################################################
    # Method
    #
    def setSerialPortStr(self,serialPortString):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.serialPortStr = serialPortString
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def openPort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 9600
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def closePort(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.serPort.close()
            if self.serPort.isOpen():
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def checkIdent(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not(serialExpect(self,'IDENT','wxStation')):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setTempThreshold(self,tempThreshold):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.tempThreshold = tempThreshold
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getAmbTemp(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.ambTemp=float(serialSend(self,'T'))
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'Getting ambient temperature {self.ambTemp:.1f}C')
            retInfo =  self.ambTemp
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getSkyTemp(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.skyTemp=float(serialSend(self,'ST'))
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'Getting sky temperature {self.skyTemp:.1f}C')
            retInfo =  self.skyTemp
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isClear(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.getAmbTemp()
            self.getSkyTemp()
            self.deltaTemp=self.ambTemp-self.skyTemp
            self.wasClear = self.isClearNow
            self.isClearNow=self.deltaTemp>self.tempThreshold
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(), ptos('Amb%6.2f Sky%6.2f Diff%6.2f'%(self.ambTemp,self.skyTemp,self.deltaTemp)).strip())
            if self.isClearNow and not self.wasClear:
                self.timeBecameClear = Time.now()
            if self.isClearNow and ((Time.now()-self.timeBecameClear).sec > self.safeToOpenDelay_sec):
                self.isClearBool = True
            else:
                self.isClearBool = False
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(), ptos('wasClear %s, isClearNow %s, timeClear %f %s'%(self.wasClear,self.isClearNow,(Time.now()-self.timeBecameClear).sec,self.isClearBool)).strip())
            retInfo =  self.isClearBool
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# Mount Class
#
class Mount:
    def __init__(self):
        self.deviceKind = 'Mount'
        self.postSlewPause = 2

    #############################################################################
    # Method
    # Expects >undefined|No error. Error = 0.<
    #
    def connect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Connect();"
            skyXcmd(self,command,allowErrors=False)
            if not(self.isConnected()):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    # exception on result value
    #
    def isConnected(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "Out=sky6RASCOMTele.IsConnected;" 
            skyXresult = skyXcmd(self,command,allowErrors=True)                     
            skyXparts = skyXresult.split("|")
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'isConnected = {skyXresult}')
            if skyXparts[0] == '0':
                result = False
            elif skyXparts[0] == '1':
                result = True
            else:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)                
            retInfo =  result
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def connectDoNotUnpark(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.ConnectAndDoNotUnpark();"
            skyXcmd(self,command,allowErrors=False)
            if not(self.isConnected()):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def disconnect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Disconnect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def disconnectTelescope(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTheSky.DisconnectTelescope();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def home(self, asyncMode: bool):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Connect();"\
                    + f"sky6RASCOMTele.Asynchronous={js_bool(asyncMode)};" \
                    + "sky6RASCOMTele.FindHome();" 
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Home complete')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def park(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Asynchronous=false;" \
                    + "sky6RASCOMTele.Park();" 
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Park complete')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def parkAndDoNotDisconnect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Asynchronous=false;" \
                    + "sky6RASCOMTele.ParkAndDoNotDisconnect();"
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Park complete')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isParked(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "Out=sky6RASCOMTele.IsParked();" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'Parked = {skyXresult}')
            if skyXparts[0] == 'false':
                result = False
            elif skyXparts[0] == 'true':
                result = True
            else:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)                
            retInfo =  result
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def unpark(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Connect();"\
                    + "sky6RASCOMTele.Unark();" 
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Unpark completed')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def slewToSafeCoord(self,obsLocation):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            timeNowUTC = Time.now()
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),ptos('timeNowUTC      =',timeNowUTC).strip())
            mountSafeCoord = AltAz(alt=45*u.deg,az=55*u.deg,obstime=timeNowUTC, location=obsLocation)
            mountSafeCoord = mountSafeCoord.transform_to(ICRS())
            mountSafeCoord = SkyCoord(mountSafeCoord.ra.value, mountSafeCoord.dec.value, frame='icrs', unit='deg')
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),ptos('mountSafeCoord  =',mountSafeCoord.to_string('hmsdms')).strip())
            self.slewToRaDec(mountSafeCoord.ra.hour,mountSafeCoord.dec.value,False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def slewToRaDec(self,Ra,Dec,asyncMode):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Connect();" \
                    + f"sky6RASCOMTele.Asynchronous={js_bool(asyncMode)};" \
                    + "var wasTracking=sky6RASCOMTele.IsTracking;" \
                    + "var oldRaRate=sky6RASCOMTele.dRaTrackingRate;" \
                    + "var oldDecRate=sky6RASCOMTele.dDecTrackingRate;" \
                    + f'sky6RASCOMTele.SlewToRaDec({Ra},{Dec},"");' \
                    + "sky6RASCOMTele.SetTracking(wasTracking,1,oldRaRate,oldDecRate);" 
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Slew completed')
            time.sleep(self.postSlewPause)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def slewToAltAz(self, alt, az, asyncMode):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Connect();" \
                    + f"sky6RASCOMTele.Asynchronous={js_bool(asyncMode)};" \
                    + "var wasTracking=sky6RASCOMTele.IsTracking;" \
                    + "var oldRaRate=sky6RASCOMTele.dRaTrackingRate;" \
                    + "var oldDecRate=sky6RASCOMTele.dDecTrackingRate;" \
                    + f'sky6RASCOMTele.SlewToAzAlt({az},{alt},\"\");' \
                    + "sky6RASCOMTele.SetTracking(wasTracking,1,oldRaRate,oldDecRate);" 
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Slew completed')
            time.sleep(self.postSlewPause)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isSlewComplete(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "Out=sky6RASCOMTele.IsSlewComplete;" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            if skyXparts[0] == '0':
                result = False
            elif skyXparts[0] == '1':
                result = True
            else:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)                
            retInfo =  result
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def abortSlew(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "sky6RASCOMTele.Abort();" 
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getRaDec(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            return_ra: float = 0
            return_dec: float = 0
            command = ''\
                    + "sky6RASCOMTele.GetRaDec();" \
                    + "var Out=sky6RASCOMTele.dRa + '|' + sky6RASCOMTele.dDec;" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            return_ra = float(skyXparts[0])
            return_dec = float(skyXparts[1])
            retInfo = return_ra, return_dec
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getAltAz(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            return_alt: float = 0
            return_az: float = 0
            command = ''\
                    + "sky6RASCOMTele.GetAzAlt();" \
                    + "var Out=sky6RASCOMTele.dAlt + '|' + sky6RASCOMTele.dAz;" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            return_alt = float(skyXparts[0])
            return_az = float(skyXparts[1])
            retInfo = return_alt, return_az
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setTracking(self, tracking: bool):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + f"sky6RASCOMTele.SetTracking({1 if tracking else 0},1,0,0);" 
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isTracking(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "Out=sky6RASCOMTele.isTracking();" 
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Query Parked completed')
            retInfo =  skyXparts[0]
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def jog(self,deltaRa,deltaDec):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            NorS = "N"
            if(deltaDec<0): NorS = "S"
            EorW = "E"
            if(deltaRa<0): EorW = "W"
            command = ''\
                    + "sky6RASCOMTele.Asynchronous = false;"\
                    + f'sky6RASCOMTele.Jog({abs(deltaDec)}, "{NorS}");'\
                    + f'sky6RASCOMTele.Jog({abs(deltaRa )}, "{EorW}");'
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'jog completed')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def jogDec(self,deltaDecMin):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            NorS = "N"
            if(deltaDecMin<0): NorS = "S"
            command = ''\
                    + "sky6RASCOMTele.Asynchronous = false;"\
                    + f'sky6RASCOMTele.Jog({abs(deltaDecMin)}, "{NorS}");'
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'jog completed')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def jogRa(self,deltaRaMin):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            EorW = "E"
            if(deltaRaMin<0): EorW = "W"
            command = ''\
                    + "sky6RASCOMTele.Asynchronous = false;"\
                    + f'sky6RASCOMTele.Jog({abs(deltaRaMin)}, "{EorW}");'
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'jog completed')
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def loadPointingDataSet(self,path,file):
        try:
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),'Enter method')
            self.pointingDataSet = pd.read_excel(path + file,sheet_name='pointingSheet')
            if False and (self.pointingDataSet.shape[0]==0):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def savePointingDataSet(self,path,file):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            with pd.ExcelWriter(path + file) as writer:  
                    self.pointingDataSet.to_excel(writer, index = False, sheet_name='pointingSheet') 
            if 1==0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)


#############################################################################
#
# MainFilter Class
#
class MainFilter:
    def __init__(self):
        self.deviceKind = 'mainFilter'
        #self.filterNdx={'R':0,'G':1,'B':2,'C':3,'L':4,'SII':5,'OIII':6,'Ha':7}
        #self.filterName=['R','G','B','C','L','SII','OIII','Ha']

    #############################################################################
    # Method
    #
    def connect(self):
        if not self.kind == 'OSC':
            try:
                writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
                command = "ccdsoftCamera.filterWheelConnect();"
                skyXcmd(self,command,allowErrors=False)
                retInfo = True
                return retInfo
            except:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                ex_type, ex_value, ex_traceback = sys.exc_info()
                trace_back = traceback.extract_tb(ex_traceback)
                stack_trace = list()
                for trace in trace_back:
                    stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
                writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
                writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
                writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
                raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def disconnect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = "ccdsoftCamera.filterWheelDisconnect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getNumbFilters(self):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        if not self.kind == 'OSC':
            command = ''\
                    + "var temp=ccdsoftCamera.lNumberFilters;" \
                    + "var Out;" \
                    + "Out=temp;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            self.numbFilters= int(skyXparts[0])
        else:
            self.numbFilters= 1
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def getFilterNames(self):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.filterDictFwd =	{}
        self.filterDictRev =	{}
        if not self.kind == 'OSC':
            for ndx in range(self.numbFilters):
                command = ''\
                        + f"var temp=ccdsoftCamera.szFilterName({ndx});" \
                        + "var Out;" \
                        + "Out=temp;"
                skyXresult = skyXcmd(self,command,allowErrors=True)
                skyXparts = skyXresult.split("|")
                self.filterDictFwd[ndx] = skyXparts[0]
                self.filterDictRev[skyXparts[0]] = ndx
        else:
            self.filterDictFwd[0] =	'OSC'
            self.filterDictRev['OSC'] =	0
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def setFilterByNdx(self, filterNdx):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self._selected_filterNdx = filterNdx
            command = f"ccdsoftCamera.FilterIndexZeroBased={filterNdx};"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            if not (int(skyXparts[0]) == filterNdx):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setFilterByName(self, filterName):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            if not self.kind == 'OSC':
                filterNdx = self.filterDictRev[filterName]
                self._selected_filterName = filterName
                self._selected_filterNdx = filterNdx
                command = f"ccdsoftCamera.FilterIndexZeroBased={filterNdx};"
                skyXresult = skyXcmd(self,command,allowErrors=True)
                skyXparts = skyXresult.split("|")
                if not (int(skyXparts[0]) == filterNdx):
                    ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                    writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                    raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# MainCamera Class
#
class MainCamera:
    def __init__(self):
        self.deviceKind = 'mainCamera'
        self.tempTollerance = 0.5
        self.tempProbeTimerSec = 10

    #############################################################################
    # Method
    #
    def connect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = "ccdsoftCamera.Connect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def disconnect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = "ccdsoftCamera.Disconnect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setTempSetPoint(self,cooling_on, target_temperature, waitForTemp, waitTimeMin):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            target_temperature_command = ''
            if cooling_on:
                target_temperature_command = f"ccdsoftCamera.TemperatureSetPoint={target_temperature};"
            command = ''\
                    + f"{target_temperature_command}" \
                    + f"ccdsoftCamera.RegulateTemperature={js_bool(cooling_on)};" \
                    + "ccdsoftCamera.ShutDownTemperatureRegulationOnDisconnect=" \
                    + f"{js_bool(False)};"
            skyXcmd(self,command,allowErrors=False)
            if not(self.getTempSetPoint()==target_temperature):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            if waitForTemp:
                coolerTemp = self.getTemp()
                accumulatedTime=0
                while abs(target_temperature - coolerTemp) > self.tempTollerance:
                    writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'sleeping {self.tempProbeTimerSec:.1f} seconds')
                    time.sleep(self.tempProbeTimerSec)
                    accumulatedTime=accumulatedTime+self.tempProbeTimerSec
                    coolerTemp = self.getTemp()
                    #coolerPower = self.getCoolerPower()
                    # if (coolerPower>90):
                    #     ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                    #     writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                    #     raise Exception(ExcMsg)
                    if (accumulatedTime>waitTimeMin*60):
                        ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                        writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                        raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getTemp(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "var temp=ccdsoftCamera.Temperature;" \
                    + "var Out;" \
                    + "Out=temp;"
            temperature = 0
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            temperature = float(skyXparts[0])
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'GetTemp = {temperature:.1f}C')
            retInfo =  temperature
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getTempSetPoint(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "var temp=ccdsoftCamera.TemperatureSetPoint;" \
                    + "var Out;" \
                    + "Out=temp;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            temperature = float(skyXparts[0])
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'GetTemp = {temperature:.1f}C')
            retInfo =  temperature
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getCoolerPower(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "var power=ccdsoftCamera.ThermalElectricCoolerPower;" \
                    + "var Out;" \
                    + "Out=power;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            coolerPower =  float(skyXparts[0])
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'GetCoolerPower = {coolerPower:.1f}%')
            retInfo = coolerPower
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getAutosavePath(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "var path=ccdsoftCamera.AutoSavePath;" \
                    + "var Out;" \
                    + "Out=path;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'autoSavepath = >{skyXparts[0]}<')
            retInfo =  skyXparts[0]
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def abortImage(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = "ccdsoftCamera.Abort();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    # def saveImageToAutosave(self,objName:str,frameType: str,filter_name: str,exposure: float,binning: int,sequence: int):
    #     writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'saveImageToAutosave')
    #     saveFileName = generateSaveFileName(frameType,temp,objName,filterName,exposure,binning,sequence)
    #     #writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'saveFileName = >{saveFileName}<')
    #     command = ''\
    #             + "cam = ccdsoftCamera;" \
    #             + "img = ccdsoftCameraImage;" \
    #             + "img.AttachToActiveImager();" \
    #             + "var path = ccdsoftCamera.AutoSavePath;" \
    #             + f'img.Path = path + "/" + "{saveFileName}";' \
    #             + "var Out=img.Save();" 
    #     skyXresult = skyXcmd(self,command,allowErrors=True)
    #     return

    #############################################################################
    # Method
    #
    def saveImgToFile(self,directoryPath,frameType,temp,objName,filterName,exposure,binning,sequence):
        try:
            if not os.path.exists(directoryPath):
                writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'Making Folder {directoryPath}')
                os.makedirs(directoryPath)

            saveFileName = generateSaveFileName(frameType,temp,objName,filterName,exposure,binning,sequence)
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'Save {saveFileName}')

            command = ''\
                    + "cam = ccdsoftCamera;" \
                    + "img = ccdsoftCameraImage;" \
                    + "img.AttachToActiveImager();" \
                    + f'var path = "{directoryPath}";' \
                    + f'img.Path = path + "/" + "{saveFileName}";' \
                    + "img.Save();" 
            skyXcmd(self,command,allowErrors=False)
            if not os.path.exists(directoryPath+'/'+saveFileName):
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            self.lastSaveFilePath = directoryPath
            self.lastFileName = saveFileName
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def takeImage(self,frameType, exposure, binning, reductionKind, reductionGrp, autoSaveFile, asyncMode):
        writeLog(True,'',self.deviceKind,currentFuncName(),f'take{frameType}Frame {exposure:.1f}Sec {binning:.1f}x{binning:.1f} autoSaveFile={js_bool(autoSaveFile)}, asyncMode={js_bool(asyncMode)}')
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            self.frameTypeDict={}
            self.frameTypeDict['Light']=1
            self.frameTypeDict['Bias']=2
            self.frameTypeDict['Dark']=3
            self.frameTypeDict['Flat']=4
            
            self.frameReductionDict={}
            self.frameReductionDict['No']=0
            self.frameReductionDict['None']=0
            self.frameReductionDict['Full']=2

            frameTypeNdx = self.frameTypeDict[frameType]
            reductionNdx = self.frameReductionDict[reductionKind]

            command = ''\
                    + "ccdsoftCamera.Autoguider=false;" \
                    + f"ccdsoftCamera.Asynchronous={js_bool(asyncMode)};" \
                    + f"ccdsoftCamera.AutoSaveOn={js_bool(autoSaveFile)};" \
                    + f"ccdsoftCamera.ImageReduction={reductionNdx};" \
                    + f'ccdsoftCamera.ReductionGroupName="{reductionGrp}";' \
                    + "ccdsoftCamera.ToNewWindow=false;" \
                    + "ccdsoftCamera.ccdsoftAutoSaveAs=0;" \
                    + f"ccdsoftCamera.Frame={frameTypeNdx};" \
                    + f"ccdsoftCamera.ExposureTime = {exposure};" \
                    + f"ccdsoftCamera.BinX={binning};" \
                    + f"ccdsoftCamera.BinY={binning};" \
                    + "var cameraResult = ccdsoftCamera.TakeImage();"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            assert (len(skyXparts) > 0)
            if skyXparts[0] == "0":
                pass  # Result indicates success
            else:
                pass
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def isComplete(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    +'ccdsoftCamera.IsExposureComplete;'
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")

            if skyXparts[0] == '0':
                retInfo = False
            elif skyXparts[0] == '1':
                retInfo = True
            else:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)                
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    def getExpStatus(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    +'ccdsoftCamera.ExposureStatus;'
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            retInfo = skyXparts[0]
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getImgAvgADU(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    +'ccdsoftCameraImage.AttachToActive();'\
                    +'var averageAdu = ccdsoftCameraImage.averagePixelValue();'\
                    +'var Out;'\
                    +'Out=averageAdu;'
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            retInfo =  skyXparts[0]
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getInventory(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    +"var CSAGI=ccdsoftCameraImage;"\
                    +"CSAGI.AttachToActiveImager();"\
                    +"CSAGI.ShowInventory();"\
                    +"var FWHM=CSAGI.InventoryArray(4);"\
                    +"var counter=FWHM.length;"\
                    +"var path=CSAGI.Path;"\
                    +"var fwhm=FWHM[0];"\
                    +'var Out="";'\
                    +'Out+=counter+"|";'\
                    +'Out+=fwhm+"|";'\
                    +'Out+=path;'\
                    +'Out+="";'
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            retInfo = {}
            retInfo['count'] = int(skyXparts[0])
            retInfo['FWHM'] = float(skyXparts[1])
            retInfo['path'] = skyXparts[2]
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# Guider Class
#
class Guider:
    def __init__(self):
        self.deviceKind = 'Guider'
        self.postSlewPause = 2

    #############################################################################
    # Method
    #
    def connect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftAutoguider.Connect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def disconnect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftAutoguider.Disconnect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def setExposure(self,exp):
        writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
        self.exp = exp
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def takeImage(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
            +"ccdsoftAutoguider.Asynchronous = false;"\
            +"ccdsoftAutoguider.Frame = 1;"\
            +"ccdsoftAutoguider.Delay = 0;"\
            +"ccdsoftAutoguider.Subframe = false;"\
            +"ccdsoftAutoguider.ExposureTime = " + str(self.exp) + ";"  \
            +"ccdsoftAutoguider.AutoSaveOn = true;"\
            +"ccdsoftAutoguider.TakeImage();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def findStar(self ):
       try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
            +"function median(values){values.sort(function(a,b){return a - b;});"\
                +"var half=Math.floor(values.length/2);"\
                +"if(values.length%2){return values[half];}"\
                +"else{return(values[half-1]+values[half])/2.0;}}"\
            +"var CSAGI=ccdsoftAutoguiderImage;"\
            +"CSAGI.AttachToActiveAutoguider();"\
            +"CSAGI.ShowInventory();"\
            +"var X=CSAGI.InventoryArray(0);"\
            +"var Y=CSAGI.InventoryArray(1);"\
            +"var Mag=CSAGI.InventoryArray(2);"\
            +"var Class=CSAGI.InventoryArray(3);"\
            +"var FWHM=CSAGI.InventoryArray(4);"\
            +"var AImage=CSAGI.InventoryArray(5);"\
            +"var BImage=CSAGI.InventoryArray(6);"\
            +"var Theta=CSAGI.InventoryArray(7);"\
            +"var Elong=CSAGI.InventoryArray(8);"\
            +"var disposableX=CSAGI.InventoryArray(0);"\
            +"var disposableY=CSAGI.InventoryArray(1);"\
            +"var disposableMag=CSAGI.InventoryArray(2);"\
            +"var disposableFWHM=CSAGI.InventoryArray(4);"\
            +"var disposableElong=CSAGI.InventoryArray(8);"\
            +"var Width=CSAGI.WidthInPixels;"\
            +"var Height=CSAGI.HeightInPixels;"\
            +"var strResult='';"\
            +"var Brightest=0;"\
            +"var newX=0;"\
            +"var newY=0;"\
            +"var counter=X.length;"\
            +"var medFWHM=median(disposableFWHM);"\
            +"var medMag=median(disposableMag);"\
            +"var medElong=median(disposableElong);"\
            +"var baseMag=medMag;"\
            +"var path='Nothing';"\
            +"median(disposableX);"\
            +"median(disposableY);"\
            +"X.push(0);"\
            +"Y.push(0);"\
            +"X.push(Width);"\
            +"Y.push(Height);"\
            +"Mag.push(medMag,medMag);"\
            +"for(ls=0;ls<counter;++ls){"\
                +"if(((X[ls]>30&&X[ls]<(Width-30)))&&(Y[ls]>30&&Y[ls]<(Height-30))){"\
                    +"if((Elong[ls]<medElong*2.5)&&(Mag[ls]<(medMag))){"\
                        +"if(FWHM[ls]<(medFWHM*3)&&(FWHM[ls]>1)){"\
                            +"var highNeighborX=disposableX[disposableX.indexOf(X[ls])+1];"\
                            +"var lowNeighborX=disposableX[disposableX.indexOf(X[ls])-1];"\
                            +"var highNeighborY=disposableY[disposableY.indexOf(Y[ls])+1];"\
                            +"var lowNeighborY=disposableY[disposableY.indexOf(Y[ls])-1];"\
                            +"if(!highNeighborY)highNeighborY=Height;"\
                            +"if(!lowNeighborY)lowNeighborY=0;"\
                            +"if(!highNeighborX)highNeighborX=Width;"\
                            +"if(!lowNeighborX)lowNeighborX=0;"\
                            +"var highNeighborXLS=X.indexOf(highNeighborX);"\
                            +"var lowNeighborXLS=X.indexOf(lowNeighborX);"\
                            +"var highNeighborYLS=Y.indexOf(highNeighborY);"\
                            +"var lowNeighborYLS=Y.indexOf(lowNeighborY);"\
                            +"if(((X[highNeighborXLS]-X[ls])>20)||(((Y[highNeighborXLS]-Y[ls])>20)&&((Y[ls]-Y[highNeighborXLS])>20))||(Mag[highNeighborXLS]>((Mag[ls]+medMag)/1.75))){"\
                                +"if(((X[ls]-X[lowNeighborXLS])>20)||(((Y[lowNeighborXLS]-Y[ls])>20)&&((Y[ls]-Y[lowNeighborXLS])>20))||(Mag[lowNeighborXLS]>((Mag[ls]+medMag)/1.75))){"\
                                    +"if(((Y[highNeighborYLS]-Y[ls])>20)||(((X[highNeighborYLS]-X[ls])>20)&&((X[ls]-X[highNeighborYLS])>20))||(Mag[lowNeighborYLS]>((Mag[ls]+medMag)/1.75))){"\
                                        +"if(((Y[ls]-Y[lowNeighborYLS])>20)||(((X[lowNeighborYLS]-X[ls])>20)&&((X[ls]-X[lowNeighborYLS])>20))||(Mag[lowNeighborYLS]>((Mag[ls]+medMag)/1.75))){"\
                                            +"if(Mag[ls]<baseMag){baseMag=Mag[ls];Brightest=ls;"\
                                            +"}"\
                                        +"}"\
                                    +"}"\
                                +"}"\
                            +"}"\
                        +"}"\
                    +"}"\
                +"}"\
            +"}"\
            +"if((ccdsoftAutoguider.ImageUseDigitizedSkySurvey=='1')&&(CSAGI.FITSKeyword('XBINNING')=='1')){newY =(Height-Y[Brightest]);}"\
            +"else{newY=Y[Brightest];}"\
            +"newX=X[Brightest];"\
            +"newX=newX.toFixed(2);"\
            +"newY=newY.toFixed(2);"\
            +"Mag[Brightest]=Mag[Brightest].toFixed(2);"\
            +"newMedMag=medMag.toFixed(2);"\
            +"path=CSAGI.Path;"\
            +"strResult+= newX + '|' + newY + '|(X,Y)';"\
            +"strResult+='Mag='+Mag[Brightest]+',';"\
            +"strResult+='MedMag='+newMedMag+',';"\
            +"strResult+='FWHM='+FWHM[Brightest]+',';"\
            +"strResult+='MedFWHM='+medFWHM+',';"\
            +"strResult+='TtlLgtSrcs='+counter+';';"\
            +"strResult+='Path='+path;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            #print(result)
            skyXparts = skyXresult.split("|")
            #print(data2[0],data2[1])
            self.starX = skyXparts[0]
            self.starY = skyXparts[1]
            if not (self.starY=='0.00') and not(self.starY=='0.00'):
                retInfo = True
            else:
                retInfo = False
            return retInfo
       except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def start(self ):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = '' \
            +"ccdsoftAutoguider.GuideStarX = " + str(self.starX) + ";"\
            +"ccdsoftAutoguider.GuideStarY = " + str(self.starY) + ";"\
            +"ccdsoftAutoguider.AutoguiderExposureTime = " + str(self.exp) + ";"\
            +"ccdsoftAutoguider.AutoSaveOn = true;"\
            +"ccdsoftAutoguider.Subframe = true;"\
            +"ccdsoftAutoguider.Delay = 0;"\
            +"ccdsoftAutoguider.Frame = 1;"\
            +"ccdsoftAutoguider.Asynchronous = true;"\
            +"ccdsoftAutoguider.Autoguide();"
            skyXcmd(self,command,allowErrors=False)
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Wait 3 seconds for guider to settle')
            time.sleep(3)
            #############################################################################
            # FEATURE ADD:
            #   * Measure a good start
            #
            if True:
                retInfo = True
            else:
                retInfo = False
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def stop(self ):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = '' \
            +"ccdsoftAutoguider.Abort();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getError(self ):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = '' \
            +"var errorX = ccdsoftAutoguider.GuideErrorX;"\
            +"var errorY = ccdsoftAutoguider.GuideErrorY;"\
            +"Out = errorX + '|' + errorY;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            #print(result)
            skyXparts = skyXresult.split("|")
            #print(data2[0],data2[1])
            retInfo =  skyXparts[0],skyXparts[1]
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# Focuser Class
#
class Focuser:
    def __init__(self):
        self.deviceKind = 'Focuser'
        self.postSlewPause = 2

    #############################################################################
    # Method
    #
    def setTempCurve(self):
        p=numpy.polyfit(self.mainFocuserDataSet['Temperature'].values, self.mainFocuserDataSet['Step'].values, 1)
        self.p=p
        writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'Intercept={p[1]:.1f} slope={p[0]:.1f}')
        retInfo = True
        return retInfo

    #############################################################################
    # Method
    #
    def connect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftCamera.focConnect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def disconnect(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftCamera.focDisconnect();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getTemp(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "focTemp = ccdsoftCamera.focTemperature;" \
                    + "var Out;" \
                    + "Out=focTemp;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")            
            focTemp = float(skyXparts[0])
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'GetTemp {focTemp:.1f}C')
            retInfo = focTemp
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def getPosition(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "focPos = ccdsoftCamera.focPosition;" \
                    + "var Out;" \
                    + "Out=focPos;"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'GetPosition {int(skyXparts[0]):.1f}')
            retInfo =  int(skyXparts[0])
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def move(self,steps):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            retInfo=True
            if steps>0:
                retInfo = self.moveOut(steps)
            if steps<0:
                retInfo = self.moveIn(-steps)
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def moveIn(self,steps):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftCamera.Asynchronous=false;"\
                    + f"ccdsoftCamera.focMoveIn({steps});"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def moveOut(self,steps):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftCamera.Asynchronous=false;"\
                    + f"ccdsoftCamera.focMoveOut({steps});"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def moveTo(self,step):
        try:
            if (-1<step) and (step<self.positionMax) :
                isAt = self.getPosition()
                delta = int(step - isAt)
                if delta > 0:
                    writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'Move out {delta:.1f} from {isAt:.1f} to {step:.1f}')
                    self.moveOut(delta)
                elif delta < 0:
                    writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'Move in {-delta:.1f} from {isAt:.1f} to {step:.1f}')
                    self.moveIn(-delta)
                else:
                    writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'No move required from {isAt:.1f}')
            else:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def focus2(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.BinX=1;" \
                    + "ccdsoftCamera.BinY=1;" \
                    + "ccdsoftCamera.Asynchronous=false;"\
                    + "ccdsoftCamera.AtFocus2();"
            skyXresult = skyXcmd(self,command,allowErrors=True)
            skyXparts = skyXresult.split("|")
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),f'skyXparts[0]={skyXparts[0]}')
            if(skyXparts[0] == 'TypeError: @Focus diverged.  Error = 7001.|No error. Error = 0.'):
                writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Focus failed')
                retInfo = False
            else:              
                writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'Focus passed {self.getTemp():.1f},{self.getPosition():.1f}')
                retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def focus3(self):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            command = ''\
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.BinX=1;" \
                    + "ccdsoftCamera.BinY=1;" \
                    + "ccdsoftCamera.Asynchronous=false;"\
                    + "ccdsoftCamera.AtFocus3();"
            skyXcmd(self,command,allowErrors=False)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def loadFocuserDataSet(self,path,file):
        try:
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),'Enter method')
            self.mainFocuserDataSet = pd.read_excel(path + file,sheet_name='focuserSheet')
            if self.mainFocuserDataSet.shape[0]==0:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def saveFocuserDataSet(self,path,file):
        try:
            writeLog(self.verboseLevel>1,'',self.deviceKind,currentFuncName(),'Enter method')
            with pd.ExcelWriter(path + file) as writer:  
                    self.mainFocuserDataSet.to_excel(writer, index = False, sheet_name='focuserSheet') 
            if 1==0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
                raise Exception(ExcMsg)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

    #############################################################################
    # Method
    #
    def moveToTempCurve(self):
        try:
            temp = self.getTemp()
            step = int(self.p[1]+self.p[0]*temp)
            writeLog(self.verboseLevel>0,'',self.deviceKind,currentFuncName(),f'Curve({temp:.1f}C) = {step:.1f} ')
            self.moveTo(step)
            retInfo = True
            return retInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',self.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',self.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)

#############################################################################
#
# Helpers
#

#############################################################################
# Method
#
def deltaTimeTohms(timedelta):
    # arbitrary number of seconds
    s = timedelta.sec
    # hours
    hours = s // 3600
    # remaining seconds
    s = s - (hours * 3600)
    # minutes
    minutes = s // 60
    # remaining seconds
    seconds = s - (minutes * 60)
    # total time
    return ptos('{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))).strip()

#############################################################################
# Method
#
def ptos(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

#############################################################################
# Method
#
def serialSend(foo,cmd):
    writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'Sending command '+cmd)
    time.sleep(foo.serialPortPaceDelay)
    foo.serPort.write(bytes(cmd+'\n','utf8'))
    writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    SENT : >'+cmd+'<')
    time.sleep(foo.serialPortPaceDelay)
    foo.responce=foo.serPort.readline().decode('utf8').strip()
    writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    RXED : >'+foo.responce+'<')
    time.sleep(foo.serialPortPaceDelay)
    return foo.responce

#############################################################################
# Method
#
def serialExpect(foo,cmd,expect):
    writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'Sending command '+cmd)
    time.sleep(foo.serialPortPaceDelay)
    foo.serPort.write(bytes(cmd+'\n','utf8'))
    writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    SENT : >'+cmd+'<')
    time.sleep(foo.serialPortPaceDelay)
    foo.responce=foo.serPort.readline().decode('utf8').strip()
    writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    RXED : >'+foo.responce+'<')
    time.sleep(foo.serialPortPaceDelay)
    if foo.responce==expect:
        retInfo = True
        return retInfo
    else:
        writeLog(foo.verboseLevel,'',foo.deviceKind,currentFuncName(),ptos('    ',cmd+' FAILED expected >'+expect+'< got >'+foo.responce+'<').strip())
        retInfo = False
        return retInfo

#############################################################################
# Method
#
def skyXcmd(foo,command: str,allowErrors):
    command_packet = "/* Java Script */" \
                     + "/* Socket Start Packet */" \
                     + command \
                     + "/* Socket End Packet */"
    result = skyXsndPkt(foo,command_packet)
    if not allowErrors:
        if not skyXchkIsOk(result):
            ExcMsg="Exception in " + foo.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',foo.deviceKind,currentFuncName(),ExcMsg)
            writeLog(True,'',foo.deviceKind,currentFuncName(),command_packet)
            writeLog(True,'',foo.deviceKind,currentFuncName(),result)
            raise Exception(ExcMsg)            
    return result

#############################################################################
# Method
#
def skyXsndPkt(foo,command_packet: str):
    result = ''
    address_tuple = ('127.0.0.1', 3040)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as the_socket:
        try:
            the_socket.connect(address_tuple)
            bytes_to_send = bytes(command_packet, 'utf-8')
            writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    SENT : >'+command_packet+'<')
            the_socket.sendall(bytes_to_send)
            writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    socket.sendall returned, calling socket.recv')
            returned_bytes = the_socket.recv(1024)
            result = returned_bytes.decode('utf=8')
            writeLog(foo.debugCommLevel,'',foo.deviceKind,currentFuncName(),'    RXED : >'+result+'<')
        except:
            ExcMsg="Exception in " + foo.deviceKind + " unexpected error in "+currentFuncName()
            writeLog(True,'',foo.deviceKind,currentFuncName(),ExcMsg)
            ex_type, ex_value, ex_traceback = sys.exc_info()
            trace_back = traceback.extract_tb(ex_traceback)
            stack_trace = list()
            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            writeLog(True,'',foo.deviceKind,currentFuncName(),f'Exception type : {ex_type.__name__}')
            writeLog(True,'',foo.deviceKind,currentFuncName(),f'Exception message : {ex_value}')
            writeLog(True,'',foo.deviceKind,currentFuncName(),f'Stack trace : {stack_trace}')
            raise Exception(ExcMsg)
    time.sleep(foo.theSkyXPaceDelay)
    return result

#############################################################################
# Method
#
def skyXchkIsOk(result: str):
    ''"Check for TheSkyX errors that are encoded in the return value string''"
    success = False
    if '0|No error. Error = 0.' in result :
        success = True
    elif 'undefined|No error. Error = 0.' in result :
        success = True    
    elif 'false|No error. Error = 0.' in result :
        success = True
    return success
    
#############################################################################
# Method
#
def js_bool(value: bool):
    return "true" if value else "false"

#############################################################################
# Method
#
def getProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    retInfo = False
    return retInfo


#############################################################################
# Method
#
def checkIfProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                retInfo = True
                return retInfo
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    retInfo = False
    return retInfo

#############################################################################
# Method
#
def generateSaveFileName(frameType,temp,objName,filterName,exposure,binning,sequence):
    dateStamp = Time.now().strftime("%Y%m%d-%H%M%S")
    saveFileName = f'{frameType} {int(temp)}C {objName} {filterName} {exposure}s {binning}bin #{sequence:03d} {dateStamp}.fit'
    return saveFileName

