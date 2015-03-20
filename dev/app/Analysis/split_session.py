'''
Created on 2014. 11. 27.

@author: biscuit
'''

def split_time(time_list, threshold):
    if len(time_list) == 0:
        return []
    session_list = []
    sess = []
    sess.append(time_list.pop(0))
    while len(time_list) != 0:
        if abs(time_list[0]-sess[-1]) > threshold:
            session_list.append(sess)
            sess = []
        sess.append(time_list.pop(0))
    session_list.append(sess)
    return session_list


def split_data(_ip_DataSet, threshold):
    if len(_ip_DataSet) == 0:
        return []
    zero_vec = [0]*len(_ip_DataSet)
    session_list = []
    sel = []
    v = zero_vec[:]
    for i, d in enumerate(_ip_DataSet):
        v[i] = 1
        if i == len(_ip_DataSet)-1:
            continue
        if abs(_ip_DataSet[i+1]['t_offset'].value-d['t_offset'].value) > threshold:
            sel.append(v)
            v = zero_vec[:]
    for w in sel:
        session_list.append(_ip_DataSet.select_ref(w))
    return session_list