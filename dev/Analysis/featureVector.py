'''
Created on 2014. 11. 26.

@author: user
'''
from Orange import data
from DoC import page, time as t, status, user_agent 
import split_session as ss
import Feature_Set as fs
import refine_data as rd
from Analysis.Freq import ip_freq
from Analysis.Freq import query_markov
from time import time

vDom = data.Domain([fs.ip, fs.DoC_t, fs.DoC_p, fs.DoC_ua, fs.DoC_s], False)

def SimpsonIndex_count(basket):
    S = sum(basket)
    if S < 2:
        return 0
    R = sum([x*(x-1) for x in basket if x > 1]) 
    return float(R)/(S*(S-1))

def SimpsonIndex_prob(probDistbasket):
    return sum([p*p for p in probDistbasket])

def getDoCInstance(_ip_DataSet, IP):
    #ip_freq.add_value(IP)
    result = [IP]
    t_Data = [d["t_offset"].value for d in _ip_DataSet]
    sessList = ss.split_time(t_Data, 900)
    timeDoC = 0
    for s in sessList:
        t_hist, t_bins = t.get_tHistogram(s, 15)
        timeDoC = max([timeDoC, t.getDoC(t_hist)])   
    ua_Dist = user_agent.getDoCDist(_ip_DataSet)
    p_Dist = page.getDoCDist(_ip_DataSet)
    result.append(timeDoC)
    result.append(SimpsonIndex_count(p_Dist.values()))
    try:
        result.append(1-SimpsonIndex_count(ua_Dist.values()))
    except AttributeError:
        result.append(None)
    result.append(status.get_404ratio(_ip_DataSet))
    return result

def getDoCTable(DataSet, indexMap):
    ip_List = list(set([x['ip'].value for x in DataSet]))
    DoC_Table = data.Table(vDom)
    DoCList = []
    for i in ip_List:
        DoCList.append(getDoCInstance(DataSet.get_items_ref(indexMap[i]), i))
    DoC_Table.extend(DoCList)
    return DoC_Table

def DoC_filtering(DataSet, DoCTable, t_range=(0,1), u_range=(0,1), p_range=(0,1), s_range=(0,1)):
    filtered = DoCTable.filter_ref({"time_DoC": t_range,
                                    "u_agent_DoC": u_range,
                                    "page_DoC": p_range,
                                    "status_DoC": s_range
                                    })
    ip_List = [d["ip"].value for d in filtered]
    return DataSet.filter_ref(ip=ip_List), ip_List

def getFeatureVectors(DataSet, indexMap):
    DoCT = getDoCTable(DataSet, indexMap)
    ipFT = ip_freq.getTable(DataSet)
    pageFT = query_markov.getTable(DataSet)
    Merged = data.Table([DoCT, ipFT, pageFT])
    return Merged

def extract_feature(data_path, save_path):
    DataSet = data.Table(data_path) 
    rData = rd.remove_tiny(DataSet)
    indexMap = rd.getindexMap(rData)
    Feat_Table = getFeatureVectors(rData, indexMap)
    Feat_Table.save(save_path)

def main():
    
    data_path = raw_input("path > ")
    save_path = raw_input("save path > ")
    extract_feature(data_path,save_path)
    #DoCT = getFeatureVectors(Data)
    #Save_path = raw_input("save path > ")
    
if __name__ == '__main__':
    main()
    