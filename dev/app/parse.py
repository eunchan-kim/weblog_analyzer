"""
Eunchan Kim
"""
import sys
import operator
import collections
from bson.objectid import ObjectId
import pymongo
import zlib
import json
import bson

def parse_line(line):
  
  #print line
  if "HTTP/1.0" in line:
    delim = "1.0\""
  elif "HTTP/1.1" in line:
    delim = "1.1\""
  else:
    #print "parse error at " + line
    l = line.split("\"")
    result = {}
    first = l[0].split()
    last = l[-1].split()
    
    if len(last) > 0:
      result["ip"] = first[0]
      result["time"] = first[3] + " " + first[4]
      result["uri"] = (" ").join(l[1:-1])
      result["status"] = last[0]
      result["response_length"] = last[1]

      if len(last) != 4:
        result["user_agent"] = "-"
      else:
        result["user_agent"] = last[3]
      return result
    
    else:
      try:
        first = line.split()
        return {"ip":first[0], "time" : first[3] + " " + first[4], "uri":first[5], "status": first[6], "response_length": first[7], "user_agent":first[8]}
      except IndexError:
        return {"ip":first[0], "time" : first[3] + " " + first[4], "uri":"parsing error", "status": "parsing error", "response_length": "parsing error", "user_agent": "parsing error"}

  
  l = line.split(delim)
  result = {}
  first = l[0].split()
  last = l[-1].split()
  

  result["ip"] = first[0]

  result["time"] = first[3] + " " + first[4]
  result["uri"] = "\"" + (" ").join(first).split("\"")[1]+delim

  if len(last) > 0:
    result["status"] = last[0]
    result["response_length"] = last[1]
    if len(last) <= 4:
      result["user_agent"] = "-"
    else:
      result["user_agent"] = (" ").join(last[3:])
    return result

  else:
    second = l[1].split()

    if len(second) > 0:
      result["status"] = second[0]
      result["response_length"] = second[1]
      result["user_agent"] = (" ").join(second[3:])

      return result
    else:
      return {"ip":first[0], "time" : first[3] + " " + first[4], "uri":"parsing error", "status": "parsing error", "response_length": "parsing error", "user_agent": "parsing error"}


def get_log_from_number(filename, num_list):
  f = open("/home/kec/uploads/"+filename)

  i = 0
  result = []

  for log in f:
    if len(num_list) == 0:
      break
    if i in num_list:
      result.append(log)
      num_list.remove(i)
    i += 1

  return result


def dic_to_string(dic):
#  string = "ip: " + dic["ip"] + " time: " + dic["time"] + " URI: " + dic["uri"] + " status: " + dic["status"]
  string = dic["ip"] + " - - " + dic["time"] + " " + "\""+ dic["uri"] + "\"" + " " + dic["status"] + " " + dic["response_length"] + " " + dic["user_agent"]
  return string

def is_404(dic, not_found): # dic's type is dictionary
  ip = dic["ip"]
  not_used = []
  if dic["status"] == "404" and not is_xss(dic, not_used) and not is_bot(dic, not_used) and not is_xss(dic, not_used) and not "favicon" in dic["uri"]:
#    print dic_to_string(dic)

    not_found[ip] = not_found.get(ip, 0) + 1

def is_xss(dic, xss):
  uri = dic["uri"].lower()
  if "<script" in uri or "alert(" in uri:
    xss.append(dic)
    return True
  else:
    return False

def is_bot(dic, bot):
  user_agent = dic["user_agent"]
  not_used = []
  if not is_sqlinjection(dic, not_used) and not is_xss(dic, not_used) and not "Mozilla" in user_agent and not "Opera" in user_agent and not "WebKit" in user_agent and not "Darwin" in user_agent and not "Apache" in user_agent and user_agent != "-" and dic["status"] != "408":
    bot.append(dic)
    return True
  else:
    return False

sql_injection_signature = [["sel", "%20"], "substr", "union", ["select", "from"]]

def contain_signature(uri, signatures):
  for signature in signatures:
    
    if type(signature) == type(["list"]): # if list
      for sig in signature:
        result = True
        if sig in uri:
          result = result and True
        else:
          result = False
        if result:
          return True
          
      return True
    else:
      if signature in uri:
        return True
  return False

def is_sqlinjection(dic, sql_injection): #dic's type is dictionary
  uri = dic["uri"].lower()
  if ("sel" in uri and "%20" in uri) or "substr" in uri or "union" in uri or ("select" in uri and "from" in uri):
    sql_injection.append(dic)
#  if contain_signature(uri, sql_injection_signature):
#    sql_injection.append(dic)
    return True
  else:
    return False

def cluster_by_date(dic, time_list): 
  tmp = dic["time"].split(":") # ex) dic["time"] = "[09/Jun/2014:09:02:29 +0900]"
  date = tmp[0][1:] # ex)  09/Jun/2014
  time = (":").join(tmp[1:4])[0:-1] # ex) 09:02:29 +0900
  time_list[date] = time_list.get(date, 0) + 1

def get_ip_list(log_list):
  result = []
  for log in log_list:
    if len(log) > 10: # log is string
      #print "log is string"
      parsed = parse_line(log)
    else:   #log is dic
      parsed = log


    if parsed["ip"] not in result:
      result.append(parsed["ip"])
  return result

def process(filename, search_id="default"): # (return 404_list, sql_list, time_list, scanning_list, xss_list, bot_list, log_number)

  if search_id == "default":
    f = open("/home/kec/uploads/"+filename)
  else:
    connection = pymongo.MongoClient("mongodb://localhost")
    db = connection.test
    people = db.people
    cursor = people.find({"_id":ObjectId(search_id)})
    f = cursor[0]["list"]

  not_found_list = {}
  sql_list = []
  xss_list = []
  bot_list = []
  #time_list = {}
  time_list = collections.OrderedDict() # used OrderedDict to maintain the order of "date"

  log_number = 0

  for line in f:

    log_number += 1
    if not "::1" in line:
      result = parse_line(line)
  #    string = "ip: " + result["ip"] + " time: " + result["time"] + " URI: " + result["uri"] + " status: " + result["status"] 

      is_404(result, not_found_list)
      is_sqlinjection(result,sql_list)
      is_xss(result, xss_list)
      is_bot(result, bot_list)
      cluster_by_date(result, time_list)

  if search_id == "default":
    f.close()
  

  #print "log number is " + str(log_number)
  ret_1 = []  # ret_1 is a list of dics which saves the number of 404 requests per individual ip address
  for ip in not_found_list: # ip is key of not_found_list(dic)
    tmp = {}
    tmp["ip"] = ip
    tmp["num"] = not_found_list[ip]
    ret_1.append(tmp)
  
  
  ret_3 = []
  for date in time_list: # date is key of time_list(dic)
    tmp = {}
    tmp["date"] = date
    tmp["num"] = time_list[date]
    ret_3.append(tmp)

  ret_4 = [] # scanning ip lists

  for dic in ret_1:
    if dic["num"] > 1000:
      ret_4.append((dic["ip"]))

  phpmyadmin_list = search_keyword(keyword="scripts/setup.php", filename=filename, search_id=search_id, result="404")
  malicious_redirect = search_keyword(keyword=None, filename=filename, search_id=search_id, result="302", URI="www")

  return [ret_1, sql_list, ret_3, ret_4, xss_list, bot_list, log_number, phpmyadmin_list, malicious_redirect]

# function for remove duplicate elements in list
def remove_duplicate(l):
  result = []
  for elem in l:
    if not elem in result:
      result.append(elem)
  return result

# takes sql_injection logs, xss logs. scanning_ip and filename or search_id.
# and then return {attack: number} list, suspicious ip list, attack count per each day.
# and then save all the logs in database and also return object id. 
def make_statistics(sql_list, xss_list, bot_list, scanning_list, filename, search_id, phpmyadmin_list, malicious_redirect):
  sql_number = len(sql_list)
  xss_number = len(xss_list)
  bot_number = len(bot_list)
  scanning_number = 0
  scanning_logs = [] # for saving scanning logs. 

  phpmyadmin_ip_list = get_ip_list( phpmyadmin_list )
  malicious_redirect_ip = get_ip_list( malicious_redirect )

  time_list = collections.OrderedDict() # for counting traffic per day

  
  for ip in scanning_list:
    logs = search_keyword(filename=filename, search_id=search_id, keyword=None, result="404", ip=ip, not_include="favicon")
       
    scanning_number += len(logs)
    scanning_logs += logs

  scanning_number += len(phpmyadmin_list)
  scanning_logs += phpmyadmin_list
  scanning_list += phpmyadmin_ip_list
  scanning_list = remove_duplicate(scanning_list)
  

  #scanning_logs = []
  attack_and_number = [{"attack": "Sql injection", "num":sql_number}, {"attack": "Xss", "num":xss_number}, {"attack":"Scanning", "num": scanning_number}, {"attack":"Abnormal user-agent", "num": bot_number},{"attack":"Malicious redirect", "num":len(malicious_redirect)} ]
  suspicious_ip = []
  ip_list = []
  #print scanning_list

  for dic in sql_list:
   # if not dic["ip"] in ip_list:
      suspicious_ip.append({"ip": dic["ip"], "attack": "Sql injection"})
      ip_list.append(dic["ip"])
      cluster_by_date(dic, time_list)
  for dic in xss_list:
   # if not dic["ip"] in ip_list:
      suspicious_ip.append({"ip": dic["ip"], "attack": "Xss"})
      ip_list.append(dic["ip"])
      cluster_by_date(dic, time_list)
  for dic in bot_list:
      #print dic
      suspicious_ip.append({"ip": dic["ip"], "attack": "Abnormal user-agent"})
      ip_list.append(dic["ip"])
      cluster_by_date(dic, time_list)

  for ip in scanning_list:
    suspicious_ip.append({"ip":ip, "attack": "Scanning"})
  for log in scanning_logs:
    dic = parse_line(log)
    cluster_by_date(dic, time_list)

  for ip in malicious_redirect_ip:
    suspicious_ip.append({"ip":ip, "attack": "Malicious redirect"})
  for log in malicious_redirect:
    dic = parse_line(log)
    cluster_by_date(dic, time_list)

  suspicious_ip = remove_duplicate(suspicious_ip)

  attack_per_day = []
  for date in time_list: # date is key of time_list(dic)
    tmp = {}
    tmp["date"] = date
    tmp["num"] = time_list[date]
    attack_per_day.append(tmp)
  
  #suspicious_ip = suspicious_ip + scanning_list

  all_suspicious_logs = sql_list + xss_list + bot_list + scanning_logs + malicious_redirect

  connection = pymongo.MongoClient("mongodb://localhost")
  db = connection.test
  people = db.people

  suspicious_string = json.dumps(all_suspicious_logs)
  compressed_str = zlib.compress(suspicious_string)

  object_id = str(people.insert( {"filename": filename, "list": bson.Binary(compressed_str)} ))
  
  return [attack_and_number, suspicious_ip, attack_per_day, object_id]
  
  
def find_ip(uri, lines):
  for line in lines:
    if uri in line:
      result = parse_line(line)
      return result["ip"]

def gather_all_suspicious(filename):
  result = process(filename)  
  not_found_list = result[0]
  sql_list = result[1]
  scanning_list = []

  for dic in sql_list:
    if dic["num"] > 100:
      scanning_list.append(dic["ip"])

def count_each_hour(date, filename, search_id="default"):
  counting_list = []
  for i in xrange(24):
    counting_list.append({})
  

  lines = search_keyword(keyword=date, filename=filename, search_id=search_id) 
  current_hour = "00"
  for line in lines:
    is_string = str(line) == line

    if is_string:
      result = parse_line(line)
    else:
      result = line
    tmp = result["time"].split(":")

    #date = tmp[0][1:]
    hour = int(tmp[1])

    counting_list[hour]["num"] = counting_list[hour].get("num", 0) + 1


  hour_request_list = [] # list of dictionary. ex [ {"hour": 00, "num": 432}, .....]
  for i in xrange(len(counting_list)):
    tmp = {}
    tmp["hour"] = "%02d" % i
    tmp["num"] = counting_list[i].get("num", 0)
    hour_request_list.append(tmp)

  return hour_request_list


def count_uri(filename):
  f = open("/home/kec/uploads/"+filename)
  lines = f.readlines()
  f.close()

  uri_list = collections.OrderedDict()
  
  for i in xrange(4, len(lines)):
    line = lines[i]
    result = parse_line(line)
    uri = result["uri"]
    uri_list[uri] = uri_list.get(uri, 0) + 1
    
#  sorted_uri = sorted(uri_list.items(), key=operator.itemgetter(1))
  
  ip_list = collections.OrderedDict()
  occur_once = []
  for key in uri_list:
    if uri_list[key] == 1:
      occur_once.append(key)
      #print key
      
      ip = find_ip(key, lines)
      ip_list[ip] = ip_list.get(ip, 0) + 1
  
  sorted_ip = sorted(ip_list.items(), key=operator.itemgetter(1), reverse=True)
  
  ret_2 = []
  for ip in sorted_ip: # ip is key of not_found_list(dic)
    tmp = {}
    tmp["ip"] = ip[0]
    tmp["num"] = ip[1]
    ret_2.append(tmp)
  return (occur_once, ret_2)


def get_key(dic):
  return dic["num"]

def pick_top10(l): # l is a list of dictionarys
  sorted_list = sorted(l, key=get_key, reverse=True)
  return sorted_list[0:10]

def top10_404_request(filename, search_id="default"):
  l = process(filename=filename, search_id=search_id)[0]
  return pick_top10( l )

def is_time_early(time_a, time_b): #return True if time_a is earlier than time_b   or   time_a is same to time_b
  month_table = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
  #ex = "18/Jan/2014:17:44:08 +0900"
  #ex = "18/Jan/2014"

  if time_a == time_b:
    return True
  a_tmp = time_a.split("/")
  a_year = a_tmp[2].split(":")[0]
  a_month = month_table[a_tmp[1]]
  a_day = a_tmp[0]
  """
  print a_year
  print a_month
  print a_day
  """
  b_tmp = time_b.split("/")
  b_year = b_tmp[2].split(":")[0]
  b_month = month_table[b_tmp[1]]
  b_day = b_tmp[0]
  """
  print b_year
  print b_month
  print b_day
  """
  

  if a_year < b_year:
    return True
  elif a_year > b_year:
    return False
  elif a_year == b_year:
    if a_month < b_month:
      return True
    elif a_month > b_month:
      return False
    elif a_month == b_month:
      if a_day < b_day:
        return True
      elif a_day > b_day:
        return False
      elif a_day == b_day:
        return False



def search_keyword(keyword, filename, search_id, ip=None, date_from="default", date_to="default", method=None, URI=None, result=None, byte_length=None, user_agent=None, not_include=None):
  if keyword==None and ip==None and date_from=="default" and date_to=="default" and method==None and URI==None and result==None and byte_length==None and user_agent==None:
    return []
  
  if search_id == "default":
    f = open("/home/kec/uploads/"+filename)
  elif "suspicious_log_id" in search_id:
    obj_id = search_id.split("suspicious")[0]
    connection = pymongo.MongoClient("mongodb://localhost")
    db = connection.test
    people = db.people
    cursor = people.find({"_id":ObjectId(obj_id)})    
    binary_string = cursor[0]["list"]
    f = json.loads(zlib.decompress(str(binary_string)))

  else:
    connection = pymongo.MongoClient("mongodb://localhost")
    db = connection.test
    people = db.people
    cursor = people.find({"_id":ObjectId(search_id)})
    f = cursor[0]["list"]

  
  found_log = [] # list of strings that contains keyword
  for line in f:
    found = True
    
    is_string = str(line) == line

    if is_string:  # case of raw log. type of line is string
      if line[0] == ":":
        found = False
        parsed = {"ip":"::1", "time":"", "uri":"", "status":"", "response_length":"","user_agent":""}
      else:
        parsed = parse_line(line)
    else:                  # case for parsed log. (already parsed before.) type of line is dic
      parsed = line

    if is_string and keyword != None and not keyword in line: # if we don't check whether line is string or dic, dic always fails at not keyword in line
      #found_log.append(line)
      found = False
    if not is_string and keyword != None and not keyword in dic_to_string(line):
      found = False

    if is_string and not_include != None and not_include in line:
      found = False
    if not is_string and not_include != None and not_include in dic_to_string(line):
      found = False    

   # parsed = parse_line(line)
    
    if ip != None and found and not ip in parsed["ip"]:
      #found_log.append(line)
      found = False

    """
    some part for checking date and time
    """
    time = parsed["time"].split(":")[0][1:]
    if date_from != "default" and date_to != "default" and found and (not (is_time_early(date_from, time) and is_time_early(time, date_to))):
      #found_log.append(line)
      found = False
    
    if method != None and found and not method in parsed["uri"]:   # method is included in parsed["uri"] ex) "GET /asdfa.php"
      #found_log.append(line)
      found = False
    
    if URI != None and found and not URI in parsed["uri"]:
      #found_log.append(line)
      found = False

    if result != None and found and not result in parsed["status"]:
      #found_log.append(line)
      found = False

    if byte_length != None and found and not byte_length in parsed["response_length"]:
      #found_log.append(line)
      found = False

    if user_agent != None and found and not user_agent in parsed["user_agent"]:
      #found_log.append(line)
      found = False

    if found:
      if is_string:
        found_log.append(line)
      else:
        #print dic_to_string(line)
        #print line["user_agent"]
        found_log.append(dic_to_string(line))

  if search_id == "default":
    f.close()

  return found_log

def count_ip_uri_useragent(search_id):
  connection = pymongo.MongoClient("mongodb://localhost")
  db = connection.test
  people = db.people
  cursor = people.find({"_id":ObjectId(search_id)})
  lines = cursor[0]["list"]
  
  ip_dict_list = {}
  uri_dict_list = {}
  user_agent_dic_list = {}
  for line in lines:
    result = parse_line(line)
    ip = result["ip"]
    uri = result["uri"]
    user_agent = result["user_agent"]
    ip_dict_list[ip] = ip_dict_list.get(ip, 0) + 1
    uri_dict_list[uri] = uri_dict_list.get(uri, 0) + 1
    user_agent_dic_list[user_agent] = user_agent_dic_list.get(user_agent, 0) + 1

  ip_list = []
  uri_list = []
  user_agent_list = []
  for ip in ip_dict_list: # ip is key of not_found_list(dic)
    tmp = {}
    tmp["ip"] = ip
    tmp["num"] = ip_dict_list[ip]
    ip_list.append(tmp)

  for uri in uri_dict_list:
    tmp = {}
    tmp["uri"] = uri
    tmp["num"] = uri_dict_list[uri]
    uri_list.append(tmp)

  for user_agent in user_agent_dic_list:
    tmp = {}
    tmp["user_agent"] = user_agent
    tmp["num"] = user_agent_dic_list[user_agent]
    user_agent_list.append(tmp)

  return [ip_list, uri_list, user_agent_list]



  




