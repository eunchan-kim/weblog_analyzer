'''
Created on 2014. 12. 4.

@author: biscuit
'''
from Orange import data, distance

def getOutlierTable(feature_vectors, Z):
    
    outDetect = data.outliers.OutlierDetection()
    outDetect.set_examples(feature_vectors)
    outDetect.set_knn(1)
    z_values = outDetect.z_values()
    outIPs = [f['ip'].value for i, f in enumerate(feature_vectors) if z_values[i]>=Z]
    #outData = DataSet.filter_ref(ip = outIPs)
    return outIPs
