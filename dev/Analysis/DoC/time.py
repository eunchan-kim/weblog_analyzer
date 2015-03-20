'''
Created on 2014. 11. 26.

@author: biscuit
'''
import numpy as np

def get_tHistogram(_timeList, resol):
    
    minT = int(min(_timeList))
    maxT = int(max(_timeList))
    t_Hist, t_bins = np.histogram(_timeList, bins=range(minT-1, maxT+resol, resol))
    return t_Hist/float(len(_timeList)), t_bins

def getDoC(t_ProbHist):
    sumProb = 0
    if len(t_ProbHist) > 1:
        for i in range(len(t_ProbHist)-1):
            sumProb += t_ProbHist[i]*(t_ProbHist[i]+t_ProbHist[i+1])
    return sumProb