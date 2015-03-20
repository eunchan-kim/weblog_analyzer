'''
Created on 2014. 11. 11.

@author: user
'''
from Orange import data, feature
import networkx as nx
import matplotlib.pyplot as plt
import log_uri2tree as lu2t
import client_uri2path as cu2p
import os
'''
def getVertexAddedDotPos(Graph, vertexList):
    G = Graph.copy()
    G.add_nodes_from(vertexList)
    G.add_node("http://..")
    return nx.graphviz_layout(G,prog='dot')
'''
def getVertexAddedDotPos(pos, vertex):
    pos[vertex] = (pos['/'][0], pos['/'][1]+20)
    pos["not_found"] = (pos['/'][0]-45000, pos['/'][1])
    pos["http://.."] = (pos['/'][0]+20000, pos['/'][1])
    return pos

Data = data.Table(r"E:\BoB\Project\log\gon_log\tab\access.log.tab")

P_Data = Data.filter_ref(rcode = ['200', '206', '404'], query_method = ["GET", "POST"]) #and (d['query_method'].value in ['GET', 'POST'])])
clients_ip = P_Data.domain.attributes[0].values
num_clients = len(clients_ip)

G = lu2t.getURITree(P_Data)

pos = nx.graphviz_layout(G,prog='dot')
pos = getVertexAddedDotPos(pos, '__client')

D = P_Data.domain["date"]
I = P_Data.domain["ip"]

date_f = data.filter.SameValue(position = P_Data.domain.features.index(D))
ip_f = data.filter.SameValue(position = P_Data.domain.features.index(I))

plt.figure(figsize=(30,10))
count = 0
for ip in clients_ip:
    count += 1
    print "(%d/%d)" %(count, num_clients)
    ip_f.value = data.Value(I, ip)
    try:
        os.mkdir('E:\\BoB\\Project\\log\\gon_log\\graph\\'+ ip)
    except WindowsError:
        continue
    ip_data = ip_f(P_Data)
    ip_date = ip_data.domain.attributes[1].values
    for date in ip_date:
        date_list = date.split("/")
        date_list.reverse()
        date_dir = "_".join(date_list)
        date_f.value = data.Value(D, date)
    
        filtered = date_f(ip_data)
        if len(filtered) == 0:
            continue
        with open(r'E:\BoB\Project\log\gon_log\graph\%s\%s.txt' % (ip, date_dir), 'w' ) as f:
            for i in filtered:
                f.write(str(i)+"\n")
        K = cu2p.getVisitGraph(ip, filtered)
        if K.number_of_edges() == 1:
            continue
        nx.relabel_nodes(K, {ip:"__client"}, False)
        nx.draw(G,pos,node_size=10,alpha=0.1, node_color="blue",with_labels=False, arrows=False)
        nx.draw_networkx(K, pos, node_size=[K.node[i]['visited']*10 for i in K.nodes()], edge_color="red" ,alpha=0.5, with_labels=False)
        #base.imshow(img)
        plt.savefig(r'E:\BoB\Project\log\gon_log\graph\%s\%s.png' % (ip, date_dir))
        plt.clf()

