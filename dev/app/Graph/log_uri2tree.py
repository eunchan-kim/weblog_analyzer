'''
Created on 2014. 10. 31.

@author: biscuit
'''

import Orange
import networkx as nx

def generateTreeLoc(uristr,loc_sq, rcode):
    if rcode == '404' and uristr != '/favicon.ico':
        return ['not_found']
    if rcode[0] != '2':
        return []
    if uristr.startswith("http") and loc_sq==['/']:
        return ["http://.."]
    if uristr == None:
        return loc_sq
    if uristr == "":
        #loc_sq.append(loc_sq[-1]+"i")
        return loc_sq
    '''
    if(uristr.find("?")>=0):
        uri_path = uristr[:uristr.find("?")]
        temp = generateTreeLoc(uri_path, loc_sq, rcode)
        #temp.append(uri_arg)
        return temp
    '''
    if(uristr[0]=='/'):
        if loc_sq==['/']:
            return generateTreeLoc(uristr[1:], loc_sq, rcode)
        loc_sq.append(loc_sq[-1]+'/')
        return generateTreeLoc(uristr[1:], loc_sq, rcode)
    
    if uristr.find('/') < 0:
        loc_sq.append(loc_sq[-1]+uristr)
        return loc_sq
    else :
        loc_sq.append(loc_sq[-1]+uristr[:uristr.find('/')]+'/')
        return generateTreeLoc(uristr[uristr.find('/')+1:], loc_sq, rcode)
    
def getURITree(uri_dataSet):
    G = nx.DiGraph()
    for d in uri_dataSet:
        G.add_path(generateTreeLoc(d['query_uri'].value, ['/'], d['rcode'].value))
    return G


