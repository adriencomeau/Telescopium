#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 13:04:39 2021

@author: adrien
"""

import telescopium 
import json

#############################################################################
#
# Set Observatory Object
#
observatory = telescopium.Observatory()
observatory.getMainControl()

s=observatory.mainControl['telescopiumLibraryPath']+'telescopium.json'
with open(s, 'r') as f:
  data = json.load(f)
print(data['stopTelescopium'])
