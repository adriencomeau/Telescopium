#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import telescopium

observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.setDebugLevel(True)

observatory.setObsLocation()
observatory.calculateNight()

observatory.startCheese()
observatory.startTheSkyX()

observatory.startWxMonitor()
observatory.startDcPowerSwitch()
observatory.setAllSwOn()

observatory.startDomeController()
observatory.startParkDetector()
observatory.startMount()
observatory.telescopeMount.disconnectTelescope()

    
#############################################################################
# If it is clear open the roof
#
if observatory.wxMonitor.isClear():
    observatory.domeController.openRoof()

    observatory.telescopeMount.connectDoNotUnpark()                                
    if observatory.isSafeToHome():
        observatory.telescopeMount.home(asyncMode=False)
        observatory.telescopeMount.isConnected()
        observatory.telescopeMount.slewToSafeCoord(observatory.obsLocation)
        observatory.telescopeMount.isSlewComplete()
        observatory.telescopeMount.isTracking()
        observatory.telescopeMount.isParked()

        observatory.telescopeMount.slewToAltAz(45, 54, asyncMode=False)
        observatory.telescopeMount.getAltAz()
        
        observatory.telescopeMount.slewToRaDec(12, 53, asyncMode=False)
        observatory.telescopeMount.getRaDec()    
        observatory.telescopeMount.jogDec(deltaDecMin=60)
        observatory.telescopeMount.jogRa(deltaRaMin=60)
        observatory.telescopeMount.getRaDec()    

        observatory.telescopeMount.parkAndDoNotDisconnect()
        observatory.telescopeMount.isParked()
        observatory.telescopeMount.isConnected()

        observatory.telescopeMount.slewToSafeCoord(observatory.obsLocation)

        #observatory.telescopeMount.connect()    
        #observatory.telescopeMount.disconnect()
        #observatory.telescopeMount.park()
        #observatory.telescopeMount.unpark()
        #observatory.telescopeMount.slewToRaDec(Ra, Dec, asyncMode)
        #observatory.telescopeMount.slewToAltAz(alt, az, asyncMode)
        #observatory.telescopeMount.abortSlew()
        #observatory.telescopeMount.setTracking()
        #observatory.telescopeMount.jog(deltaRa, deltaDec)
    
    
    
    #############################################################################
    # If it is safe to hmoe, home the mount, and slre to safeCoords
    #

