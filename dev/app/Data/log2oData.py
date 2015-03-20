'''
Created on 2014. 10. 10.

@author: biscuit

I apply def component()!!
'''
import os
import datetime
import random

month_map = {'Jan':1, 'Feb':2,'Mar':3,'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12 }
Mon_List = [['Jan', '1'], ['Feb', '2'], ['Mar', '3'], ['Apr', '4'], ['May', '5'], ['Jun', '6'], ['Jul', '7'], ['Aug', '8'], ['Sep', '9'], ['Oct', '10'], ['Nov', '11'], ['Dec', '12']]

def is_xss(uri):
    if "<script" in uri or "alert(" in uri:
        return True
    else:
        return False

def is_bot(user_agent, uri, status):
    if not is_sqlinjection(uri) and not is_xss(uri) and not "Mozilla" in user_agent and not "Opera" in user_agent and not "WebKit" in user_agent and not "Apache" in user_agent and user_agent != "." and status != "408":
        return True
    else:
        return False

def is_sqlinjection(uri):
    if ("sel" in uri and "%20" in uri) or "substr" in uri or "union" in uri or ("select" in uri and "from" in uri):
        return True
    else:
        return False

def time2int(td):
    return td.days * 24 * 3600 + td.seconds  

def isip(c):
    temp = False
    for i in c:
        
        if ord(i) == 46:
            temp = True
        if ord(i) == 46 or (ord(i) >= 48 and ord(i) <= 57):
            continue
        else:
            return False
    return temp

def istime(c):    
    if c[0] == "[":
        return True
    return False

def isuri(c):
    if c.find("GET") >= 0 or c.find("POST") >= 0:
        return True
    return False

def isstatus(c):
    for i in c:
        if ord(i) >= 48 and ord(i) <= 57:
            continue
        else:
            return False
    if int(c) > 99 and int(c) < 103:
        return True
    if int(c) > 199 and int(c) < 209:
        return True
    if int(c) > 299 and int(c) < 309:
        return True
    if int(c) > 399 and int(c) < 450:
        return True
    if int(c) > 499 and int(c) < 512:
        return True
    if int(c) == 598 or int(c) == 599:
        return True
    return False

def isresponse_length(c):
    for i in c:
        if ord(i) >= 48 and ord(i) <= 57:
            continue
        return False    
    if isstatus(c):
        return False
    return True

def isuser_agent(c):
    s = ["Android", "iPhone", "Mozilla", "AppleWebKit", "Chrome", "Windows NT", "Gecko", "KHTML", "Safari", "CoolNovo", "Firefox", "Linux", "Build", "Internet Explorer"]
    for i in s:
        if c.find(i) >= 0:
            return True
    return False

def isreferer(c):
    return c.find("http") != -1
def quotation(s):
    cnt = 0
    for i in s:
        if '"' == i:
            cnt = cnt + 1
    return cnt
def component(path): # return ip, time, uri, status, response_length, user_agent index
    dataset = open(path, 'r').readlines()
    num = [0] * 100
    cnt = min(100, len(dataset))
    for i in range(cnt):
        c = dataset[i]
        if quotation(c) > 80:
            num[80] = num[80] + 1
        else:
            num[quotation(c)] = num[quotation(c)] + 1

    tmax = 0
    imax = 0
    for i in range(85):
        if num[i] > tmax:
            imax = i
            tmax = num[i]
   
    ip = [0] * 20
    ipindex, timeindex, uriindex, statusindex, rlindex, uaindex, rfindex = -1, -1, -1, -1, -1, -1, -1
    time = [0] * 20
    uri = [0] * 20
    status = [0] * 20
    response_length = [0] * 20
    referer = [0] * 20
    user_agent = [0] * 20
    for tt in range(cnt):
        n = random.randint(0, len(dataset)-1)
        i = dataset[random.randint(0, n)]
        try:
            if quotation(i) != imax:
                continue
       
            fi = -1
            ti = -1
            ci = 0
            bi = -1
            comp = [""] * 20
            for j in range(len(i)): # split with null space, but the sentence which includes in quotation not split.
           
            
                if i[j] == "[":
                    ti = j
                if i[j] == "]":
                    ti = -1
            
                if i[j] == '"':                
                    if fi == -1:
                        fi = j
                    else:
                        fi = -1
                
                
                if ord(i[j]) == 32:                
                    if fi == -1 and ti == -1:
                        comp[ci] = i[bi+1:j]
                        bi = j
                        ci = ci + 1
                if j == len(i)-1 and j != '"':
                    comp[ci] = i[bi:j+1]
            for j in range(20):
                if comp[j] == '':
                    continue
                if isip(comp[j]):
                    ip[j] = ip[j] + 1
                if istime(comp[j]):
                     time[j] = time[j] + 1
                if isuri(comp[j]):
                    uri[j] = uri[j] + 1
                if isstatus(comp[j]):
                    status[j] = status[j] + 1
                if isresponse_length(comp[j]):
                    response_length[j] = response_length[j] + 1
                if isuser_agent(comp[j]):
                    user_agent[j] = user_agent[j] + 1
                if isreferer(comp[j]):
                    referer[j] = referer[j] + 1
        except:
            continue

    tm = 0
    for i in range(20):
        if ip[i] > tm and float(ip[i]) / cnt > 0.5:
            tm = ip[i]
            ipindex = i
    tm = 0
    for i in range(20):
        if time[i] > tm and float(time[i]) / cnt > 0.5:
            tm = time[i]
            timeindex = i
    tm = 0
    for i in range(20):
        if uri[i] > tm and float(uri[i]) / cnt > 0.5:
            tm = uri[i]
            uriindex = i
    tm = 0
    for i in range(20):
        if status[i] > tm and float(status[i]) / cnt > 0.5:
            tm = status[i]
            statusindex = i
    tm = 0
    for i in range(20):
        if response_length[i] > tm and float(response_length[i]) / cnt > 0.5:
            tm = response_length[i]
            rlindex = i
    tm = 0
    for i in range(20):
        if user_agent[i] > tm  and float(user_agent[i]) / cnt > 0.5:
            tm = user_agent[i]
            uaindex = i
    tm = 0
    for i in range(20):
        if referer[i] > tm and float(referer[i]) / cnt > 0.5:
            tm = referer[i]
            rfindex = i
    #print referer
    return ipindex, timeindex, uriindex, statusindex, rlindex, rfindex, uaindex

def MyownOrange(path, path2, path3): # path2 : output path3 : error path
    index = component(path) # ip, time, uri, status, response_length, referer, user_agent index

    with open(path,"r") as k:
        with open(path2, "w") as g:
            g.write("ip\tdate\ttime\tt_offset\tquery_method\tquery_uri\turi_parameter\trcode\tlength\treferer\tuser-agent\tvalid_query\tvalid_ua\tlineNo\n")
            g.write("s\td\ts\tc\td\ts\ts\td\tc\ts\ts\td\td\tc\n")
            g.write("\tm\tm\t\tm\t\t\t\t\t\tm\tm\tm\tm\n")


            num = [0] * 100
            f = k.readlines()
            for i in range(min(100, len(f))):
                c = f[i]
                if quotation(c) > 80:
                    num[80] = num[80] + 1
                else:
                    num[quotation(c)] = num[quotation(c)] + 1

            tmax = 0
            imax = 0
            dt_Pivot = datetime.datetime.strptime("[01/01/2012:01:01:01", "[%d/%m/%Y:%H:%M:%S")
            for i in range(85):
                if num[i] > tmax:
                    imax = i
                    tmax = num[i]   
            lineNo = 0
            for i in f:
                lineNo = lineNo + 1
                try:
                    if quotation(i) != imax:
                        with open(path3, "a") as h:
                            h.write(i)
                        continue
       
                    fi = -1
                    ti = -1
                    ci = 0
                    bi = -1
                    comp = [""] * 20
                    for j in range(len(i)): # split with null space, but the sentence which includes in quotation not split.
                        if i[j] == "[":
                            ti = j
                        if i[j] == "]":
                            ti = -1
            
                        if i[j] == '"':                
                            if fi == -1:
                                fi = j
                            else:
                                fi = -1
                        if ord(i[j]) == 32:                
                            if fi == -1 and ti == -1:
                                comp[ci] = i[bi+1:j]
                                bi = j
                                ci = ci + 1
                        if j == len(i)-1 and j != '"':
                            comp[ci] = i[bi:j+1]
                    ip = "."
                    if index[0] != -1:
                        ip = comp[index[0]]

                        
                    date = "."
                    time = "."
                    t_offset = 0
                    if index[1] != -1:                        
                        ttt = comp[index[1]].split(":")
                        date = ttt[0][1:]
                        time = ttt[1]+":"+ttt[2]+":"+ttt[3].split()[0]                    
                        ttt = comp[index[1]].split()[0]
                        for j in Mon_List:
                            ttt = ttt.replace(j[0], j[1])    
                        t_offset = time2int(datetime.datetime.strptime(ttt, "[%d/%m/%Y:%H:%M:%S") - dt_Pivot)
                

                    query_method = "."
                    query_uri = "."
                    uri_parameter = "."

                    if index[2] != -1:
                        query_method = comp[index[2]].split()[0][1:]
                        query_uri = comp[index[2]].split()[1].split('?')[0]
                        if comp[index[2]].split()[1].find('?') == -1:
                            uri_parameter = "."
                        else:
                            uri_parameter = comp[index[2]].split()[1].split('?')[1]

                    rcode = "0"
                    if index[3] != -1:
                        rcode = comp[index[3]]

                    length = "0"
                    if index[4] != -1:
                        length = comp[index[4]]

                    user_agent = "."
                    if index[6] != -1:
                        user_agent = comp[index[6]]
                        user_agent = user_agent.strip('"')
                        user_agent = user_agent.strip('\n')

                    referer = "."
                    if index[5] != -1 and comp[index[5]].find("http") > -1:
                        referer = comp[index[5]].strip('"')

                    valid_query = 0
                    valid_ua = 0
                    
                    if is_xss(query_uri) or is_sqlinjection(query_uri):
                        valid_query = 1
                    if is_bot(user_agent, query_uri, rcode):
                        valid_ua = 1                    
                    
                    if ip == "::1":
                        continue
                    par = [ip, date, time, str(t_offset), query_method, query_uri, uri_parameter, rcode, length, referer, user_agent, str(valid_query), str(valid_ua), str(lineNo)]
                    
                    g.write("\t".join(par)+"\n")

                except:
                    with open(path3, "a") as h:
                        h.write(i)
                    continue

#MyownOrange(r"C:\localhost-access_log_2014_11_06.log", r'C:\a.tab', r"C:\a.err")