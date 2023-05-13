"""
Created on Tue Mar 30 16:05:05 2021

@author: adrien
"""

import telescopium
import pandas as pd

observatory = telescopium.Observatory()
observatory.getMainControl()
observatory.mainControl['getNewInstance']        = True      # (True) Get new instances of apps (Cheese/SkyX etc)
observatory.setDebugLevel(True)

observatory.setObsLocation()
observatory.calculateNight()

observatory.startTheSkyX()

#############################################################################
# Set folder for saving
#
observatory.setPathsForTonight()

###############################################################################
# Start MainCamera
#
observatory.startMainCamera()

###############################################################################
# Start MainFilter
#
observatory.startMainFilter()

###############################################################################
# the todo ilst
#
#   ------------------------------------
#
#   ------------------------------------
#   Have to tackle pier flip at some time...
#   if get new instance is False, does not mean dont get one if its not running,
#

observatory.loadWorkList()
while observatory.chooseWorkItem():
    #############################################################################
    # get the exposure details
    #
    kBool_o=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_o) or (observatory.workList.loc[observatory.workItemRowNdx].done_o.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_o.astype(int))))
    kBool_1=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_1) or (observatory.workList.loc[observatory.workItemRowNdx].done_1.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
    kBool_2=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_2) or (observatory.workList.loc[observatory.workItemRowNdx].done_2.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
    kBool_3=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_3) or (observatory.workList.loc[observatory.workItemRowNdx].done_3.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
    if kBool_o:
        exposure            = observatory.workList.loc[observatory.workItemRowNdx].Exp_o.astype(int)
        binning             = observatory.workList.loc[observatory.workItemRowNdx].Bin_o.astype(int)
        filterName          = observatory.workList.loc[observatory.workItemRowNdx].F_o
        srtNdx              = observatory.workList.loc[observatory.workItemRowNdx].done_o.astype(int)
        endNdx              = observatory.workList.loc[observatory.workItemRowNdx].Rep_o.astype(int)
        maxNdx              = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
    elif kBool_1:
        exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp_j.astype(int)
        binning         = observatory.workList.loc[observatory.workItemRowNdx].Bin_j.astype(int)
        filterName      = observatory.workList.loc[observatory.workItemRowNdx].F_1
        srtNdx          = observatory.workList.loc[observatory.workItemRowNdx].done_1.astype(int)
        endNdx          = observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int)
        maxNdx          = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
    elif kBool_2:
        exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp_j.astype(int)
        binning         = observatory.workList.loc[observatory.workItemRowNdx].Bin_j.astype(int)
        filterName      = observatory.workList.loc[observatory.workItemRowNdx].F_2
        srtNdx          = observatory.workList.loc[observatory.workItemRowNdx].done_2.astype(int)
        endNdx          = observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int)
        maxNdx          = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
    elif kBool_3:
        exposure        = observatory.workList.loc[observatory.workItemRowNdx].Exp_j.astype(int)
        binning         = observatory.workList.loc[observatory.workItemRowNdx].Bin_j.astype(int)
        filterName      = observatory.workList.loc[observatory.workItemRowNdx].F_3
        srtNdx          = observatory.workList.loc[observatory.workItemRowNdx].done_3.astype(int)
        endNdx          = observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int)
        maxNdx          = ((observatory.mainControl['maxExposureBlock_hr']*3600)/exposure).astype('int')
    else:
        raise Exception('shit 1')
    x=1/0
    
    frameType       = 'Light'
    temp            = int(observatory.mainCamera.getTempSetPoint())
    objName         = observatory.workList.loc[observatory.workItemRowNdx].ObjName
    #############################################################################
    # FEATURE ADD:
    #   * gain control over calibration (reduction) frames
    #
    imageReduction  = 0
    autoSaveFile    = False
    asyncMode       = False

    for sequenceNdx in range(srtNdx,min(endNdx,maxNdx)):

        #############################################################################
        # save work done
        #
        if kBool_o:
            observatory.workList.loc[observatory.workItemRowNdx,'done_o']=sequenceNdx+1
        elif kBool_1:
            observatory.workList.loc[observatory.workItemRowNdx,'done_1']=sequenceNdx+1
        elif kBool_2:
            observatory.workList.loc[observatory.workItemRowNdx,'done_2']=sequenceNdx+1
        elif kBool_3:
            observatory.workList.loc[observatory.workItemRowNdx,'done_3']=sequenceNdx+1
        else:
            raise Exception('shit 2')

        kBool_o=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_o) or (observatory.workList.loc[observatory.workItemRowNdx].done_o.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_o.astype(int))))
        kBool_1=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_1) or (observatory.workList.loc[observatory.workItemRowNdx].done_1.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
        kBool_2=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_2) or (observatory.workList.loc[observatory.workItemRowNdx].done_2.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))
        kBool_3=(not(pd.isna(observatory.workList.loc[observatory.workItemRowNdx].F_3) or (observatory.workList.loc[observatory.workItemRowNdx].done_3.astype(int)==observatory.workList.loc[observatory.workItemRowNdx].Rep_j.astype(int))))

        if kBool_o or kBool_1 or kBool_2 or kBool_3:
            observatory.workList.loc[observatory.workItemRowNdx,'done']='not done'
        else:
            observatory.workList.loc[observatory.workItemRowNdx,'done']='done'
        observatory.saveWorkList()
        
#observatory.saveWorkList()
 

