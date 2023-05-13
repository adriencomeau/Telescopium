#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 14:20:17 2023

@author: acomeau
"""
import serial
import time

serPortA = serial.Serial('/dev/ttyUSB0',timeout=0.1)
serPortB = serial.Serial('/dev/ttyUSB1',timeout=0.1)


while 1:
    if serPortA.inWaiting():
        a2b = serPortA.read(1)
        serPortB.write(a2b)
    
    if serPortB.inWaiting():
        b2a = serPortB.read(1)
        serPortA.write(b2a)

    time.sleep(0)
