from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/kec/uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['log', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config.from_object('config')
from app import views
