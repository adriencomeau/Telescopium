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

observatory.startTheSkyX()


###############################################################################
# Start MainCamera
#
observatory.startMainCamera()

###############################################################################
# Start MainFilter
#
observatory.startMainFilter()


###############################################################################
#   loop over all filters
#   handle OSC as neeeded
#   auto measure filter sensitivity
#   loop over all binning options
#   Do the lease sensitive filters/binnings first
#


###############################################################################
# Slew to flat location
#
#telescopium.writeLog(True,observatory.currentState,'','Slew to flat')
#observatory.calculateFlatSkyLoc()
#observatory.slewToFlat()

binValueList = [1]
for filterNdx in range(observatory.mainFilter.numbFilters):
    for binValue in binValueList:
        exposure        = 1
        binning         = binValue
        imageReduction  = 0
        autoSaveFile    = False
        asyncMode       = False
        observatory.mainFilter.setFilterByNdx(filterNdx)
        observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)
        imgAvgADU = observatory.mainCamera.getImgAvgADU()
        print(f'{filterNdx} {binning} {imgAvgADU}')

# if not(flatDataFrame.done.all()):
#     telescopium.writeLog(True,observatory.currentState,'','Setting Camera temp')
#     observatory.mainCamera.setTempSetPoint(True,observatory.tempSetPointForTonight,True)
#     filePrefix = f"{observatory.tempSetPointForTonight}C"
#     while not(flatDataFrame.done.all()):
#         telescopium.writeLog(True,observatory.currentState,'','Top of loop')
#         telescopium.writeLog(True,observatory.currentState,'','updating for current time')
#         for indexInD, row in flatDataFrame[(flatDataFrame.done==False)].iterrows():
#             expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
#             expSeqTemp.exp=expMin
#             expSeqTemp.rep=1
#             observatory.mainCamera.takeImgSeq(observatory.mainFilter,False,expSeqTemp,observatory.filePathFlats,filePrefix)
#             imgAvgADU = observatory.mainCamera.getImgAvgADU()
#             #imgAvgADU = min(65000,(30000+7000*mainFilter.filterNdx[expSeqTemp.filterName])*expSeqTemp.exp)
#             flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp'] = expSeqTemp.exp
#             flatDataFrame.loc[flatDataFrame.index[indexInD], 'imgAvgADU'] = imgAvgADU
#             if (imgAvgADU<0.9*imgAvgADUMax):
#                 flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']   = flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp']*targetImgAvgADU/imgAvgADU
#                 if flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']>expMax:
#                     flatDataFrame.loc[flatDataFrame.index[indexInD], 'done'] = True
#                 telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('%-2d %-2d %4.2f %1d %5s %6.1f %4.2f'%(indexInD,flatDataFrame.loc[indexInD,'indexInflatExpBlk'],expSeqTemp.exp,expSeqTemp.bin,expSeqTemp.filterName,imgAvgADU,flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj'])).strip())
#         telescopium.writeLog(True,observatory.currentState,'','picking canidates')
#         canidates = flatDataFrame[(flatDataFrame.expProj>=expMin)&(flatDataFrame.done!=True)].index.values
#         telescopium.writeLog(True,observatory.currentState,'','running canidates')
#         for indexInD in canidates:
#             expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
#             expSeqTemp.exp=flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']
#             expSeqTemp.rep=1
#             observatory.mainCamera.takeImgSeq(observatory.mainFilter,False,expSeqTemp,observatory.filePathFlats,filePrefix)
#             imgAvgADU = observatory.mainCamera.getImgAvgADU()
#             #imgAvgADU = min(65000,(30000+7000*mainFilter.filterNdx[expSeqTemp.filterName])*expSeqTemp.exp)
#             flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp'] = expSeqTemp.exp
#             flatDataFrame.loc[flatDataFrame.index[indexInD], 'imgAvgADU'] = imgAvgADU
#             flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']   = flatDataFrame.loc[flatDataFrame.index[indexInD], 'exp']*targetImgAvgADU/imgAvgADU
#             telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('%-2d %-2d %4.2f %1d %5s %6.1f %4.2f'%(indexInD,flatDataFrame.loc[indexInD,'indexInflatExpBlk'],expSeqTemp.exp,expSeqTemp.bin,expSeqTemp.filterName,imgAvgADU,flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj'])).strip())
#             expSeqTemp = observatory.flatExpBlk.loc[flatDataFrame.loc[indexInD,'indexInflatExpBlk']].copy()
#             expSeqTemp.exp=flatDataFrame.loc[flatDataFrame.index[indexInD], 'expProj']
#             observatory.mainCamera.takeImgSeq(observatory.mainFilter,True,expSeqTemp,observatory.filePathFlats,filePrefix)
#             flatDataFrame.loc[flatDataFrame.index[indexInD], 'done'] = True
#         telescopium.writeLog(True,observatory.currentState,'','pace delay at bottom of loop')
#         time.sleep(10)
# else:
#     telescopium.writeLog(True,observatory.currentState,'',telescopium.ptos('Waiting %s hms to enter ReadyToObserve state'%(telescopium.deltaTimeTohms((observatory.timetoEnter_ReadyToObserve-Time.now())))).strip())



# for ndx in range(observatory.mainFilter.numbFilters):
#     exposure        = 1
#     binning         = 2
#     imageReduction  = 2
#     imageReduction  = 0
#     autoSaveFile    = False
#     asyncMode       = False
#     observatory.mainFilter.setFilterByNdx(ndx)
#     observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)

# for ndx in ['R','G','B','L','SII','OIII','Ha']:
#     exposure        = 1
#     binning         = 2
#     imageReduction  = 2
#     imageReduction  = 0
#     autoSaveFile    = False
#     asyncMode       = False
#     observatory.mainFilter.setFilterByName(ndx)
#     observatory.mainCamera.takeLightFrame(exposure,binning,imageReduction,autoSaveFile,asyncMode)



