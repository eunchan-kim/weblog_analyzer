'''
Created on 2014. 11. 26.

@author: biscuit
'''


def get_404ratio(_ip_DataSet):
    subData_404 = _ip_DataSet.filter_ref(rcode = '404')
    return float(len(subData_404))/len(_ip_DataSet)

def get_404Table(_ip_DataSet):
    return _ip_DataSet.filter_ref(rcode= '404')
