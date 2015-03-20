'''
Created on 2014. 11. 26.

@author: biscuit
'''

def getDoCDist(_ip_DataSet):
    count_dict = {}
    for d in _ip_DataSet:
        try:
            count_dict[d["user-agent"].value] += 1 
        except KeyError:
            count_dict[d["user-agent"].value] = 1
            continue
        except TypeError:
            return
    return count_dict