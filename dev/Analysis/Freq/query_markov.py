'''
Created on 2014. 11. 14.

@author: user

'''
from __future__ import division
from Orange import data
from scipy import sparse as sp
import numpy as np
import math
from Analysis import split_session as ss
import Feature_Set as fs
import refine_data as rd

def getGeoMeanFrac(numer, denom):
    try:
        s = sum(map(math.log, numer))-sum(map(math.log, denom))
    except ValueError:
        return 1
    return math.e**(s/len(numer))

def getGeoMeanProb(probList):
    try:
        s = sum(map(math.log, probList))
    except ValueError:
        return 1
    return math.e**(s/len(probList))

def getGeoMeanScore(probList):
    try:
        s = sum(map(math.log, probList))
    except ValueError:
        return 0
    return -s/len(probList)


def markov_Count(DataSet, indexMap):
    pages = list(set([d['query_uri'].value for d in DataSet]))
    ips = list(set([d['ip'].value for d in DataSet]))
    numPages = len(pages)
    #numIPs = len(ips)
    
    p2n = {}
    for i, p in enumerate(pages):
        p2n[p]=i
    transCount = sp.lil_matrix((numPages, numPages))
    
    rowTotal = np.zeros(numPages)
    
    for IP in ips:
        try:
            _ip_Data = DataSet.get_items_ref(indexMap[IP])
        except KeyError:
            return 0
        sessions = ss.split_data(_ip_Data, 900)
        for s in sessions:
            for i in range(len(s)-1):
                cur = s[i]
                nxt = s[i+1]
                transCount[p2n[cur['query_uri'].value], p2n[nxt['query_uri'].value]] +=1
                rowTotal[p2n[cur['query_uri'].value]] += 1
    return p2n, transCount, rowTotal

def markov_getTransMat(transCount, rowTotal):
    numPages = len(rowTotal)
    transMat = sp.lil_matrix((numPages, numPages))
    for i, r in enumerate(rowTotal):
        if r == 0:
            continue
        transMat[i,:] = transCount[i,:]/r
    return transMat

def markov_anomalyScore(DataSet, IP, markowMat, p2n, indexMap):
    try:
        ip_Data = DataSet.get_items_ref(indexMap[IP])
    except KeyError:
        return 0
    pList = []
    sess = ss.split_data(ip_Data, 900)
    for s in sess:
        prob = getScoreSession(s, markowMat, p2n)
        pList.append(prob)
    if len(pList) == 0:
        return 0
    return max(pList)
    
def getScoreSession(DataSeq, markovMat, p2n):
    '''
    numer = []
    denom = []
    for i in range(len(DataSeq)-1):
        cur = DataSeq[i]
        nxt = DataSeq[i+1]
        try:
            numer.append(int(transCount[p2n[cur['query_uri'].value], p2n[nxt['query_uri'].value]]))
            denom.append(int(rowTotal[p2n[cur['query_uri'].value]]))
        except KeyError:
            continue
    if len(numer)== 0:
        return -1
    return getGeoMeanFrac(numer, denom)
    '''
    pList = []
    for i in range(len(DataSeq)-1):
        cur = DataSeq[i]
        nxt = DataSeq[i+1]
        try:
            pList.append(markovMat[p2n[cur['query_uri'].value], p2n[nxt['query_uri'].value]])
        except KeyError:
            continue
    if len(pList)== 0:
        return 1
    return getGeoMeanScore(pList)

def getTable(DataSet):
    P_Data = DataSet.filter_ref(rcode=['200'])
    indexMap = rd.getindexMap(P_Data)
    p2n, transCount, rowTotal = markov_Count(P_Data, indexMap)
    markovMat = markov_getTransMat(transCount, rowTotal)
    
    vDom = data.Domain([fs.ip, fs.page_freq], False)
    pageFreqTable = data.Table(vDom)
    ips = set([d['ip'].value for d in DataSet])
    for IP in ips:
        t = markov_anomalyScore(P_Data, IP, markovMat, p2n, indexMap)
        pageFreqTable.append([IP, max(0,t)])
    return pageFreqTable

'''
P_Data = Data.filter_ref(rcode=['200', '206'])  # <---Here's something wrong
p2n, transCount, rowTotal = markov_Count(P_Data)
PL = []
markovMat = markov_getTransMat(transCount, rowTotal)

ips = set([d['ip'].value for d in P_Data])
for ip in ips:
    t = markov_anomalyScore(P_Data, ip)
    print ip, t
    if t>=0:
        PL.append(t)

hist, bins = np.histogram(PL, bins=10)
with open(r"C:\outhist.txt", 'w') as f:
    for i in hist:
        f.write('*'*i+"\n")
        
print bins
'''