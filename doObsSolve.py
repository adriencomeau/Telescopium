#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 13:04:39 2021

@author: adrien
"""


import telescopium 


#observatory.closePorts()
#############################################################################
#
# Set Observatory Object
#
observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.setPathsForTonight()

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

observatory.solveUnkState()

observatory.setAllSwOff()                
observatory.dcPowerSwitch.setSwOn(6)



