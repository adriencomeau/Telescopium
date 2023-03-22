import datetime
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

from Validators import Validators

# from astropy.coordinates import FK5
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

filePathLog = '.'

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
        self.debugLevl = False
        self.debugCommLevel = False
        self.paceDelay = 1

        self.currentState = 'PreCheck';


    def getTelescopiumMainControl(self) -> (dict):
        telescopiumMainControl = {}
        #############################################################################
        # debug Level Control
        telescopiumMainControl['debugLevel']            = True      # (True) True to log debugging information
        telescopiumMainControl['debugCommLevel']        = False     # (False) True to log serial traffic

        #############################################################################
        # Serial port pacing
        telescopiumMainControl['serialPortPaceDelay']   = 0.1       # (0.1) 0.1 sec pause between serial port commends

        #############################################################################
        # Application suport
        telescopiumMainControl['getNewInstance']        = True      # (True) Get new instances of apps (Cheese/SkyX etc)

        telescopiumMainControl['sleepForAllOff']        = 30        # (30)
        telescopiumMainControl['sleepForAllOn']         = 10        # (10)
        telescopiumMainControl['sleepForMount']         = 10        # (10)
        telescopiumMainControl['sleepAtLoopEnd']        = 2        # (10)

        #############################################################################
        # Run Control
        telescopiumMainControl['normalScheduling']      = True      # (True) True to have telescopium use real night times
        telescopiumMainControl['manualObservation']     = False     # (False) not used

        telescopiumMainControl['justPowerOn']           = False     # (False)
        telescopiumMainControl['leavePowerOn']          = False     # (False)
        telescopiumMainControl['leaveOpen']             = False     # (False)
        telescopiumMainControl['leaveLightOn']          = True      # (True)
        telescopiumMainControl['allowOpenInBadWx']      = False     # (False)

        telescopiumMainControl['lookForJobs']           = True      # (True)

        telescopiumMainControl['takeBias']              = False     # (False)
        telescopiumMainControl['forceTakeBias']         = False     # (False)
        telescopiumMainControl['numbBiasExp']           = 50        # (50)

        telescopiumMainControl['sunDownDegrees']        = -18       # (False)
        telescopiumMainControl['moonDownDegrees']       = -5        # (False)

        telescopiumMainControl['takeDarks']             = False     # (False)
        telescopiumMainControl['numbDarkExp']           = 5
        telescopiumMainControl['darkExpRange']          = [300,600,1200]

        telescopiumMainControl['takeFlat']              = False     # (False)
        telescopiumMainControl['flatSpotAltitude']      = 75        # (75)

        #############################################################################
        # Camera Cooler Control
        telescopiumMainControl['deltaTemp']             = 30                # Max delta T
        telescopiumMainControl['a_list']                = [-20,-10,0]       # .
        telescopiumMainControl['b_list']                = [0,0,-10,-20]     # .
        telescopiumMainControl['waitForTemp']           = True

        #############################################################################
        # filter Control
        #telescopiumMainControl['filterKind']            = "OSC"     # ('OSC')

        #############################################################################
        # Focuser Control
        telescopiumMainControl['focStepInt']            = 4610      # (4852)
        telescopiumMainControl['focStepSlope']          = -26.5     # (0)
        telescopiumMainControl['numbDwell']             = 10     # (0)
        telescopiumMainControl['positionMax']           = 9000
        #############################################################################
        # Observatory Location
        telescopiumMainControl['lat']                   = '45d04m57s'
        telescopiumMainControl['lon']                   = '-75d42m33s'

        telescopiumMainControl['homeLocAlt']            = 37.697
        telescopiumMainControl['homeLocAz']             = 219.191

        #############################################################################
        # Avoid Sun, Horizon, Wx threshold
        telescopiumMainControl['minimumSafeToHomeAngle']      = 20
        telescopiumMainControl['usableHorizon']               = 30
        telescopiumMainControl['wxMonitorTempThreshold']      = 14

        #############################################################################
        # Set Com Ports
        if platform.system() == "Linux" :
            telescopiumMainControl['dcPowerSwitchSerialPortStr']    ='/dev/K8090'
            telescopiumMainControl['parkDetectorSerialPortStr']     ='/dev/ParkDetector'
            telescopiumMainControl['wxMonitorSerialPortStr']        ='/dev/WxMonitor'
            telescopiumMainControl['domeControllerSerialPortStr']   ='/dev/DomeController'
            telescopiumMainControl['telescopiumLibraryPath']        = '/home/acomeau/Library/Telescopium/'
            telescopiumMainControl['webCamProc']                    = 'cheese'
            telescopiumMainControl['webCamApp']                     = '/bin/cheese'
            telescopiumMainControl['theSkyProc']                    = 'TheSkyX'
            telescopiumMainControl['theSkyApp']                     = '/home/acomeau/TheSkyX/TheSkyX'
        else :
            telescopiumMainControl['dcPowerSwitchSerialPortStr']    ='COM12'
            telescopiumMainControl['parkDetectorSerialPortStr']     ='COM5'
            telescopiumMainControl['wxMonitorSerialPortStr']        ='COM9'
            telescopiumMainControl['domeControllerSerialPortStr']   ='COM11'
            telescopiumMainControl['telescopiumLibraryPath']        = 'C:/Users/Adrien/Documents/Library/Telescopium/'
            telescopiumMainControl['webCamProc']                    = 'LogitechCamera.exe'
            telescopiumMainControl['webCamApp']                     = 'C:/Program Files (x86)/Common Files/LogiShrd/LogiUCDpp/LogitechCamera.exe'
            telescopiumMainControl['theSkyProc']                    = 'TheSky64.exe'
            telescopiumMainControl['theSkyApp']                     = 'C:/Program Files (x86)/Software Bisque/TheSkyX Professional Edition/TheSky64/TheSky64.exe'


        return telescopiumMainControl

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,self.currentState,self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setObsLocation(self, latIn, lonIn, heightIn) -> ():
        try:
            self.obsLocation = EarthLocation(lat=latIn, lon=lonIn, height=heightIn*u.m)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('obsLocation = lat:%10s lon:%10s '%(self.obsLocation.lat.to_string(), self.obsLocation.lon.to_string())).strip())
            if not((str(self.obsLocation.lat)==latIn)and(str(self.obsLocation.lon)==lonIn)):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setObsLocation"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def loadWorkList(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'loadWorkList')
            #self.workList = pd.read_pickle(self.telescopiumLibraryPath+'WorkList/'+'workList.pkl')
            self.workList = pd.read_excel(self.telescopiumLibraryPath +'workList.ods')
            if self.workList.shape[0]==0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in loadWorkList"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)

    def saveWorkList(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'saveWorkList')
            self.workList.to_excel(self.telescopiumLibraryPath +'workList.ods',index=False)
            return
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in saveWorkList"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)

    def calculateNight(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Calculating upcomming night')
            delta_midnight = np.linspace(-12, 12, 1000)*u.hour
            midnightLocal = Time(datetime.datetime((datetime.datetime.now()+datetime.timedelta(days=1)).year, (datetime.datetime.now()+datetime.timedelta(days=1)).month, (datetime.datetime.now()+datetime.timedelta(days=1)).day, 0, 0, 0))
            utcoffset = -4*u.hour  # Eastern Daylight Time
            midnight = midnightLocal - utcoffset
            times = midnight + delta_midnight
            frames = AltAz(obstime=times, location=self.obsLocation)

            sunaltazs  = get_sun (times).transform_to(frames)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'get sun complete')
            #moonaltazs = get_moon(times).transform_to(frames)

            self.sunSet       = midnight+delta_midnight[sunaltazs.alt.value<0][0]
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('sun set                     ',self.sunSet).strip())

            self.sunSetFlats  = midnight+delta_midnight[sunaltazs.alt.value<1][0]
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('sun set  Flats              ',self.sunSetFlats).strip())

            self.sunSetAstro  = midnight+delta_midnight[sunaltazs.alt.value<self.sunDownDegrees][0]
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('sun set  astro              ',self.sunSetAstro).strip())

            self.sunRiseAstro = midnight+delta_midnight[sunaltazs.alt.value<self.sunDownDegrees][-1]
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('sun rise astro              ',self.sunRiseAstro).strip())

            self.sunRise      = midnight+delta_midnight[sunaltazs.alt.value<0][-1]
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('sun rise                    ',self.sunRise).strip())

            if self.normalScheduling:
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

            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoEnter_PoweredUp       ',self.timetoEnter_PoweredUp).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoEnter_AllConnected    ',self.timetoEnter_AllConnected).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoEnter_ReadyToOpen     ',self.timetoEnter_ReadyToOpen).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoEnter_ReadyToFlats    ',self.timetoEnter_ReadyToFlats).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoEnter_ReadyToObserve  ',self.timetoEnter_ReadyToObserve).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoLeave_ReadyToObserve  ',self.timetoLeave_ReadyToObserve).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoLeave_AllConnected    ',self.timetoLeave_AllConnected).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timetoLeave_PoweredUp       ',self.timetoLeave_PoweredUp).strip())
            if ((self.timetoLeave_PoweredUp-self.timetoEnter_PoweredUp).value)>1:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in calculateNight"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def calculateNight2(self):
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'calculate items over night Night')
            self.midnightLocal = Time(datetime.datetime((datetime.datetime.now()+datetime.timedelta(days=1)).year, (datetime.datetime.now()+datetime.timedelta(days=1)).month, (datetime.datetime.now()+datetime.timedelta(days=1)).day, 0, 0, 0))
            self.utcoffset = -4*u.hour  # Eastern Daylight Time
            self.midnight = self.midnightLocal - self.utcoffset
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'calculate frames over night')
            self.delta_midnight = np.linspace(-12, 12, 1+(24)*4)*u.hour
            self.times = self.midnight + self.delta_midnight
            self.frames = AltAz(obstime=self.times, location=self.obsLocation)


            writeLog(self.debugLevl,self.currentState,self.deviceKind,'calculate sun location over night')
            self.sunaltazs = get_sun(self.times).transform_to(self.frames)

            writeLog(self.debugLevl,self.currentState,self.deviceKind,'calculate moon location over night')
            self.moonaltazs= get_moon(self.times).transform_to(self.frames)

            writeLog(self.debugLevl,self.currentState,self.deviceKind,'calculate sun/moon/joint down times over night')
            self.sunIsDown  = self.sunaltazs.alt.value<self.sunDownDegrees
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'sun is down (below {self.sunDownDegrees}) for {self.sunIsDown.sum()*0.25} hours')
            self.moonIsDown = self.moonaltazs.alt.value<self.moonDownDegrees
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'moon is down (below {self.moonDownDegrees}) for {self.moonIsDown.sum()*0.25} hours')
            self.sunAndMoonAreDown = self.sunIsDown * self.moonIsDown
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'both are down for {self.sunAndMoonAreDown.sum()*0.25} hours')

            self.timesItIsDark = self.times[self.sunAndMoonAreDown]

            makePlots=True
            if makePlots:
                plt.plot(self.delta_midnight, self.sunaltazs.alt, color='r', label='Sun')
                plt.plot(self.delta_midnight, self.moonaltazs.alt, color=[0.75]*3, ls='--', label='Moon')
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(self.sunDownDegrees*u.deg, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

            writeLog(self.debugLevl,self.currentState,self.deviceKind,'calculate all workListItems location over night')
            
            self.workListSkyCoords = SkyCoord(self.workList.skyCoordRaHrsJ2000[:]*u.hour, self.workList.skyCoordDecValJ2000[:]*u.deg, frame='icrs')
            self.workListAltaz = self.workListSkyCoords[:, np.newaxis].transform_to(self.frames[np.newaxis])
            
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'Numb Objects                    {self.workListAltaz.shape[0]}')

            if makePlots:
                plt.plot(self.delta_midnight, self.workListAltaz[:].alt.degree.T, marker='', alpha=0.5)
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(0, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

                plt.plot(self.delta_midnight[self.sunAndMoonAreDown], self.workListAltaz[:,self.sunAndMoonAreDown].alt.degree.T, marker='', alpha=0.5)
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(0*u.deg, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Calculate times each object is observable')

            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'useable horizon is {self.usableHorizon}')

            # Calculate while the sun is down what frames for each object that are above the useable horizon
            self.pointersToAboveHorizon=self.workListAltaz[:,self.sunAndMoonAreDown].alt.degree>self.usableHorizon

            # the usable time is the net sum of time each object is above the horizon
            self.durationAboveHorizon_hrs=(self.pointersToAboveHorizon).sum(axis=1)*0.25
            

            # minimum time is met if time above the horizon exceeds the needed time
            self.pointersToitemsWithEnoughTime = self.durationAboveHorizon_hrs>(self.workList['NetTimeMin']/60)


            self.workListWithEnoughTimeAltaz=self.workListAltaz[self.pointersToitemsWithEnoughTime]

            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'Numb Objects with ehough time   {self.workListWithEnoughTimeAltaz.shape[0]}')

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
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='0.5', zorder=0)
                plt.fill_between(self.delta_midnight, self.sunDownDegrees*u.deg, 90*u.deg, self.sunaltazs.alt < self.sunDownDegrees*u.deg, color='k', zorder=0)
                plt.xlim(-12*u.hour, 12*u.hour)
                plt.xticks((np.arange(13)*2-12)*u.hour)
                plt.ylim(0*u.deg, 90*u.deg)
                plt.xlabel('Hours from EDT Midnight')
                plt.ylabel('Altitude [deg]')
                plt.show()

    def chooseWorkItem(self,mode) -> (bool):
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'chooseWorkItem')
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'measure what where now')
            aa = AltAz(location=self.obsLocation, obstime=Time.now())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'1')

            #for index, row in self.workList.iterrows():
            #    skyCoordJ2000 = SkyCoord.from_name(row.objName)
            #    skyCoordJNow  = skyCoordJ2000.transform_to(FK5(equinox='J2023'))

            #    self.workList.loc[index,'skyCoordRaHrsJ2000'] = skyCoordJ2000.ra.hour
            #    self.workList.loc[index,'skyCoordDecValJ2000'] = skyCoordJ2000.dec.value
            #    self.workList.loc[index,'skyCoordRaHrsJNow'] = skyCoordJNow.ra.hour
            #    self.workList.loc[index,'skyCoordDecValJNow'] = skyCoordJNow.dec.value

            #    workItemSkyCoord = SkyCoord(self.workList.loc[index,'skyCoordRaHrsJNow']*u.hour, self.workList.loc[index,'skyCoordDecValJNow']*u.deg, frame='icrs')

            #    self.workList.loc[index,'altNow'] = workItemSkyCoord.transform_to(aa).alt.value
            #    self.workList.loc[index,'azNow'] = workItemSkyCoord.transform_to(aa).az.value

            #writeLog(self.debugLevl,self.currentState,self.deviceKind,'2')
            #self.workList['testHorizon'] = self.workList['altNow']>self.workList['Horizon']
            #self.workList = self.workList.replace(True,'Above')
            #self.workList = self.workList.replace(False,'Below')
            #self.workList['NetTimeMin'] = 10+self.workList['Exp']*self.workList['Rep']/60



            return

            timeNowUTC                  = Time.now()

            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'{self.workList.shape[0]} items to look over')

            self.workList = self.workList.sort_values('alt',ascending=False)
            print(self.workList)
            asd=self.workList.loc[(self.workList.alt>self.usableHorizon) & (self.workList.done==0)]
            if asd.shape[0]>0:
                rowNdx = asd.index[0]
                self.workItemRowNdx = rowNdx
                writeLog(self.debugLevl,self.currentState,self.deviceKind,f'Found {self.workList.objName[self.workItemRowNdx]} {self.workList.CommonName[self.workItemRowNdx]} in work list at {int(self.workList.alt[self.workItemRowNdx])}deg')
                return True
            else:
                self.workItemRowNdx = float("nan")
                writeLog(self.debugLevl,self.currentState,self.deviceKind,'No work found in work list')
                return False
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in chooseWorkItem"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)


    def startCheese(self,getNewInstance,appProc,appPath) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Start Webcam Monitor')
            subProc = self._startNew(getNewInstance,appProc,appPath)
            self.subProcCheese = subProc
            if not(checkIfProcessRunning(appProc)):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startCheese"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def stopCheese(self,appProc,appPath) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Stopping Webcam Monitor')
            self._stopProc(appProc,appPath)
            if checkIfProcessRunning(appProc):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startCheese"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startTheSkyX(self,getNewInstance,appProc,appPath) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Start TheSkyX')
            subProc = self._startNew(getNewInstance,appProc,appPath)
            self.subProcTheSkyX = subProc
            if not(checkIfProcessRunning(appProc)):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startTheSkyX"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def stopTheSkyX(self,appProc,appPath) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Stopping TheSkyX')
            self._stopProc(appProc,appPath)
            if checkIfProcessRunning(appProc):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startTheSkyX"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def loadFlatExpBlkList(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'loadFlatExpBlkList')
            self.flatExpBlk = pd.read_pickle(self.telescopiumLibraryPath+'/flatExpBlk.pkl')
            return
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in loadFlatExpBlkList"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)

    def startWxMonitor(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'connectWxMonitor')
            self.wxMonitor = WxMonitor()
            self.wxMonitor.setSerialPortStr(telescopiumMainControl['wxMonitorSerialPortStr'])
            self.wxMonitor.setPaceDelay(telescopiumMainControl['serialPortPaceDelay'])
            self.wxMonitor.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.wxMonitor.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.wxMonitor.setTempThreshold(telescopiumMainControl['wxMonitorTempThreshold'])
            self.wxMonitor.openPort()
            self.wxMonitor.checkIdent()
            self.wxMonitorPortOpen = True
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connectWxMonitor"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startDcPowerSwitch(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'connectDcPowerSwitch')
            self.dcPowerSwitch = DCPowerSwitch()
            self.dcPowerSwitch.setSerialPortStr(telescopiumMainControl['dcPowerSwitchSerialPortStr'])
            self.dcPowerSwitch.setPaceDelay(telescopiumMainControl['serialPortPaceDelay'])
            self.dcPowerSwitch.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.dcPowerSwitch.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.dcPowerSwitch.openPort()
            self.dcPowerSwitch.checkIdent()
            self.dcPowerSwitchPortOpen = True
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connectDcPowerSwitch"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setAllSwOff(self,sleepTime) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'setAllSwOff')
            self.dcPowerSwitch.setSwOff(0)
            self.dcPowerSwitch.setSwOff(1)
            self.dcPowerSwitch.setSwOff(2)
            self.dcPowerSwitch.setSwOff(3)
            self.dcPowerSwitch.setSwOff(4)
            self.dcPowerSwitch.setSwOff(5)
            self.dcPowerSwitch.setSwOff(6)
            self.dcPowerSwitch.setSwOff(7)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'Sleep {sleepTime}sec for all to settle')
            time.sleep(sleepTime)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setAllSwOff"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setAllSwOn(self,leaveLightOn,sleepTime) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'setAllSwOn')
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
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'Sleep {sleepTime}sec for all to settle')
            time.sleep(sleepTime)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setAllSwOn"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setPathsForTonight(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'setPaths')
            dateStringForTonight = datetime.datetime.now().strftime("%Y%m%d")
            self.filePathBias    = self.telescopiumLibraryPath + 'Bias/'      + dateStringForTonight
            self.filePathFlats   = self.telescopiumLibraryPath + 'Flats/'     + dateStringForTonight
            self.filePathDarks   = self.telescopiumLibraryPath + 'Darks/'     + dateStringForTonight
            self.filePathLights  = self.telescopiumLibraryPath + 'Lights/'    + dateStringForTonight

            self.filePathBias    = self.telescopiumLibraryPath + dateStringForTonight
            self.filePathFlats   = self.telescopiumLibraryPath + dateStringForTonight
            self.filePathDarks   = self.telescopiumLibraryPath + dateStringForTonight
            self.filePathLights  = self.telescopiumLibraryPath + dateStringForTonight
            global filePathLog
            filePathLog          = self.telescopiumLibraryPath + dateStringForTonight
            return
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in setPsetPathsForTonightaths"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)

    def startDomeController(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'connectDomeController')
            self.domeController = DomeController()
            self.domeController.setSerialPortStr(telescopiumMainControl['domeControllerSerialPortStr'])
            self.domeController.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.domeController.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.domeController.openPort()
            self.domeController.checkIdent()
            self.domeController.Activate=True
            self.domeControllerPortOpen = True
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startDomeController"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startParkDetector(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'connectParkDetector')
            self.parkDetector = ParkDetector()
            self.parkDetector.setSerialPortStr(telescopiumMainControl['parkDetectorSerialPortStr'])
            self.parkDetector.setPaceDelay(telescopiumMainControl['serialPortPaceDelay'])
            self.parkDetector.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.parkDetector.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.parkDetector.openPort()
            self.parkDetector.checkIdent()
            self.parkDetectorPortOpen = True
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f"sleep {telescopiumMainControl['sleepForMount']}sec for Mount to power up")
            self.sleep(telescopiumMainControl['sleepForMount'])
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startParkDetector"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startMount(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'startMount')
            self.telescopeMount = Mount()
            self.telescopeMount.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.telescopeMount.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.telescopeMount.connectAndDoNotUnpark()
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startMount"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startMainCamera(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'startMainCamera')
            self.mainCamera = MainCamera()
            self.mainCamera.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.mainCamera.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.mainCamera.connect()
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startMainCamera"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


    def startMainFilter(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'startMainFilter')
            self.mainFilter = MainFilter()
            self.mainFilter.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.mainFilter.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])     
            
            command = ""\
                    + "var temp=SelectedHardware.filterWheelModel;" \
                    + "var Out;" \
                    + "Out=temp+\"\\n\";"
            (success, result, message) = skyXsendCndWithReturn(self.mainFilter,command)

            print(result)
            if 'No Filter Wheel Selected' in result:
                self.mainFilter.kind = 'OSC'
            else:
                self.mainFilter.kind = 'FilterWheel'  
            print(self.mainFilter.kind)
                              
            self.mainFilter.connect()
            self.mainFilter.getNumbFilters()
            self.mainFilter.getFilterNames()            
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startMainFilter"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startFocuser(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'startFocuser')
            self.focuser = Focuser()
            self.focuser.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.focuser.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.focuser.numbDwell = telescopiumMainControl['numbDwell']
            self.focuser.setTempCurve(telescopiumMainControl['focStepInt'],telescopiumMainControl['focStepSlope'])
            self.focuser.connect()
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startFocuser"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def startGuider(self,telescopiumMainControl) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'startGuider')
            self.guider = Guider()
            self.guider.setDebugLevel(telescopiumMainControl['debugLevel'])
            self.guider.setDebugCommLevel(telescopiumMainControl['debugCommLevel'])
            self.guider.connect()
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in startGuider"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def plateSolve(self) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'solveWCS')
        try:
            self.imageScale=0.78
            command = ""\
                    + f'ImageLink.pathToFITS = "{self.mainCamera.lastSaveFilePath}/{self.mainCamera.lastFileName}";' \
                    + f"ImageLink.scale = {self.imageScale};" \
                    + "ImageLink.execute();" \
                    + "var Out=ImageLinkResults.errorCode;" \
                    + "Out += '/' + ImageLinkResults.succeeded;" \
                    + "Out += '/' + ImageLinkResults.searchAborted;" \
                    + "Out += '/' + ImageLinkResults.errorText;" \
                    + "Out += '/' + ImageLinkResults.imageScale;" \
                    + "Out += '/' + ImageLinkResults.imagePositionAngle;" \
                    + "Out += '/' + ImageLinkResults.imageCenterRAJ2000;" \
                    + "Out += '/' + ImageLinkResults.imageCenterDecJ2000;" \
                    + "Out += '/' + ImageLinkResults.imageFWHMInArcSeconds;" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            #writeLog(self.debugLevl,"",self.deviceKind,returned_value)
            parts = returned_value.split("/")
            returnInfo = {}
            returnInfo['errorCode'] = (parts[0])
            returnInfo['succeeded'] = (parts[1])
            returnInfo['searchAborted'] = (parts[2])
            returnInfo['errorText'] = (parts[3])
            returnInfo['imageScale'] = float(parts[4])
            returnInfo['imagePositionAngle'] = float(parts[5])
            returnInfo['imageCenterRAJ2000'] = float(parts[6])
            returnInfo['imageCenterDecJ2000'] = float(parts[7])
            returnInfo['imageFWHMInArcSeconds'] = float(parts[8])
            return returnInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in solveWCS"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def plateSolve2(self) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'solveWCS')
        try:
            self.imageScale=0.78
            command = ""\
                    + "img = ccdsoftCameraImage;" \
                    + f'img.Path = "{self.mainCamera.lastSaveFilePath}/{self.mainCamera.lastFileName}";' \
                    + 'img.Open();' \
                    + 'img.ScaleInArcsecondsPerPixel=0.78;' \
                    + 'img.InsertWCS();' \
                    + 'img.Save();' \
                    + 'img.Close();' \
                    + "var Out=12;" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            #writeLog(self.debugLevl,"",self.deviceKind,returned_value)
            parts = returned_value.split("/")
            returnInfo = {}
            # returnInfo['errorCode'] = (parts[0])
            # returnInfo['succeeded'] = (parts[1])
            # returnInfo['searchAborted'] = (parts[2])
            # returnInfo['errorText'] = (parts[3])
            # returnInfo['imageScale'] = float(parts[4])
            # returnInfo['imagePositionAngle'] = float(parts[5])
            # returnInfo['imageCenterRAJ2000'] = float(parts[6])
            # returnInfo['imageCenterDecJ2000'] = float(parts[7])
            # returnInfo['imageFWHMInArcSeconds'] = float(parts[8])
            return returnInfo
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in solveWCS"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setCameraTempTarget(self,deltaTemp,a_list,b_list) -> ():
        try:
            self.tempSetPointForTonight=([item for item in a_list if item >= (self.wxMonitor.getAmbTemp()-deltaTemp)])
            self.tempSetPointForTonight=b_list[len(self.tempSetPointForTonight)]
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Amb %5.1f, MinSetPoint %5.1f, Selected SetPt %5.1f '%(self.wxMonitor.getAmbTemp(),self.wxMonitor.getAmbTemp()-deltaTemp,self.tempSetPointForTonight)).strip())
            if (self.tempSetPointForTonight<-20) or (self.tempSetPointForTonight>0):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setCameraTempTarget"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isSafeToHome(self) -> (bool):
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Checking if safeToHome')
            timeNowUTC = Time.now()
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('timeNowUT  =',timeNowUTC).strip())
            self.mountHome = AltAz(alt=self.homeLocAlt*u.deg,az=self.homeLocAz*u.deg,obstime=timeNowUTC, location=self.obsLocation)
            self.mountHome = self.mountHome.transform_to(ICRS())
            self.mountHome = SkyCoord(self.mountHome.ra.value, self.mountHome.dec.value, frame='icrs', unit='deg')
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Mx Home    =',self.mountHome.to_string('hmsdms')).strip())
            sun=get_sun(timeNowUTC)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Sun        =',sun.to_string('hmsdms')).strip())
            self.k=sun.separation(self.mountHome).deg
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Seperation = %6.2f'%(self.k)).strip())
            safeToHome = self.k > self.minimumSafeToHomeAngle
            return safeToHome
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isSafeToHome"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def calculateFlatSkyLoc(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Calculating flat skyLoc')

            timeNowUTC = Time.now()
            frames = AltAz(obstime=timeNowUTC, location=self.obsLocation)
            sun  = get_sun (timeNowUTC)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Sun  (RaDec)=',sun.to_string('hmsdms')).strip())

            sunAzAlt  = get_sun (timeNowUTC).transform_to(frames)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Sun  (AzAlt)=',sunAzAlt.to_string('hmsdms')).strip())

            self.flatSpot = AltAz(alt=self.flatSpotAltitude*u.deg,az=(sunAzAlt.az.value+180)*u.deg,obstime=timeNowUTC, location=self.obsLocation)
            self.flatSpot = self.flatSpot.transform_to(ICRS())
            self.flatSpot = SkyCoord(self.flatSpot.ra.value, self.flatSpot.dec.value, frame='icrs', unit='deg')

            flatSpotAzAlt  = self.flatSpot.transform_to(frames)
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Flat (AzAlt)=',flatSpotAzAlt.to_string('hmsdms')).strip())
            writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Flat (RaDec)=',self.flatSpot.to_string('hmsdms')).strip())
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in calculateFlatSkyLoc"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def slewToFlat(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Slew to flat skyLoc')
            self.telescopeMount.slew(self.flatSpot.ra.hour,self.flatSpot.dec.value)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in slewToFlat"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def runFocus(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'runFocus')
            self.focuser.meanFocusPosition = 0
            for sequenceNdx in range(self.focuser.numbDwell):
                self.focuser.moveToTempCurve()
                self.focuser.focus2()

                self.loadFocuserDataSet()
                self.focuserDataSet.loc[len(self.focuserDataSet)] = {'DateTime':Time.now(), 'Temperature':self.focuser.getTemp(), 'Step':self.focuser.getPosition()}
                self.saveFocuserDataSet()

                p=numpy.polyfit(self.focuserDataSet['Temperature'].values, self.focuserDataSet['Step'].values, 1)
                self.focuser.setTempCurve(p[1],p[0])
                self.focuser.meanFocusPosition += self.focuser.getPosition()/self.focuser.numbDwell
            self.focuser.moveTo(self.focuser.meanFocusPosition)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in runFocus"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def pointingCorrection(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'pointingCorrection')
            frameType       = 'Light'
            temp            = int(self.mainCamera.getTempSetPoint())
            objName         = self.workList.loc[self.workItemRowNdx].objName+'PointingExp'
            filterName      = 'OSC'
            exposure        = 10
            binning         = 2
            imageReduction  = 0
            sequence        = 0
            autoSaveFile    = False
            asyncMode       = False

            self.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)
            self.mainCamera.saveImgToFile(self.filePathLights,frameType,temp,objName,filterName,exposure,binning,sequence)
            returnInfo=self.plateSolve()
            actualRaHrs  = returnInfo['imageCenterRAJ2000']
            actualDecVal = returnInfo['imageCenterDecJ2000']

            deltaRaMin   = (actualRaHrs -self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000 )*60*(360/24)*math.cos(returnInfo['imageCenterDecJ2000']*math.pi/180.0)
            deltaDecMin  = (actualDecVal-self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000)*60
            writeLog(True,self.currentState,'',f'{self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000},{actualRaHrs},{deltaRaMin}')
            writeLog(True,self.currentState,'',f'{self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000},{actualDecVal},{deltaDecMin}')

            self.telescopeMount.jogRa(-deltaRaMin)
            self.telescopeMount.jogDec(-deltaDecMin)

            sequence        = 1
            self.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)
            self.mainCamera.saveImgToFile(self.filePathLights,frameType,temp,objName,filterName,exposure,binning,sequence)
            returnInfo=self.plateSolve()
            actualRaHrs  = returnInfo['imageCenterRAJ2000']
            actualDecVal = returnInfo['imageCenterDecJ2000']
            deltaRaMin   = (actualRaHrs -self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000 )*60*(360/24)*math.cos(returnInfo['imageCenterDecJ2000']*math.pi/180.0)
            deltaDecMin  = (actualDecVal-self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000)*60
            writeLog(True,self.currentState,'',f'{self.workList.loc[self.workItemRowNdx].skyCoordRaHrsJ2000},{actualRaHrs},{deltaRaMin}')
            writeLog(True,self.currentState,'',f'{self.workList.loc[self.workItemRowNdx].skyCoordDecValJ2000},{actualDecVal},{deltaDecMin}')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in pointingCorrection"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def dither(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'dither')
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
            writeLog(self.debugLevl,self.currentState,self.deviceKind,f'{60*DitherXarcMin}"{NorS} {60*DitherYarcMin}"{EorW}')
            self.telescopeMount.jog(DitherXarcMin, NorS, DitherYarcMin, EorW)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in dither"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def loadFocuserDataSet(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'loadFocuserDataSet')
            self.focuserDataSet = pd.read_excel(self.telescopiumLibraryPath +'focuserDataSet.ods')
            if self.focuserDataSet.shape[0]==0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in loadFocuserDataSet"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)


    def saveFocuserDataSet(self) -> ():
        try:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'saveFocuserDataSet')
            self.focuserDataSet.to_excel(self.telescopiumLibraryPath +'focuserDataSet.ods',index=False)
            if 1==0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in saveFocuserDataSet"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)

    def sleep(self,sleepTimeSec) -> ():
        writeLog(self.debugLevl,self.currentState,self.deviceKind,f'Sleeping {sleepTimeSec}')
        time.sleep(sleepTimeSec)
        return

    def closePorts(self) -> ():
        if self.wxMonitorPortOpen:
            writeLog(self.debugLevl,self.currentState,'','Close serial port to Wx Monitor')
            self.wxMonitor.closePort()
        if self.dcPowerSwitchPortOpen:
            writeLog(self.debugLevl,self.currentState,'','Close serial port to DC power switch')
            self.dcPowerSwitch.closePort()
        if self.domeControllerPortOpen:
            writeLog(self.debugLevl,self.currentState,'','Closing Dome Controller')
            self.domeController.closePort()
        if self.parkDetectorPortOpen:
            writeLog(self.debugLevl,self.currentState,'','Closing Park Detector')
            self.parkDetector.closePort()
        return

    def _startNew(self,getNewInstance,procName,cmdStr):
        writeLog(self.debugLevl,self.currentState,self.deviceKind,procName+' testing if running')
        if checkIfProcessRunning(procName):
            writeLog(self.debugLevl,self.currentState,self.deviceKind,procName+' was running')
            if(getNewInstance):
                writeLog(self.debugLevl,self.currentState,self.deviceKind,'Terminating '+procName)
                theskyXProc = getProcessRunning(procName)
                theskyXProc.terminate()
                theskyXProc.wait()
                time.sleep(10)
                if checkIfProcessRunning(procName):
                    writeLog(self.debugLevl,self.currentState,self.deviceKind,'Could not terminate '+procName)
                    raise Exception('Could not terminate '+procName)
                    subProc = 0
                else:
                    writeLog(self.debugLevl,self.currentState,self.deviceKind,'Starting New '+procName)
                    if platform.system() == "Linux" :
                        subProc = subprocess.Popen(cmdStr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else :
                        subProc = subprocess.Popen(cmdStr)
                    time.sleep(10)
            else:
                writeLog(self.debugLevl,self.currentState,self.deviceKind,procName+' did not need to make another')
        else:
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Was not running, starting new instance'+procName)
            if platform.system() == "Linux" :
                subProc = subprocess.Popen(cmdStr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else :
                subProc = subprocess.Popen(cmdStr)
            time.sleep(10)
        writeLog(self.debugLevl,self.currentState,self.deviceKind,procName+' returning')
        subProc=getProcessRunning(procName)
        #if not(checkIfProcessRunning(procName)):
        #    writeLog(self.debugLevl,self.currentState,self.deviceKind,'Could not start '+procName)
        #    raise Exception('Could not start '+procName)
        #    subProc = 0
        return subProc

    def _stopProc(self,procName,cmdStr):
        writeLog(self.debugLevl,self.currentState,self.deviceKind,procName+' testing if running')
        if checkIfProcessRunning(procName):
            writeLog(self.debugLevl,self.currentState,self.deviceKind,procName+' was running')
            writeLog(self.debugLevl,self.currentState,self.deviceKind,'Terminating '+procName)
            theskyXProc = getProcessRunning(procName)
            theskyXProc.terminate()
            theskyXProc.wait()
            time.sleep(10)
            if checkIfProcessRunning(procName):
                writeLog(self.debugLevl,self.currentState,self.deviceKind,'Could not terminate '+procName)
                raise Exception('Could not terminate '+procName)
        return

    def pause(self) -> ():
        writeLog(self.debugLevl,self.currentState,self.deviceKind,'Pause... ')
        input('pause')
        return

    # def takeImgSeqAsync(self,saveImg,expSeq,filePath,filePrefix):
    #     foo= dict({'Light':1,'Bias':2,'Dark':3,'Flat':4})
    #     MESSAGE = '/* Java Script */'\
    #     +'ccdsoftCamera.Connect();'\
    #     +'ccdsoftCamera.Asynchronous = true; '\
    #     +'ccdsoftCamera.ExposureTime = ' + str(expSeq.exp) + ';'\
    #     +'ccdsoftCamera.AutoSaveOn = false;'\
    #     +'ccdsoftCamera.ImageReduction = 0;   '\
    #     +'ccdsoftCamera.Frame = ' + str(foo[expSeq.frame]) + ';'\
    #     +'ccdsoftCamera.Delay = ' + str(expSeq.delay) + ';'\
    #     +'ccdsoftCamera.Subframe = false;'\
    #     +'ccdsoftCamera.filterWheelConnect(); '\
    #     +'ccdsoftCamera.FilterIndexZeroBased = ' + str(self.mainFilter.filterNdx[expSeq.filterName]) + ';'\
    #     +'ccdsoftCamera.BinX = ' + str(expSeq.bin) + ';'\
    #     +'ccdsoftCamera.BinY = ' + str(expSeq.bin) + ';'\
    #     +'var cameraResult = ccdsoftCamera.TakeImage();'
    #     for ndx in range(expSeq.rep):
    #         writeLog(self.debugLevl,self.currentState,self.deviceKind,ptos('Taking image %d of %d, %dsec  %dx%d'%(ndx+1,expSeq.rep,expSeq.exp,expSeq.filterName,expSeq.bin,expSeq.bin)).strip())
    #         if skyxExpect(self,'takeimage',MESSAGE,'No error. Error = 0.'):
    #             writeLog(self.debugLevl,self.currentState,self.deviceKind,'Takeimage started')
    #             while not(self.mainCamera.isExposing()):
    #                 time.sleep(1)
    #                 if not(self.wxMonitor.isClear()):
    #                     break
    #             if not(self.wxMonitor.isClearBool):
    #                 break
    #             if saveImg:
    #                 self.fullPath = self.mainCamera.saveImgToFile(self.mainFilter,filePath,filePrefix,expSeq,ndx+1)
    #         else:
    #             ExcMsg="Exception in " + self.deviceKind + "skyxExpect returned with errors"
    #             writeLog(self.debugLevl,self.currentState,self.deviceKind+ExcMsg)
    #             raise Exception(ExcMsg)

def writeLog(debugLevl,ObsState,device,logcomment) -> ():
    if debugLevl:
        if not os.path.exists(filePathLog):
            os.makedirs(filePathLog)
        logLine = ptos(Time.now(),' : %15s : %15s : %s'%(ObsState, device, logcomment))
        print(logLine.strip())
        with open(filePathLog+'/telescopium.log', 'a') as the_file:
            the_file.write(logLine)
    return


#############################################################################
#
# DCPowerSwitch Class
#
class DCPowerSwitch:
    def __init__(self):
        self.deviceKind = 'DC Power Switch'
        self.paceDelay = 2
        self.debugLevl=False
        self.debugCommLevel=False

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def setSerialPortStr(self,serialPortString) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting serialPortStr to '+serialPortString)
        self.serialPortStr = serialPortString
        return

    def setPaceDelay(self,paceDelay) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting paceDelay to '+str(paceDelay))
        self.paceDelay = paceDelay
        return

    def openPort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Opening serial port {self.serialPortStr}')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 19200
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in openPort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            writeLog(self.debugLevl,"",self.deviceKind,'IOError happned')
            raise Exception(ExcMsg)

    def closePort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Closing serial port')
            self.serPort.close()
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in closePort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def checkIdent(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'Checking Identity')
            self.getSw(0)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in checkIdent"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setSwOff(self,id) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Setting SwOff for SW {id}')
            buffer = [4,18,2**id,0,0,0,15]
            buffer[5] = (((buffer[0]+buffer[1]+buffer[2])^255) & 255) + 1
            self.serPort.write(bytes(buffer))
            time.sleep(self.paceDelay)
            writeLog(self.debugCommLevel,"",self.deviceKind,'    SENT Command  : >'+ptos(buffer).strip()+'<')
            if not(self.getSw(id)==0):
                ExcMsg="Exception in " + self.deviceKind + " switch did not turn off"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setSwOff"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setSwOn(self,id) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Setting SwOn for SW {id}')
            buffer = [4,17,2**id,0,0,0,15]
            buffer[5] = (((buffer[0]+buffer[1]+buffer[2])^255) & 255) + 1
            self.serPort.write(bytes(buffer))
            time.sleep(self.paceDelay)
            writeLog(self.debugCommLevel,"",self.deviceKind,'    SENT Command  : >'+ptos(buffer).strip()+'<')
            if not(self.getSw(id)==1):
                ExcMsg="Exception in " + self.deviceKind + " switch did not turn on"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setSwOn"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getSw(self,id) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Get Switch state')
            buffer = [4,24,0,0,0,0,15]
            buffer[5] = (((buffer[0]+buffer[1]+buffer[2])^255) & 255) + 1
            self.serPort.reset_input_buffer()
            self.serPort.write(bytes(buffer))
            time.sleep(self.paceDelay)
            writeLog(self.debugCommLevel,"",self.deviceKind,'    SENT Command  : >'+ptos(buffer).strip()+'<')

            self.responce=self.serPort.read(7)

            buffer[0]=self.responce[0]
            buffer[1]=self.responce[1]
            buffer[2]=self.responce[2]
            buffer[3]=self.responce[3]
            buffer[4]=self.responce[4]
            buffer[5]=self.responce[5]
            buffer[6]=self.responce[6]

            writeLog(self.debugCommLevel,"",self.deviceKind,'    RXED Response : >'+ptos(buffer).strip()+'<')

            if not(buffer[5] == (((buffer[0]+buffer[1]+buffer[2]+buffer[3])^255) & 255) + 1):
                ExcMsg="Exception in " + self.deviceKind + " Shecksum fail"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)

            writeLog(self.debugLevl,"",self.deviceKind,'Switch '+ str(id) +' state is ' + str(((buffer[3]>>id) & 1)))
            return((buffer[3]>>id) & 1)
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getSw"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


#############################################################################
#
# ParkDetector Class
#
class ParkDetector:
    def __init__(self):
        self.deviceKind = 'Park Detector'
        self.paceDelay = 1
        self.sleepTimeForUserInput = 1
        self.debugLevl=False
        self.debugCommLevel=False

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def setSerialPortStr(self,serialPortString) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting serialPortStr to '+serialPortString)
        self.serialPortStr = serialPortString
        return

    def setPaceDelay(self,paceDelay) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting paceDelay to '+str(paceDelay))
        self.paceDelay = paceDelay
        return

    def openPort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Opening serial port {self.serialPortStr}')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 9600
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in openPort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def closePort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'closing serial port')
            self.serPort.close()
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in closePort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def checkIdent(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'Checking Identity')
            if not(serialExpect(self,'IDENT','ParkDetector')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in checkIdent"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def FrcMntOn(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'FrcMntOn')
            if not(serialExpect(self,'FrcMntOn','FrcMntOn')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in FrcMntOn"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def FrcMntOff(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'FrcMntOff')
            if not(serialExpect(self,'FrcMntOff','FrcMntOff')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in FrcMntOff"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def FrcPPOn(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'FrcPPOn')
            if not(serialExpect(self,'FrcPPOn','FrcPPOn')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in FrcPPOn"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def FrcPPOff(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'FrcPPOff')
            if not(serialExpect(self,'FrcPPOff','FrcPPOff')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            time.sleep(10)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in FrcPPOff"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getAll(self) -> ():
        try:
            self.responce = serialSend(self,'GetAll')
            writeLog(self.debugLevl,"",self.deviceKind,f'Getting all data ={self.responce}')
            return self.responce
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " getAll"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isParked(self) -> (bool):
        try:
            isParked = serialExpect(self,'isParked','Parked')
            if isParked:
                writeLog(self.debugLevl,"",self.deviceKind,'Checking is parked = parked')
            else:
                writeLog(self.debugLevl,"",self.deviceKind,'Checking is parked = not parked')
            return isParked
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isParked"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

#############################################################################
#
# DomeController Class
#
class DomeController:
    def __init__(self):
        self.deviceKind = 'Dome Controller'
        self.paceDelay = 1
        self.debugLevl=False
        self.debugCommLevel = False

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def setSerialPortStr(self,serialPortString) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting serialPortStr to '+serialPortString)
        self.serialPortStr = serialPortString
        return

    def setPaceDelay(self,paceDelay) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting paceDelay to '+str(paceDelay))
        self.paceDelay = paceDelay
        return

    def openPort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Opening serial port {self.serialPortStr}')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 9600
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in openPort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def closePort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Closing serial port')
            self.serPort.close()
            if self.serPort.isOpen():
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in closePort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def checkIdent(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'Checking Identity')
            if not(serialExpect(self,'IDENT#','RoofRoller')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in checkIdent"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def openRoof(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Opening roof')
            if self.Activate:
                if not(serialSend(self,'QUERYROOF#')=='is Open'):
                    if not(serialExpect(self,'OPENROOF#','OPENROOF Ack')):
                        ExcMsg="Exception in " + self.deviceKind + ""
                        writeLog(self.debugLevl,"",self.deviceKind+ExcMsg)
                        raise Exception(ExcMsg)
                    time.sleep(1)
                    while serialExpect(self,'QUERYROOF#','is Opening'):
                        time.sleep(5)
                    time.sleep(1)
                    if not(serialExpect(self,'QUERYROOF#','is Open')):
                        ExcMsg="Exception in " + self.deviceKind + ""
                        writeLog(self.debugLevl,"",self.deviceKind+ExcMsg)
                        raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in openRoof"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def closeRoof(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Closing roof')
            if self.Activate:
                if not(serialSend(self,'QUERYROOF#')=='is Closed'):
                    if not(serialExpect(self,'CLOSEROOF#','CLOSEROOF Ack')):
                        ExcMsg="Exception in " + self.deviceKind + ""
                        writeLog(self.debugLevl,"",self.deviceKind+ExcMsg)
                        raise Exception(ExcMsg)
                        return
                    time.sleep(1)
                    while serialExpect(self,'QUERYROOF#','is Closing'):
                        time.sleep(5)
                    time.sleep(1)
                    if not(serialExpect(self,'QUERYROOF#','is Closed')):
                        ExcMsg="Exception in " + self.deviceKind + ""
                        writeLog(self.debugLevl,"",self.deviceKind+ExcMsg)
                        raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in closeRoof"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def queryRoof(self) -> (str):
        try:
            self.responce = serialSend(self,'QUERYROOF#')
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return self.responce
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in queryRoof"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isOpen(self) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Confirm is open')
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return serialExpect(self,'QUERYROOF#','is Open')
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isOpen"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isClosed(self) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Confirm is closed')
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return serialExpect(self,'QUERYROOF#','is Closed')
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isClosed"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

#############################################################################
#
# WxMonitor Class
#
class WxMonitor:
    def __init__(self):
        self.deviceKind = 'Wx Monitor'
        self.paceDelay = 1
        self.debugLevl = False
        self.debugCommLevel=False

        self.deltaTemp = 99
        self.ambTemp = 99
        self.skyTemp = 99

        self.isClearBool = True
        self.isClearNow = True

        self.timeBecameClear = Time.now()-u.s*120

        self.safeToOpenDelay_sec = 60


        self.tempThreshold=20.0

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def setSerialPortStr(self,serialPortString) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting serialPortStr to '+serialPortString)
        self.serialPortStr = serialPortString
        return

    def setPaceDelay(self,paceDelay) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting paceDelay to '+str(paceDelay))
        self.paceDelay = paceDelay
        return

    def openPort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Opening serial port {self.serialPortStr}')
            self.serPort = serial.Serial(self.serialPortStr,timeout=10)  # open serial port
            time.sleep(5)
            self.serPort.baudrate = 9600
            if not(self.serPort.isOpen()):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in openPort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def closePort(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Closing serial port')
            self.serPort.close()
            if self.serPort.isOpen():
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in openPort"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def checkIdent(self) -> ():
        try:
            writeLog(True,"",self.deviceKind,'Checking Identity')
            if not(serialExpect(self,'IDENT','wxStation')):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in checkIdent"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setTempThreshold(self,tempThreshold) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Setting tempThreshold to {tempThreshold}')
            self.tempThreshold = tempThreshold
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setTempThreshold"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getAmbTemp(self) -> (float):
        try:
            self.ambTemp=float(serialSend(self,'T'))
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            writeLog(self.debugLevl,"",self.deviceKind,f'Getting ambient temperature {self.ambTemp}')
            return self.ambTemp
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getAmbTemp"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getSkyTemp(self) -> (float):
        try:
            self.skyTemp=float(serialSend(self,'ST'))
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            writeLog(self.debugLevl,"",self.deviceKind,f'Getting sky temperature {self.skyTemp}')
            return self.skyTemp
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getSkyTemp"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isClear(self) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Getting isClear')
            self.getAmbTemp()
            self.getSkyTemp()
            self.deltaTemp=self.ambTemp-self.skyTemp
            self.wasClear = self.isClearNow
            self.isClearNow=self.deltaTemp>self.tempThreshold
            writeLog(self.debugLevl,"",self.deviceKind, ptos('Amb%6.2f Sky%6.2f Diff%6.2f'%(self.ambTemp,self.skyTemp,self.deltaTemp)).strip())

            if self.isClearNow and not self.wasClear:
                self.timeBecameClear = Time.now()

            if self.isClearNow and ((Time.now()-self.timeBecameClear).sec > self.safeToOpenDelay_sec):
                self.isClearBool = True
            else:
                self.isClearBool = False

            writeLog(self.debugLevl,"",self.deviceKind, ptos('wasClear %s, isClearNow %s, timeClear %f %s'%(self.wasClear,self.isClearNow,(Time.now()-self.timeBecameClear).sec,self.isClearBool)).strip())
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)

            return self.isClearBool
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isClear"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


#############################################################################
#
# Mount Class
#
class Mount:
    def __init__(self):
        self.deviceKind = 'Mount'
        self.paceDelay = 1
        self.debugLevl = False
        self.debugCommLevel = False
        self.postSlewPause = 2

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def connect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Connect Mount')
            command = ""\
                    + "sky6RASCOMTele.Connect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            if not(self.isConnected()):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isConnected(self) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Query is isConnected')
            command = ""\
                    + "Out=sky6RASCOMTele.IsConnected;" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            writeLog(self.debugLevl,"",self.deviceKind,f'isConnected = {returned_value}')
            if returned_value == 'false':
                returned_value = False
            elif returned_value == 'true':
                returned_value = True
            return returned_value
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isConnected"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


    def connectAndDoNotUnpark(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Connect Mount')
            command = ""\
                    + "sky6RASCOMTele.ConnectAndDoNotUnpark();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            if not(self.isConnected()):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connectAndDoNotUnpark"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def disconnect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Disconnect Mount')
            command = ""\
                    + "sky6RASCOMTele.Disconnect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in disconnect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def disconnectTelescope(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'DisconnectTelescope Mount')
            command = ""\
                    + "sky6RASCOMTheSky.DisconnectTelescope();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in disconnectTelescope"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def home(self, asyncMode: bool) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Starting Home Mount')
            command = ""\
                    + "sky6RASCOMTele.Connect();"\
                    + f"sky6RASCOMTele.Asynchronous={js_bool(asyncMode)};" \
                    + "Out=sky6RASCOMTele.FindHome();" \
                    + "Out += \"\\n\";"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'Home complete')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in home"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def park(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Starting Park Mount')
            command = ""\
                    + "sky6RASCOMTele.Asynchronous=false;" \
                    + "Out=sky6RASCOMTele.Park();" \
                    + "Out += \"\\n\";"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'Park complete')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in park"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def parkAndDoNotDisconnect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Starting Park Mount')
            command = ""\
                    + "sky6RASCOMTele.Asynchronous=false;" \
                    + "Out=sky6RASCOMTele.ParkAndDoNotDisconnect();" \
                    + "Out += \"\\n\";"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'Park complete')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in parkAndDoNotDisconnect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isParked(self) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Query is Parked')
            command = ""\
                    + "Out=sky6RASCOMTele.IsParked();" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            writeLog(self.debugLevl,"",self.deviceKind,f'Parked = {returned_value}')
            if returned_value == 'false':
                returned_value = False
            elif returned_value == 'true':
                returned_value = True
            return returned_value
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isParked"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def unpark(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Starting Unpark Mount')
            command = ""\
                    + "sky6RASCOMTele.Connect();"\
                    + "Out=sky6RASCOMTele.Unark();" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            writeLog(self.debugLevl,"",self.deviceKind,'Unpark completed')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in unpark"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def slewToSafeCoordinates(self,obsLocation) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'SlewToSafeCoordinates')
            timeNowUTC = Time.now()
            writeLog(self.debugLevl,"",self.deviceKind,ptos('timeNowUTC      =',timeNowUTC).strip())
            mountSafeCoord = AltAz(alt=45*u.deg,az=55*u.deg,obstime=timeNowUTC, location=obsLocation)
            mountSafeCoord = mountSafeCoord.transform_to(ICRS())
            mountSafeCoord = SkyCoord(mountSafeCoord.ra.value, mountSafeCoord.dec.value, frame='icrs', unit='deg')
            writeLog(self.debugLevl,"",self.deviceKind,ptos('mountSafeCoord  =',mountSafeCoord.to_string('hmsdms')).strip())
            self.slewToRaDec(mountSafeCoord.ra.hour,mountSafeCoord.dec.value,False)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in slewToSafeCoordinates"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def slewToRaDec(self,Ra,Dec,asyncMode) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,ptos('Slew Mount ra:%6.2f dec:%6.2f'%(Ra,Dec)).strip())
            command = ""\
                    + "sky6RASCOMTele.Connect();" \
                    + f"sky6RASCOMTele.Asynchronous={js_bool(asyncMode)};" \
                    + "var wasTracking=sky6RASCOMTele.IsTracking;" \
                    + "var oldRaRate=sky6RASCOMTele.dRaTrackingRate;" \
                    + "var oldDecRate=sky6RASCOMTele.dDecTrackingRate;" \
                    + f'Out=sky6RASCOMTele.SlewToRaDec({Ra},{Dec},"");' \
                    + "sky6RASCOMTele.SetTracking(wasTracking,1,oldRaRate,oldDecRate);" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            writeLog(self.debugLevl,"",self.deviceKind,'Slew completed')
            time.sleep(self.postSlewPause)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in slewToRaDec"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def slewToAltAz(self, alt, az, asyncMode) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,ptos('Slew Mount alt:%6.2f az:%6.2f'%(alt,az)).strip())
            command = ""\
                    + "sky6RASCOMTele.Connect();" \
                    + f"sky6RASCOMTele.Asynchronous={js_bool(asyncMode)};" \
                    + "var wasTracking=sky6RASCOMTele.IsTracking;" \
                    + "var oldRaRate=sky6RASCOMTele.dRaTrackingRate;" \
                    + "var oldDecRate=sky6RASCOMTele.dDecTrackingRate;" \
                    + f'Out=sky6RASCOMTele.SlewToAzAlt({az},{alt},\"\");' \
                    + "sky6RASCOMTele.SetTracking(wasTracking,1,oldRaRate,oldDecRate);" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            writeLog(self.debugLevl,"",self.deviceKind,'Slew completed')
            time.sleep(self.postSlewPause)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in slewToAltAz"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isSlewComplete(self) -> (bool):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Query is Slew Complete')
            success = True
            is_complete = False
            command = ""\
                    + "Out=sky6RASCOMTele.IsSlewComplete;" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
                if success:
                    result_as_int = int(returned_value)
                    is_complete = result_as_int != 0
            return is_complete
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isSlewComplete"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def abortSlew(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'abortSlew')
            command = ""\
                    + "Out=sky6RASCOMTele.Abort();" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in abortSlew"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getRaDec(self) -> (float, float):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Query RaDec')
            return_ra: float = 0
            return_dec: float = 0
            command = ""\
                    + "sky6RASCOMTele.GetRaDec();" \
                    + "var Out=sky6RASCOMTele.dRa + '/' + sky6RASCOMTele.dDec;" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            if success:
                parts = returned_value.split("/")
                return_ra = float(parts[0])
                return_dec = float(parts[1])
                return return_ra, return_dec
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getRaDec"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getAltAz(self) -> (float, float):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Query AltAz')
            return_alt: float = 0
            return_az: float = 0
            command = ""\
                    + "sky6RASCOMTele.GetAzAlt();" \
                    + "var Out=sky6RASCOMTele.dAlt + '/' + sky6RASCOMTele.dAz;" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            if success:
                parts = returned_value.split("/")
                return_alt = float(parts[0])
                return_az = float(parts[1])
                return return_alt, return_az
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getAltAz"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setTracking(self, tracking: bool) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'Set Tracking to {tracking}')
            command = ""\
                    + f"Out=sky6RASCOMTele.SetTracking({1 if tracking else 0},1,0,0);" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setTracking"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def isTracking(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Query Tracking')
            command = ""\
                    + "Out=sky6RASCOMTele.IsTracking();" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                (success, message) = check_for_error_in_return_value(returned_value)
            writeLog(self.debugLevl,"",self.deviceKind,'Query Parked completed')
            return message
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in isTracking"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


    def jog(self,deltaRa,deltaDec):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'jog')
            NorS = "N"
            if(deltaDec<0): NorS = "S"
            EorW = "E"
            if(deltaRa<0): EorW = "W"
            command = ""\
                    + "sky6RASCOMTele.Asynchronous = false;"\
                    + f'sky6RASCOMTele.Jog({abs(deltaDec)}, "{NorS}");'\
                    + f'sky6RASCOMTele.Jog({abs(deltaRa )}, "{EorW}");'
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'jog completed')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in jog"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def jogDec(self,deltaDec):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'jog')
            NorS = "N"
            if(deltaDec<0): NorS = "S"
            command = ""\
                    + "sky6RASCOMTele.Asynchronous = false;"\
                    + f'sky6RASCOMTele.Jog({abs(deltaDec)}, "{NorS}");'
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'jog completed')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in jog"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def jogRa(self,deltaRa):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'jog')
            EorW = "E"
            if(deltaRa<0): EorW = "W"
            command = ""\
                    + "sky6RASCOMTele.Asynchronous = false;"\
                    + f'sky6RASCOMTele.Jog({abs(deltaRa )}, "{EorW}");'
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'jog completed')
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in jog"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

#############################################################################
#
# MainFilter Class
#
class MainFilter:
    def __init__(self):
        self.deviceKind = 'mainFilter'
        self.paceDelay = 1
        self.debugLevl = False
        self.debugCommLevel = False
        #self.filterNdx={'R':0,'G':1,'B':2,'C':3,'L':4,'SII':5,'OIII':6,'Ha':7}
        #self.filterName=['R','G','B','C','L','SII','OIII','Ha']

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def connect(self) -> ():
        if not self.kind == 'OSC':
            try:
                writeLog(self.debugLevl,"",self.deviceKind,'Connect')
                command = "ccdsoftCamera.filterWheelConnect();"
                (success, message) = skyXsendCndWithNoReturn(self,command)
                if 0:
                    ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                    writeLog(True,"",self.deviceKind,ExcMsg)
                    raise Exception(ExcMsg)
                return
            except:
                ExcMsg="Exception in " + self.deviceKind + " unexpected error in connect"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)

    def disconnect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'disconnect')
            command = "ccdsoftCamera.filterWheelDisconnect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in disconnect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getNumbFilters(self) -> ():
        if not self.kind == 'OSC':
            command = ""\
                    + "var temp=ccdsoftCamera.lNumberFilters;" \
                    + "var Out;" \
                    + "Out=temp+\"\\n\";"
            (success, result, message) = skyXsendCndWithReturn(self,command)
            self.numbFilters= int(result)
            #print(self.numbFilters)
        else:
            self.numbFilters= 0
        return
        
    def getFilterNames(self) -> ():
        if not self.kind == 'OSC':
            self.filterDictFwd =	{}
            self.filterDictRev =	{}
            for ndx in range(self.numbFilters):
                command = ""\
                        + f"var temp=ccdsoftCamera.szFilterName({ndx});" \
                        + "var Out;" \
                        + "Out=temp+\"\\n\";"
                (success, result, message) = skyXsendCndWithReturn(self,command)
                self.filterDictFwd[ndx] = result
                self.filterDictRev[result] = ndx
                #print(self.filterDictRev)
        else:
            self.filterDictFwd =	{}
            self.filterDictRev =	{}
        return
        
    def setFilterByNdx(self, filterNdx) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'set filter to {filterNdx}')
            self._selected_filterNdx = filterNdx
            command = f"ccdsoftCamera.FilterIndexZeroBased={filterNdx};"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setFilter"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)
            
    def setFilterByName(self, filterName) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'set filter to {filterName}')
            filterNdx = self.filterDictRev[filterName]
            self._selected_filterName = filterName
            self._selected_filterNdx = filterNdx
            command = f"ccdsoftCamera.FilterIndexZeroBased={filterNdx};"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setFilter"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

#############################################################################
#
# MainCamera Class
#
class MainCamera:
    def __init__(self):
        self.deviceKind = 'mainCamera'
        self.paceDelay = 1
        self.debugLevl = False
        self.debugCommLevel = False
        self.tempTollerance = 0.5
        self.tempProbeTimerSec = 10


    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def connect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Connect')
            command = "ccdsoftCamera.Connect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def disconnect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'disconnect')
            command = "ccdsoftCamera.Disconnect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in disconnect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setTempSetPoint(self,cooling_on, target_temperature, waitForTemp) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'setTempSetPoint to {target_temperature}C')
            target_temperature_command = ""
            if cooling_on:
                target_temperature_command = f"ccdsoftCamera.TemperatureSetPoint={target_temperature};"
            command = ""\
                    + f"{target_temperature_command}" \
                    + f"ccdsoftCamera.RegulateTemperature={js_bool(cooling_on)};" \
                    + "ccdsoftCamera.ShutDownTemperatureRegulationOnDisconnect=" \
                    + f"{js_bool(False)};"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            if not(self.getTempSetPoint()==target_temperature):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            if waitForTemp:
                coolerTemp = self.getTemp()
                accumulatedTime=0
                while abs(target_temperature - coolerTemp) > self.tempTollerance:
                    writeLog(self.debugLevl,"",self.deviceKind,f'sleeping {self.tempProbeTimerSec} Sec')
                    time.sleep(self.tempProbeTimerSec)
                    accumulatedTime=accumulatedTime+self.tempProbeTimerSec
                    coolerTemp = self.getTemp()
                    coolerPower = self.getCoolerPower()
                    if (coolerPower>90):
                        ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                        writeLog(True,"",self.deviceKind,ExcMsg)
                        raise Exception(ExcMsg)
                    if (accumulatedTime>3*60):
                        ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                        writeLog(True,"",self.deviceKind,ExcMsg)
                        raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in setTempSetPoint"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getTemp(self) -> (float):
        try:
            command = ""\
                    + "var temp=ccdsoftCamera.Temperature;" \
                    + "var Out;" \
                    + "Out=temp+\"\\n\";"
            temperature = 0
            (success, temperature_result, message) = skyXsendCndWithReturn(self,command)
            if success:
                temperature = Validators.valid_float_in_range(temperature_result, -270, +200)
                if not(temperature is None):
                    writeLog(self.debugLevl,"",self.deviceKind,f'GetTemp = {temperature}C')
                    return temperature
            if 0:
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
                return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getTemp"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getTempSetPoint(self) -> (float):
        try:
            command = ""\
                    + "var temp=ccdsoftCamera.TemperatureSetPoint;" \
                    + "var Out;" \
                    + "Out=temp+\"\\n\";"
            temperature = 0
            (success, temperature_result, message) = skyXsendCndWithReturn(self,command)
            if success:
                temperature = Validators.valid_float_in_range(temperature_result, -270, +200)
                if temperature is None:
                    success = False
                    temperature = 0
                    #message = "Invalid Temperature Returned"
            writeLog(self.debugLevl,"",self.deviceKind,f'GetTemp = {temperature}C')
            return temperature
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getTempSetPoint"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getCoolerPower(self) -> (float):
        try:
            command = ""\
                    + "var power=ccdsoftCamera.ThermalElectricCoolerPower;" \
                    + "var Out;" \
                    + "Out=power+\"\\n\";"
            (success, coolerPower, message) = skyXsendCndWithReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,f'GetCoolerPower = {coolerPower}%')
            return float(coolerPower)
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getCoolerPower"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getAutosavePath(self) -> (str):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'GetAutosavePath')
            command = ""\
                    + "var path=ccdsoftCamera.AutoSavePath;" \
                    + "var Out;" \
                    + "Out=path+\"\\n\";"
            (success, autoSavepath, message) = skyXsendCndWithReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,f'autoSavepath = >{autoSavepath}<')
            return autoSavepath
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getAutosavePath"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


    def abortImage(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'abortImage')
            command = "ccdsoftCamera.Abort();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in abortImage"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    # def saveImageToAutosave(self,objName:str,frameType: str,filter_name: str,exposure: float,binning: int,sequence: int) -> ():
    #     writeLog(self.debugLevl,"",self.deviceKind,'saveImageToAutosave')
    #     saveFileName = generateSaveFileName(frameType,temp,objName,filterName,exposure,binning,sequence)
    #     #writeLog(self.debugLevl,"",self.deviceKind,f'saveFileName = >{saveFileName}<')
    #     command = ""\
    #             + "cam = ccdsoftCamera;" \
    #             + "img = ccdsoftCameraImage;" \
    #             + "img.AttachToActiveImager();" \
    #             + "var path = ccdsoftCamera.AutoSavePath;" \
    #             + f'img.Path = path + "/" + "{saveFileName}";' \
    #             + "var Out=img.Save();" \
    #             + "Out += \"\\n\";"
    #     (success, returned_value, message) = skyXsendCndWithReturn(self,command)
    #     return

    def saveImgToFile(self,directoryPath,frameType,temp,objName,filterName,exposure,binning,sequence) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'saveImgToFile')

            if not os.path.exists(directoryPath):
                writeLog(self.debugLevl,"",self.deviceKind,f'Making Folder {directoryPath}')
                os.makedirs(directoryPath)


            saveFileName = generateSaveFileName(frameType,temp,objName,filterName,exposure,binning,sequence)
            #writeLog(self.debugLevl,"",self.deviceKind,f'saveFileName = >{saveFileName}<')

            command = ""\
                    + "cam = ccdsoftCamera;" \
                    + "img = ccdsoftCameraImage;" \
                    + "img.AttachToActiveImager();" \
                    + f'var path = "{directoryPath}";' \
                    + f'img.Path = path + "/" + "{saveFileName}";' \
                    + "var Out=img.Save();" \
                    + "Out += \"\\n\";"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if not os.path.exists(directoryPath+'/'+saveFileName):
                ExcMsg="Exception in " + self.deviceKind + " what was expected did not happen"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            self.lastSaveFilePath = directoryPath
            self.lastFileName = saveFileName
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in saveImgToFile"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def takeBiasFrame(self, binning: int, autoSaveFile: bool, asyncMode: bool) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'takeBiasFrame {binning}x{binning} autoSaveFile={js_bool(autoSaveFile)}, asyncMode={js_bool(asyncMode)}')
            command = ""\
                    + "ccdsoftCamera.Autoguider=false;" \
                    + f"ccdsoftCamera.Asynchronous={js_bool(asyncMode)};" \
                    + f"ccdsoftCamera.AutoSaveOn={js_bool(autoSaveFile)};" \
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.ToNewWindow=false;" \
                    + "ccdsoftCamera.ccdsoftAutoSaveAs=0;" \
                    + "ccdsoftCamera.Frame=2;" \
                    + f"ccdsoftCamera.ExposureTime = {0};" \
                    + f"ccdsoftCamera.BinX={binning};" \
                    + f"ccdsoftCamera.BinY={binning};" \
                    + "var cameraResult = ccdsoftCamera.TakeImage();"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                return_parts = returned_value.split("|")
                assert (len(return_parts) > 0)
                if return_parts[0] == "0":
                    pass  # Result indicates success
                else:
                    success = False
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in takeBiasFrame"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def takeDarkFrame(self, ExposureTime: float, binning: int, autoSaveFile: bool, asyncMode: bool) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'takeDarkFrame {ExposureTime}Sec {binning}x{binning} autoSaveFile={js_bool(autoSaveFile)}, asyncMode={js_bool(asyncMode)}')
            command = ""\
                    + "ccdsoftCamera.Autoguider=false;" \
                    + f"ccdsoftCamera.Asynchronous={js_bool(asyncMode)};" \
                    + f"ccdsoftCamera.AutoSaveOn={js_bool(autoSaveFile)};" \
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.ToNewWindow=false;" \
                    + "ccdsoftCamera.ccdsoftAutoSaveAs=0;" \
                    + "ccdsoftCamera.Frame=3;" \
                    + f"ccdsoftCamera.ExposureTime = {ExposureTime};" \
                    + f"ccdsoftCamera.BinX={binning};" \
                    + f"ccdsoftCamera.BinY={binning};" \
                    + "var cameraResult = ccdsoftCamera.TakeImage();"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                return_parts = returned_value.split("|")
                assert (len(return_parts) > 0)
                if return_parts[0] == "0":
                    pass  # Result indicates success
                else:
                    success = False
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in takeDarkFrame"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def takeFlatFrame(self, ExposureTime: float, binning: int, autoSaveFile: bool, asyncMode: bool) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'takeFlatFrame {ExposureTime}Sec {binning}x{binning} autoSaveFile={js_bool(autoSaveFile)}, asyncMode={js_bool(asyncMode)}')
            command = ""\
                    + "ccdsoftCamera.Autoguider=false;" \
                    + f"ccdsoftCamera.Asynchronous={js_bool(asyncMode)};" \
                    + f"ccdsoftCamera.AutoSaveOn={js_bool(autoSaveFile)};" \
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.ToNewWindow=false;" \
                    + "ccdsoftCamera.ccdsoftAutoSaveAs=0;" \
                    + "ccdsoftCamera.Frame=4;" \
                    + f"ccdsoftCamera.ExposureTime = {ExposureTime};" \
                    + f"ccdsoftCamera.BinX={binning};" \
                    + f"ccdsoftCamera.BinY={binning};" \
                    + "var cameraResult = ccdsoftCamera.TakeImage();"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                return_parts = returned_value.split("|")
                assert (len(return_parts) > 0)
                if return_parts[0] == "1":
                    pass  # Result indicates success
                else:
                    success = False
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in takeFlatFrame"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def takeLightFrame(self, ExposureTime: float, binning: int, imageReduction: int, autoSaveFile: bool, asyncMode: bool) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'takeLightFrame {ExposureTime}Sec {binning}x{binning} autoSaveFile={js_bool(autoSaveFile)}, asyncMode={js_bool(asyncMode)}')
            command = ""\
                    + "ccdsoftCamera.Autoguider=false;" \
                    + f"ccdsoftCamera.Asynchronous={js_bool(asyncMode)};" \
                    + f"ccdsoftCamera.AutoSaveOn={js_bool(autoSaveFile)};" \
                    + f"ccdsoftCamera.ImageReduction={imageReduction};" \
                    + "ccdsoftCamera.ToNewWindow=false;" \
                    + "ccdsoftCamera.ccdsoftAutoSaveAs=0;" \
                    + "ccdsoftCamera.Frame=1;" \
                    + f"ccdsoftCamera.ExposureTime = {ExposureTime};" \
                    + f"ccdsoftCamera.BinX={binning};" \
                    + f"ccdsoftCamera.BinY={binning};" \
                    + "var cameraResult = ccdsoftCamera.TakeImage();"
            (success, returned_value, message) = skyXsendCndWithReturn(self,command)
            if success:
                return_parts = returned_value.split("|")
                assert (len(return_parts) > 0)
                if return_parts[0] == "1":
                    pass  # Result indicates success
                else:
                    success = False
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in takeLightFrame"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

#############################################################################
#
# Guider Class
#
class Guider:
    def __init__(self):
        self.deviceKind = 'Guider'
        self.paceDelay = 1
        self.debugLevl = False
        self.debugCommLevel = False
        self.postSlewPause = 2

    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def connect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Connect')
            command = ""\
                    + "ccdsoftAutoguider.Connect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def disconnect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Disconnect')
            command = ""\
                    + "ccdsoftAutoguider.Disconnect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in disconnect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def setExposure(self,exp) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting exposure to '+str(exp))
        self.exp = exp
        return


    def takeImage(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'takeImage')
            command = ""\
            +"ccdsoftAutoguider.Asynchronous = false;"\
            +"ccdsoftAutoguider.Frame = 1;"\
            +"ccdsoftAutoguider.Delay = 0;"\
            +"ccdsoftAutoguider.Subframe = false;"\
            +"ccdsoftAutoguider.ExposureTime = " + str(self.exp) + ";"  \
            +"ccdsoftAutoguider.AutoSaveOn = true;"\
            +"ccdsoftAutoguider.TakeImage();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in takeImage"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


    def findStar(self ) -> ():
       try:
            writeLog(self.debugLevl,"",self.deviceKind,'findStar')
            command = ""\
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
            (success, returned_result, message) = skyXsendCndWithReturn(self,command)
            #print(returned_result)
            data2 = returned_result.split("|")
            #print(data2[0],data2[1])
            self.starX = data2[0]
            self.starY = data2[1]
            return
       except:
           ExcMsg="Exception in " + self.deviceKind + " unexpected error in findStar"
           writeLog(True,"",self.deviceKind,ExcMsg)
           raise Exception(ExcMsg)

    def start(self ) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Start')
            command = "" \
            +"ccdsoftAutoguider.GuideStarX = " + str(self.starX) + ";"\
            +"ccdsoftAutoguider.GuideStarY = " + str(self.starY) + ";"\
            +"ccdsoftAutoguider.AutoguiderExposureTime = " + str(self.exp) + ";"\
            +"ccdsoftAutoguider.AutoSaveOn = true;"\
            +"ccdsoftAutoguider.Subframe = true;"\
            +"ccdsoftAutoguider.Delay = 0;"\
            +"ccdsoftAutoguider.Frame = 1;"\
            +"ccdsoftAutoguider.Asynchronous = true;"\
            +"ccdsoftAutoguider.Autoguide();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,'Wait 3 sec for guider to settle')
            time.sleep(3)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in Start"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)
        (success, message) = skyXsendCndWithNoReturn(self,command)
        return

    def stop(self ) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Stop')
            command = "" \
            +"ccdsoftAutoguider.Abort();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in Stop"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getError(self ) -> (float,float):
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'getError')
            command = "" \
            +"var errorX = ccdsoftAutoguider.GuideErrorX;"\
            +"var errorY = ccdsoftAutoguider.GuideErrorY;"\
            +"Out = errorX + '|' + errorY;"
            (success,returned_result, message) = skyXsendCndWithReturn(self,command)
            #print(returned_result)
            data2 = returned_result.split("|")
            #print(data2[0],data2[1])
            return data2[0],data2[1]
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getError"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

#############################################################################
#
# Focuser Class
#
class Focuser:
    def __init__(self):
        self.deviceKind = 'Focuser'
        self.paceDelay = 1
        self.debugLevl = False
        self.debugCommLevel = False
        self.postSlewPause = 2
        self.stepInt = 4000
        self.stepSlope = 0


    def setDebugLevel(self,debugLevl) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugLevl to '+str(debugLevl))
        self.debugLevl = debugLevl
        return

    def setDebugCommLevel(self,debugCommLevel) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,'Setting debugCommLevel to '+str(debugCommLevel))
        self.debugCommLevel = debugCommLevel
        return

    def setTempCurve(self,stepInt,stepSlope) -> ():
        writeLog(self.debugLevl,"",self.deviceKind,f'Setting setTempCurve to {stepInt} {stepSlope}step/C')
        self.stepInt = stepInt
        self.stepSlope = stepSlope
        return

    def connect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'Connect')
            command = ""\
                    + "ccdsoftCamera.focConnect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def disconnect(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'disconnect')
            command = ""\
                    + "ccdsoftCamera.focDisconnect();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in connect"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)


    def getTemp(self) -> (float):
        try:
            command = ""\
                    + "focTemp = ccdsoftCamera.focTemperature;" \
                    + "var Out;" \
                    + "Out=focTemp+\"\\n\";"
            (success, focTemp, message) = skyXsendCndWithReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,f'GetTemp {float(focTemp)}C')
            return float(focTemp)
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getTemp"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def getPosition(self) -> (int):
        try:
            command = ""\
                    + "focPos = ccdsoftCamera.focPosition;" \
                    + "var Out;" \
                    + "Out=focPos+\"\\n\";"
            (success, focPos, message) = skyXsendCndWithReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,f'GetPosition {int(focPos)}')
            return int(focPos)
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in getPosition"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def moveIn(self,steps) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'MoveIn')
            command = ""\
                    + f"ccdsoftCamera.focMoveIn({steps});"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in moveIn"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def moveOut(self,steps) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'MoveOut')
            command = ""\
                    + f"ccdsoftCamera.focMoveOut({steps});"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in moveOut"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def moveTo(self,step) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,f'MoveTo {step}')
            if (-1<step) and (step<self.positionMax) :
                isAt = self.getPosition()
                delta = int(step - isAt)
                if delta > 0:
                    self.moveOut(delta)
                elif delta < 0:
                    self.moveIn(delta)
                else:
                    writeLog(self.debugLevl,"",self.deviceKind,'no move required')
            else:
                ExcMsg="Exception in " + self.deviceKind + " out of range"
                writeLog(True,"",self.deviceKind,ExcMsg)
                raise Exception(ExcMsg)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in moveTo"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def focus2(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'focus2')
            command = ""\
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.BinX=1;" \
                    + "ccdsoftCamera.BinY=1;" \
                    + "ccdsoftCamera.AtFocus2();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            writeLog(self.debugLevl,"",self.deviceKind,f'{self.getTemp()},{self.getPosition()}')

            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in focus2"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def focus3(self) -> ():
        try:
            writeLog(self.debugLevl,"",self.deviceKind,'focus2')
            command = ""\
                    + "ccdsoftCamera.ImageReduction=0;" \
                    + "ccdsoftCamera.BinX=1;" \
                    + "ccdsoftCamera.BinY=1;" \
                    + "ccdsoftCamera.AtFocus3();"
            (success, message) = skyXsendCndWithNoReturn(self,command)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in focus3"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)

    def moveToTempCurve(self) -> ():
        try:
            temp = self.getTemp()
            step = int(self.stepInt+self.stepSlope*temp)
            writeLog(self.debugLevl,"",self.deviceKind,f'moveToTempLine {step} at {temp}C')
            self.moveTo(step)
            return
        except:
            ExcMsg="Exception in " + self.deviceKind + " unexpected error in moveToTempCurve"
            writeLog(True,"",self.deviceKind,ExcMsg)
            raise Exception(ExcMsg)




#############################################################################
#
# Helpers
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

def ptos(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def serialSend(foo,cmd):
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Sending command '+cmd)
    time.sleep(foo.paceDelay)
    foo.serPort.write(bytes(cmd+'\n','utf8'))
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'    SENT Command  : >'+cmd+'<')
    time.sleep(foo.paceDelay)
    foo.responce=foo.serPort.readline().decode('utf8').strip()
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'    RXED Response : >'+foo.responce+'<')
    time.sleep(foo.paceDelay)
    return foo.responce

def serialExpect(foo,cmd,expect):
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Sending command '+cmd)
    time.sleep(foo.paceDelay)
    foo.serPort.write(bytes(cmd+'\n','utf8'))
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'    SENT Command  : >'+cmd+'<')
    time.sleep(foo.paceDelay)
    foo.responce=foo.serPort.readline().decode('utf8').strip()
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'    RXED Response : >'+foo.responce+'<')
    time.sleep(foo.paceDelay)
    if foo.responce==expect:
        return True
    else:
        writeLog(foo.debugLevl,"",foo.deviceKind,ptos('    ',cmd+' FAILED expected >'+expect+'< got >'+foo.responce+'<').strip())
        return False

# def skyxExpect(foo,cmd,MESSAGE,expect):

#     writeLog(foo.debugLevl,"",foo.deviceKind,'Sending command '+cmd)
#     TCP_IP = '127.0.0.1'
#     TCP_PORT = 3040
#     BUFFER_SIZE = 1024
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((TCP_IP, TCP_PORT))

#     s.send(MESSAGE.encode('utf8'))

#     writeLog(foo.debugLevl,"",foo.deviceKind,'    SENT MESSAGE  : >'+MESSAGE+'<')
#     foo.responce = s.recv(BUFFER_SIZE).decode('utf8')
#     s.close()
#     writeLog(foo.debugLevl,"",foo.deviceKind,'    RXED Response : >'+foo.responce+'<')

#     if expect in foo.responce:
#         return True
#     else:
#         writeLog(foo.debugLevl,"",foo.deviceKind,ptos('    ',cmd+' FAILED expected >'+expect+'< got >'+foo.responce+'<').strip())
#         return False

def skyXsendCndWithReturn(foo,command: str) -> (bool, str, str):
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Sent command '+command)
    command_packet = "/* Java Script */" \
                     + "/* Socket Start Packet */" \
                     + command \
                     + "/* Socket End Packet */"
    (success, returned_result, message) = send_command_packet(foo,command_packet)
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Rxed >'+js_bool(success)+'< >'+returned_result+'< >'+message+'<')
    return success, returned_result, message

def skyXsendCndWithNoReturn(foo,command: str):
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Sent command '+command)
    command_packet = "/* Java Script */" \
                      + "/* Socket Start Packet */" \
                      + command \
                      + "/* Socket End Packet */"
    (success, returned_result, message) = send_command_packet(foo,command_packet)
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Rxed >'+js_bool(success)+'< >'+returned_result+'< >'+message+'<')
    return success, message

def send_command_packet(foo,command_packet: str):
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Sent command '+command_packet)
    result = ""
    success = False
    message = ""
    address_tuple = ('127.0.0.1', 3040)
    #TheSkyX._server_mutex.lock()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as the_socket:
        try:
            the_socket.connect(address_tuple)
            bytes_to_send = bytes(command_packet, 'utf-8')
            the_socket.sendall(bytes_to_send)
            returned_bytes = the_socket.recv(1024)
            result_lines = returned_bytes.decode('utf=8') + "\n"
            #writeLog(foo.debugCommLevel,"",foo.deviceKind,'Rxed >'+result_lines+'<')
            parsed_lines = result_lines.split("\n")
            if len(parsed_lines) > 0:
                result = parsed_lines[0]
                success = True
        except:
            ExcMsg="Exception in " + foo.deviceKind + " unexpected error in Stop"
            writeLog(True,"",foo.deviceKind,ExcMsg)
            raise Exception(ExcMsg)
    #TheSkyX._server_mutex.unlock()
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Rxed success >'+js_bool(success)+'<')
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Rxed result  >'+result+'<')
    writeLog(foo.debugCommLevel,"",foo.deviceKind,'Rxed message >'+message+'<')
    if ('SyntaxError:' in result) or ('TypeError:' in result) or ('ReferenceError:' in result) :
        ExcMsg="Exception in " + foo.deviceKind + " " + result
        writeLog(True,"",foo.deviceKind,ExcMsg)
        raise Exception(ExcMsg)
    time.sleep(foo.paceDelay)
    return success, result, message


def check_for_error_in_return_value(returned_text: str) -> (bool, str):
    """Check for TheSkyX errors that are encoded in the return value string"""
    returned_text_upper = returned_text.upper()
    success = False
    message = ""
    if returned_text_upper.startswith("TYPEERROR: PROCESS ABORTED"):
        message = "Camera Aborted"
    elif returned_text_upper.startswith("TYPEERROR:"):
        message = returned_text
    elif returned_text_upper.startswith("TYPEERROR: CFITSIO ERROR"):
        message = "File save folder doesn't exist or not writeable"
    else:
        success = True
    return success, message

def js_bool(value: bool) -> str:
    return "true" if value else "false"

def getProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;


def checkIfProcessRunning(processName):
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False;

def generateSaveFileName(frameType,temp,objName,filterName,exposure,binning,sequence):
    dateStamp = Time.now().strftime("%Y%m%d-%H%M%S")
    saveFileName = f'{frameType} {int(temp)}C {objName} {filterName} {exposure}s {binning}bin #{sequence:03d} {dateStamp}.fit'
    return saveFileName

