'''
Created on 2014. 12. 16.

@author: biscuit
'''

def remove_tiny(DataSet):
    ipList = list(set([x['ip'].value for x in DataSet]))
    count = {}.fromkeys(ipList, 0)
    refined = []
    for d in DataSet:
        count[d['ip'].value] += 1
    for k, v in count.iteritems():
        if v >= 4:
            refined.append(k)
    rData = DataSet.filter_ref(ip=refined)
    return rData
    
def getindexMap(DataSet):
    ipList = list(set([x['ip'].value for x in DataSet]))
    indexMap = {}.fromkeys(ipList)
    for i in indexMap:
        indexMap[i]= []
    for i, d in enumerate(DataSet):
        indexMap[d['ip'].value].append(i)
    return indexMap