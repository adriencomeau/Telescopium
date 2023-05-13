#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 13:04:39 2021

@author: adrien
"""

import telescopium 


#############################################################################
#
# Set Observatory Object
#
observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.setDebugLevel(True)

observatory.startDcPowerSwitch()
observatory.dcPowerSwitch.setSwOn(6) 