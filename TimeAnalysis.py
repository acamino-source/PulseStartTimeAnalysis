# Pulse time analysis
# explanation of the wfm format from the begining
import struct
import numpy as np
from array import array
from ROOT import TCanvas, TGraph, TH1F, TFile, TH2F
import peakutils

import sys  # for command-line input

# some input
tempStr = "filelist_"
filehead = sys.argv[1]  # ask user for data directory input
filelistStr = tempStr + filehead + ".txt"
rtfileoutputStr = filehead + "_result.root"
# dataDirectory = "/media/disk_a/ICARUS/2019NovData_decoded/" + filehead + "/"
print("Analyzing data from " + filehead + ". Files listed in " + filelistStr)

# some constants
NSamples = 50000  # number of data points in one waveform
tpt = 2.0  # time interval between sample points, in ns.
NCH = 4  # number of PMTs # check
QFactor = tpt / 50.0 * 1000.0  # convert V*ns/50Ohm to charge in pC
Nsigma = 10

# divided by 4 because 4 PMTs in group
Nwaves = len(open(filelistStr).readlines()) / 4
#print "number of waveforms in this run: ", Nwaves

  # Prepare for histograms 
  
  hPulseStartTime_list = []  # start time of the pulse
  # time distribution of the pulses that are not due to fiber trigger (ie., dark pulses or else)
  hPulseTimeDist_list = []
  # time distribution of the pulses that are not due to fiber trigger (ie., dark pulses or else)

  hWaveAvg_list = []  # average of raw waveforms
  
  # special test on time difference between the first channel
  hTimeDiff = TH1F("hTimeDiff", "Time diference", 100, -10, 10)  # unit in ns
  hTimeDiff.SetXTitle("Time difference (ns)")
  hTimeDiff.SetYTitle("N")
  
  for i in range(0, NCH, 1):
  # pulse start time, only choose those pulses above threshold
  name = "PulseStartTime_" + str(i)
        hist = TH1F(name, "", 200, 100, 300)
        hist.SetXTitle("Pulse start time bin (1.6 ns/bin)")
        hist.SetYTitle("Counts")
  hPulseStartTime_list.append(hist)

  # process the waveform
  for ch in range(NCH):
    for waveNb in range(Nwaves):
      afilename = f.readline().rstrip()
      awave = np.asarray(decode_wfm(afilename))
      
      baseline_mean = np.average(awave[NSamples - 1000:NSamples])
      baseline_width = np.std(awave[NSamples - 1000:NSamples])
	    threshold = baseline_mean - Nsigma * baseline_width
      TimeBinOfAmplitude = np.argmin(awave[70:800]) + 70

      # get charge integration about the amplitude: 20.8 ns before to 36.8 ns after the amplitude
      sumcharge = np.sum(awave[TimeBinOfAmplitude - 13:TimeBinOfAmplitude + 23])
      pulsestartbin = TimeBinOfAmplitude
      while awave[pulsestartbin] < threshold and pulsestartbin >= TimeBinOfAmplitude - 20:
            pulsestartbin -= 1
            hPulseStartTime_list[ch].Fill(pulsestartbin - 1)
            
      # search for number of pulses
            peakindex = peakutils.peak.indexes(-1.0 * awave[0:NSamples], thres=-1.0 * threshold, min_dist=31, thres_abs=True)
                
      for pulse_i in range(len(peakindex)):
         # skip pulse if it is below threshold in magnitude
         if awave[peakindex[pulse_i]] > threshold:
          continue
                    
         hPulseTimeDist_list[ch].Fill(peakindex[pulse_i])  # +TimeBinOfAmplitude+200
                    
# write results
resultsDir.cd()
for i in range(0, NCH, 1):
    hPulseStartTime_list[i].Write()
for i in range(0, NCH, 1):
     hPulseTimeDist_list[i].Write()
     print "number of pulses: ", hPulseTimeDist_list[i].GetEntries()
