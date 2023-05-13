#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 17:19:48 2023

@author: acomeau
"""

import matplotlib.pyplot as plt
import time
import numpy as np
import math

x=np.zeros((1,100))
x1=np.zeros((1,100))
x2=np.zeros((1,100))

for timeSetepNdx in range(1,100):
    
    
    x[0,timeSetepNdx]=timeSetepNdx
    x1[0,timeSetepNdx]=math.cos(timeSetepNdx*2*math.pi/100.0)
    x2[0,timeSetepNdx]=math.sin(timeSetepNdx*2*math.pi/100.0)
    
    plt.figure()
    plt.subplot(211)
    plt.plot(x,x1,'k-.')
    plt.plot(x,x2,'k-.')
    plt.xlabel('Sample')
    plt.ylabel('x,y')
    
    plt.subplot(212)
    plt.plot(x1,x2,'k-.')
    plt.axes('square')
    plt.xlabel('x1')
    plt.ylabel('y1')
    
    plt.show()
    time.sleep(0.1)
