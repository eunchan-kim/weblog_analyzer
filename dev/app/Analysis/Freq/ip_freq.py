'''
Created on 2014. 11. 29.

@author: biscuit
'''
from Orange import data
import Feature_Set as fs
import math

vDom = data.Domain([fs.ip, fs.ip_freq], False)

def getTable(DataSet):
    ipList = list(set([x['ip'].value for x in DataSet]))
    ipFreqTable = data.Table(vDom)
    freqList = []
    count = {}.fromkeys(ipList, 0)
    for d in DataSet:
        count[d['ip'].value] += 1
    for i in ipList:
        freqList.append([i, math.log(count[i])])
    ipFreqTable.extend(freqList)
    return ipFreqTable

