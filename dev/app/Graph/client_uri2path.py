'''
Created on 2014. 11. 10.

@author: user
'''
import Orange
import networkx as nx
import log_uri2tree as lu2t


def getVisitGraph(ip, uri_dataSet):
    G = nx.DiGraph()
    '''
    try:
        ip_uri = Orange.data.Table([d for d in uri_dataSet if d['ip']==ip])
    except Orange.orange.KernelException:
        return G
    '''
    path = [ip]
    for d in uri_dataSet:
        try:
            path.append(lu2t.generateTreeLoc(d['query_uri'].value, ['/'], d['rcode'].value)[-1])
        except IndexError:
            pass
    for i in path:
        if i not in G.nodes():
            G.add_node(i,visited=0)
        G.node[i]['visited'] += 1
    for i in range(len(path)-1):
        G.add_edge(path[i], path[i+1])
    return G
