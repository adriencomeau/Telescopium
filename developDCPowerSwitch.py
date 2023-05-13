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


observatory.startDcPowerSwitch()
observatory.setAllSwOff()
#observatory.setAllSwOn()



