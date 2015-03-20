'''
Created on 2014. 12. 5.

@author: biscuit
'''
from Orange import data
from Analysis import OutDetect
from time import time
#import Feature_Set as fs

def getAnalysis(tab_fvec, Z, save_path):
    #DataSet = data.Table(tab_path)
    fVectors = data.Table(tab_fvec)
    DomainSet= {('Invalid Access', ('ip','ip_freq', 'status_DoC'), 5),
                ('Surge', ('ip','ip_freq', 'time_DoC', 'page_DoC'), 5),
                ('Frequent visits to unpopular pages', ('ip','ip_freq', 'page_freq'), 3),
                ('Repeated Requests to non-existing pages', ('ip','ip_freq', 'status_DoC', 'page_DoC'), 3),
                ('Obsession', ('ip','ip_freq', 'page_DoC'), 3),
                ('Diverse User Agents', ('ip','u_agent_DoC'), 1)
                }
    
    result = []
    
    for i, d, v in DomainSet:
        try:
            subVec = fVectors.translate(d)
            outIPs = OutDetect.getOutlierTable(subVec, Z)
            #lineList = [int(d['lineNo'].value) for d in outD]
            result.append((i, outIPs, v))
        except AttributeError:
            continue
    
    with open(save_path, 'w') as f:
        for g in result:
            f.write(str(g[0])+"(level %s)\n" % str(g[2]))
            f.write(str(g[1]))
            f.write("\n")
            
    return result

def main():
    t0 = time()
    getAnalysis(r"C:\a.tab", 4.0, r'C:\result.txt')
    t1 =time()
    print 'function vers1 takes %f' %(t1-t0)
    
    
if __name__ == '__main__':
    main()

             
    