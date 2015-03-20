"""
Eunchan Kim
"""
from flask import make_response, jsonify, render_template, flash, redirect, request, send_from_directory, url_for
from app import app
from .forms import LoginForm
from werkzeug import secure_filename
from bson.objectid import ObjectId
import parse
import os
import pymongo
import base64
import pygeoip
import zipfile
from Data import log2oData
from Analysis import featureVector
from Analysis import analysis
import zlib
import json
import bson

connection = pymongo.MongoClient("mongodb://localhost")
db = connection.test
people = db.people
upload_path = "/home/kec/uploads/"
tab_path = "/home/kec/uploads/tab/"
error_path = "/home/kec/uploads/error"
feature_path = "/home/kec/uploads/feature"

def allowed_file(filename):
  return True
#  return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
@app.route('/index')
def index():
  user = {"nickname": "pavian"}
  posts = []
  return render_template("index.html", title='HOME', user=user, posts = posts)
#  form = LoginForm()
#  return render_template('login.html', title='Sign In', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
    flash('Login requested for OpenID="%s", remember_me=%s ' % (form.openid.data, str(form.remember_me.data)))
    return redirect('/index')
  response = make_response( render_template('home.html', title='Sign In', form=form, providers=app.config['OPENID_PROVIDERS']) )
  response.set_cookie('search_id', "default")
  response.set_cookie('analysis_id', "default")
  response.set_cookie('suspicious_log_id', "default")
  response.set_cookie('file_id', "default")
  response.set_cookie('log_size', "0")
  response.set_cookie('anomal_id', "default")
  return response

@app.route('/chart', methods=['GET', 'POST'])
def chart():
  return render_template('chart.html')

@app.route('/dashboard22', methods=['GET', 'POST'])
def dashboard22():
  file_id = base64.b64decode(request.cookies.get("file_id"))
  real_data = parse.top10_404_request(file_id.encode('ascii', 'ignore'))
  response = make_response(render_template('dashboard.html', filename=file_id[:-len(request.remote_addr)], data=real_data))
  response.set_cookie('test_id', "hellohellohello hahaha")
  response.set_cookie('search_id', "default")
  return response

@app.route('/404_requests/<filename>')
def not_found_request(filename):
  real_data = parse.process(filename.encode('ascii', 'ignore'))[0]
  return render_template('404_request.html', filename=filename, data=real_data)

@app.route('/anomal')
def anomal():
  filename = base64.b64decode(request.cookies.get('file_id'))
  anomal_id = request.cookies.get('anomal_id')

  suspicious_log_id = request.cookies.get('suspicious_log_id')
  cursor = people.find({"_id":ObjectId(suspicious_log_id)})    
  binary_string = cursor[0]["list"]
  misuse_logs = json.loads(zlib.decompress(str(binary_string)))
  misuse_ip = parse.get_ip_list(misuse_logs)


  if anomal_id == "default":
    log2oData.MyownOrange(upload_path+filename, tab_path+filename+".tab", error_path+filename+".tab")
    featureVector.extract_feature(tab_path+filename+".tab", feature_path+filename+".tab")
    anomaly = analysis.getAnalysis(feature_path+filename+".tab", 4.0, upload_path + "result/"+filename+".tab")

    anomal_ip = []
    for elem in anomaly:
      for ip in elem[1]:
        if ip not in misuse_ip:
          tmp = {"reason":elem[0], "ip":ip}
          anomal_ip.append(tmp)
    anomal_id = people.insert({"anomal_ip":anomal_ip})
  else:
    cursor = people.find({"_id":ObjectId(anomal_id)})
    anomal_ip = cursor[0]["anomal_ip"]

  response = make_response(render_template("anomal.html", anomal_ip=anomal_ip))
  response.set_cookie('anomal_id', str(anomal_id))
  return response


@app.route('/dashboard')
def dashboard():
  filename = base64.b64decode(request.cookies.get('file_id'))
  search_id = request.cookies.get('search_id')
  analysis_id = request.cookies.get('analysis_id')

  

  if search_id == "default" and analysis_id != "default":
    print "analysis_cache found"
    cursor = people.find({"_id":ObjectId(analysis_id)})
    statistics = cursor[0]["statistics"]
    real_data = cursor[0]["real_data"]
    ip_info = cursor[0]["ip_info"]
    response = make_response(render_template('canvas.html', filename=filename, traffic=real_data, data2=statistics[0], ip_list=statistics[1], ip_info=ip_info, attack_traffic=statistics[2]))
    return response

  elif search_id == "default":
    process_result = parse.process(filename)
  else:
    process_result = parse.process(filename, search_id=search_id)

  statistics = parse.make_statistics(process_result[1], process_result[4], process_result[5], process_result[3], filename, search_id, process_result[7], process_result[8])

  log_number = process_result[6]
  real_data = process_result[2] # traffic data
  ip_list = statistics[1]
  
  gi = pygeoip.GeoIP('/home/kec/dev/app/static/GeoLiteCity.dat') # should be absolute path because currrent running path could be different.
  
  ip_info = []
  for ip in ip_list:
    tmp = {}
    #print ip["ip"]
    location = gi.record_by_addr(ip["ip"])
    if location["city"] == None:
      tmp = {"country": location['country_name'], "city": "not found", "ip": ip["ip"], "attack" : ip["attack"]}
    else:
      tmp = {"country": location['country_name'], "city": location['city'], "ip": ip["ip"], "attack" : ip["attack"]}

    ip_info.append(tmp)

  if search_id == "default" and analysis_id == "default": # we need to store the arguments
    analysis_id = people.insert( {"statistics":statistics, "real_data": real_data, "ip_info": ip_info} )


  response = make_response(render_template('canvas.html', filename=filename, traffic=real_data, data2=statistics[0], ip_list=statistics[1], ip_info=ip_info, attack_traffic=statistics[2]))
  response.set_cookie('suspicious_log_id', statistics[3])
  response.set_cookie('analysis_id', str(analysis_id))
  response.set_cookie('log_size', str(log_number))
#  print "end"
  return response

@app.route('/ip_activity/<ip_addr>', methods=['GET', 'POST'])
def ip_activity(ip_addr):
  if request.method == "GET":
    suspicious_log_id = request.cookies.get('suspicious_log_id')
    logs = parse.search_keyword(keyword=None, filename="not used", search_id=suspicious_log_id+"suspicious_log_id", ip=ip_addr)
    object_id = people.insert( {"ip": ip_addr, "list": logs} )
    
    process_result = parse.process(filename="not used", search_id=str(object_id))
    traffic_data = process_result[2]

    cursor = people.find({"_id":ObjectId(request.cookies.get('analysis_id'))})

    ip_attack_list = cursor[0]["ip_info"]

    target = {}
    for dic in ip_attack_list:
      if dic["ip"] == ip_addr:
        target = dic
        break

    response = make_response(render_template('user.html', ip_attack=[target], traffic=traffic_data))
    response.set_cookie('corresponding_id', str(object_id))
    return response
  else: # in case of "POST" method
    cursor = people.find({"_id": ObjectId(request.cookies.get('corresponding_id'))})
    attack_logs = cursor[0]["list"]

    return jsonify({'logs' : ("\n").join(attack_logs)})



@app.route('/upload', methods=['POST'])
def upload():
  file = request.files['hellofile']
  allowed_file(file.filename)
  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename+request.remote_addr))
    if ".log" in filename and not ".zip" in filename:
      response = redirect(url_for('dashboard'))
      file_id = base64.b64encode(filename+request.remote_addr)
      response.set_cookie('file_id', file_id)
      return response
    elif ".zip" in filename:
      f = open("/home/kec/uploads/"+filename+request.remote_addr)
      z = zipfile.ZipFile(f)

      for name in z.namelist():
        outpath = "/home/kec/uploads"
       
        if not "._" in name:

          z.extract(name, outpath)
          filename = name
          break
        else:
          print "whywhy"
        

      f.close()
      os.chdir("/home/kec/uploads")

      os.rename(filename, filename+request.remote_addr)
      response = redirect(url_for('dashboard'))
      file_id = base64.b64encode(filename+request.remote_addr)
      response.set_cookie('file_id', file_id)
      return response
    return redirect(url_for('uploaded_file', filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/unique_request/<filename>')
def unique_request(filename):
  real_data = parse.count_uri(filename.encode('ascii', 'ignore'))[1]
  return render_template('unique_request.html', data=real_data)

@app.route('/search')
def search():
  search_id = request.cookies.get("search_id")
  response = make_response(render_template('search.html'))
  response.set_cookie('search_id', "default")
  return response

@app.route('/give_ip_log', methods=['POST'])
def give_ip_log():
  filename = base64.b64decode(request.cookies.get('file_id'))
  ip_addr = request.form['ip_addr']
  #print ip_addr
  logs = parse.search_keyword(keyword=None, filename=filename, search_id="default", ip=ip_addr)
  #print logs
  return jsonify({'logs':("").join(logs)})

@app.route('/give_graph_data', methods=['POST'])
def give_graph_data():
  filename = base64.b64decode(request.cookies.get('file_id'))
  search_id = request.cookies.get('search_id')
  suspicious_log_id = request.cookies.get('suspicious_log_id')
  selected_value = request.form['value']
  labels = []
  numbers = []

  if selected_value == "404 Requests":

    graph_data = parse.top10_404_request(filename=filename, search_id=search_id)

    for dic in graph_data:
      labels.append(dic['ip'])
      numbers.append(dic['num'])
    return jsonify({'graph_data' : [labels, numbers], 'attack_graph_data':[[],[]], 'type':'404'})

  else:
    attack_labels = []
    attack_numbers = []

    graph_data = parse.count_each_hour(filename=filename, date=selected_value, search_id=search_id)
    attack_data = parse.count_each_hour(filename=filename, date=selected_value, search_id=suspicious_log_id+"suspicious_log_id")

    for dic in graph_data:
      labels.append(dic['hour'])
      numbers.append(dic['num'])

    for dic in attack_data:
      attack_labels.append(dic['hour']) # actually we don't need this because it's always ["00", "01", "02" ....]
      attack_numbers.append(dic['num'])


  return jsonify({'graph_data' : [labels, numbers], 'attack_graph_data' : [attack_labels, attack_numbers], 'type': 'day traffic'})


@app.route('/parse_data', methods=['POST', 'GET'])
def parse_data():
  if request.method == "POST":
    #seems like encoding unicode to ascii not needed.

    keyword = request.form['text'].encode('ascii', 'ignore')
    if keyword == "":
      keyword = None
    filename = base64.b64decode(request.cookies.get('file_id'))
    
    ip = request.form['ip']
    if ip == "":
      ip = None
    
    date_from = request.form['date_from']
    if date_from == "":
      date_from = "default"

    date_to = request.form['date_to']
    if date_to == "":
      date_to = "default"

    method = request.form['method']
    if method == "":
      method = None

    uri = request.form['uri']
    if uri == "":
      uri = None

    result = request.form['result']
    if result == "":
      result = None

    byte_length = request.form['byte_length']
    if byte_length == "":
      byte_length = None
    
    user_agent = request.form['user_agent']
    if user_agent == "":
      user_agent = None
    

    search_id = request.cookies.get("search_id")
    log_number = request.cookies.get("log_size")
    ret_list = parse.search_keyword(keyword=keyword, search_id=search_id, filename=filename, ip=ip, date_from=date_from, date_to=date_to, method=method, URI=uri, result=result, byte_length=byte_length, user_agent=user_agent)


    if ret_list != []:
      ret_string = ("").join(ret_list)
      object_id = people.insert( {"filename": filename, "keyword":keyword, "list": ret_list} )
      statistics = parse.count_ip_uri_useragent(str(object_id))
    
      return jsonify({
        'search_id':str(object_id),
	'text': ret_string,
  'ip_count' : len(statistics[0]),
  'uri_count' : len(statistics[1]),
  'useragent_count' : len(statistics[2]),
  'result_count': len(ret_list),
  'log_number' : log_number
	})
    else:
      print "empty result"
      return jsonify({
        'search_id': "default",
        'text': "No result",
        'result_count': 0,
        'ip_count':0,
        'uri_count':0,
        'useragent_count':0,
        'log_number':log_number
        })


