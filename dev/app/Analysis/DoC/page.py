'''
Created on 2014. 11. 26.

@author: biscuit
'''

def getDoCDist(_ip_DataSet):
    count_dict = {}
    for d in _ip_DataSet:
        try:
            count_dict[d["query_uri"].value] += 1
        except KeyError:
            count_dict[d["query_uri"].value] = 1
            continue
    return count_dict

def getMostConPage(_ip_DataSet):
    count_dict = getDoCDist(_ip_DataSet)
    conPage = max(count_dict, key=lambda x: count_dict[x])
    return conPage, _ip_DataSet.filter_ref(page=conPage)