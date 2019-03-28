#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 14:00:29 2019

@author: berend
"""

### test API:

from structs import AnalyzerRegion, DetectorRegion, DetectorInfo
from sesFunctions import SESWrapper
import ctypes
import numpy as np


if __name__ == '__main__':
    
    
    dllpath = 'C:\seswrapper_2.7.4_Win64\SESWrapper.dll'
    ses_dir = 'C:/SES_1.4.0-r30_Win64'
    ses_instrument = ses_dir + '/dll/SESInstrument.dll'
    inst_path =  ses_dir + '/data/9ES219L_Instrument.dat'

    
    ses = SESWrapper(dllpath)
    
    #following:
    #/Users/berend/Documents/temp/seswrapper/seswrapper/ftp.scienta.se/SES/SESWrapper/seswrapper_2.7.4_Win64/doc/html/examples_page.html

    print(ses.SetPropertyString('lib_working_dir'.encode('ASCII'),0,ses_dir.encode('ASCII')))
    print(ses.SetPropertyString('instrument_library'.encode('ASCII'),0,ses_instrument.encode('ASCII')))
    
    
    ##note: to get this to run, go to ses/ini/detectorgraph.ini
    # and set direct_viewer to false
    #if you do that, the ses software will not load the viewer on startup, 
    #but this will run successfuly     
    print(ses.Initialize(0))
    
    
    print(ses.LoadInstrument(inst_path.encode('ASCII')))
    
    
    print(ses.SetPropertyString('element_set'.encode('ASCII'), -1, 'Low Pass (Laser)'.encode('ASCII')))
    print(ses.SetPropertyString('lens_mode'.encode('ASCII'), -1, 'Transmission'.encode('ASCII')))
    
    Epass = ctypes.c_double(10)
    print(ses.SetPropertyDouble('pass_energy'.encode('ASCII'), -1, ctypes.byref(Epass)))
    
    
    ##set detector and analyzer
    
    info = DetectorInfo()
    print(ses.GetDetectorInfo(info))
    print('Number of x channels: ',info.xChannels_)

    detector = DetectorRegion()
    detector.firstXChannel_ = 0
    detector.lastXChannel_ = 500
    detector.firstYChannel_ = 0
    detector.lastYChannel_ = 500
    detector.slices_ = 1
    detector.adcMode_ = True
    
    print(ses.SetDetectorRegion(detector))
    
    
    analyzer = AnalyzerRegion()
    analyzer.fixed_ = False
    analyzer.highEnergy_ = 90
    analyzer.lowEnergy_ = 82
#    analyzer.centerEnergy_ = 86
    analyzer.energyStep_ = 0.2
    analyzer.dwellTime_ = 500

    print(ses.SetAnalyzerRegion(analyzer))
    
    #test:
    analyzer2 = AnalyzerRegion()
    print(ses.GetAnalyzerRegion(analyzer2))
    
    print('Returned analyzer has lowenergy', analyzer2.lowEnergy_)
    
    
    
    ses.InitAcquisition(False, True)
    channels = ctypes.c_int(0)
    channels_size = ctypes.c_int(0)
    print(ses.GetAcquiredDataInteger('acq_channels'.encode('ASCII'), 0, ctypes.byref(channels), ctypes.byref(channels_size)))

    spectrum = (ctypes.c_double * 200)() ## can be oversized
    
    print('Generated spectrum has size:', ctypes.sizeof(spectrum))
    
    for i in range(10):
        print(ses.StartAcquisition())
        print(ses.WaitForRegionReady(-1))
        print(ses.ContinueAcquisition())
    
    ## acq_spectrum will write the size back to &channels
    print(ses.GetAcquiredDataVectorDouble('acq_spectrum'.encode('ASCII'), 0, spectrum, ctypes.byref(channels)))
          
    
    
    spectrum_np = np.array(spectrum)
    
    np.savetxt('test.txt',spectrum_np)
    
    print(ses.Finalize())
    
    
    
### note: here they do a similar thingk, passing an array by reference, seems like 
### the way I do it should work:
#https://stackoverflow.com/questions/51867653/passing-stdvector-from-c-to-python-via-ctypes-getting-nonsensical-values
# actually: they "cheat" by copying the vector to an array. So I see two ways out:

# one: make another shared library, that does the data conversion through some function
    
    
# two: make a class in another shared library, that has a vector at its core and 
# does read/write operations so you can access the data. A pointer can be shared
# for accessing the vector
# Here: https://stackoverflow.com/questions/16885344/how-to-handle-c-return-type-stdvectorint-in-python-ctypes (second answer)
    





