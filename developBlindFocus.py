# # -*- coding: utf-8 -*-
# """
# Spyder Editor

# This is a tempSetPointorary script file.
# """

import telescopium
import pandas as pd
import matplotlib.pyplot as plt

observatory = telescopium.Observatory()
observatory.getMainControl()
#observatory.mainControl['debugLevel']        = True      # json active while running
#observatory.mainControl['debugCommLevel']        = True      # json active while running


#############################################################################
#
#
observatory.setObsLocation()
observatory.calculateNight()

#############################################################################
# Start Webcam and TheSkyX
#
observatory.startTheSkyX()

#############################################################################
# Set folder for saving
#
observatory.setPathsForTonight()

observatory.startDcPowerSwitch()
observatory.setAllSwOn()

#############################################################################
# Start the items that were powered up
#
observatory.startFocuser()
observatory.startMainCamera()
observatory.startMainFilter()

exposure        = 0.01
binning         = 2
imageReduction  = 0
autoSaveFile    = False
asyncMode       = False
filterName      = 'L'

frameType       = 'Light'
tempSetPoint    = int(observatory.mainCamera.getTempSetPoint())
objName         = 'BlindFocusRun'
sequence        = 0

blindFocusData = pd.DataFrame(columns = ['Step', 'Count', 'FWHM']) 

for step in range(200,4000+1,100):
    observatory.mainFocuser.moveTo(step)
    observatory.mainFilter.setFilterByName(filterName)
    observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)
    observatory.mainCamera.saveImgToFile(observatory.filePathBias,frameType,tempSetPoint,objName,filterName,exposure,binning,sequence)
    retInfo = observatory.mainCamera.getInventory()
    #retInfo['FWHM']=min(10,2+(((step-3000)/500)**2))
    #retInfo['FWHM']=min(10,2+((abs(step-2770)/50)))
    print(f"Step {step:5d} {retInfo['count']:3d} stars FWHM {retInfo['FWHM']:6.2f}")
    blindFocusData.loc[len(blindFocusData)] = {'Step':step, 'Count':retInfo['count'], 'FWHM':retInfo['FWHM']}

    plt.figure(1)
    plt.plot(blindFocusData['Step'],blindFocusData['FWHM'],'o')
    plt.xlabel('Step')
    plt.ylabel('FWHM')    
    plt.show()

blindFocusData.to_excel(observatory.telescopiumLibraryPath +'blindFocusData.ods',index=False)

