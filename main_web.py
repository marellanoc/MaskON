# web server and socket
from flask import Flask, render_template, request, jsonify, redirect, Response
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import json, os

#  variables y settings

data = dict()
with open('config.json') as json_file:
    data = json.load(json_file)

ALLOWED_EXTENSIONS = ['mp3']
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.getcwd()), 'static')
UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'alarms')

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app, debug=True, async_mode="eventlet")


@app.route('/')
def index():
    resp = render_template("index.html")
    return resp

@app.route('/settings')
def settings():
    resp = render_template("settings.html")
    return resp

@app.route('/get_config')
def get_settings():
    return jsonify(data)


@app.route('/post_config', methods=['POST'])
def post_settings():
    global data
    if request.method == 'POST':
        data = request.get_json()
        with open('config.json', 'w') as fp:
            json.dump(data, fp)
    return '200'

@app.route('/post_file', methods=['POST'])
def post_file():
    f = request.files['file']
    print(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
    return '200'

@app.route('/test<n>')
def test(n):
    socketio.emit('alarm', {'alarm': n}, namespace='/', broadcast=True)
    return "hola"

@socketio.on('alarm_change', namespace='/')
def alarm_event(json):
    print(json)
    socketio.emit('my response', json, namespace='/', broadcast=True)


if __name__ == '__main__':
    PATH_TO_LABELMAP = r"C:\Users\matia\Documents\Scripts\PDI\training_resources\training\001\label_map.pbtxt"
    PATH_TO_CONFIG = r"C:\Users\matia\Documents\Scripts\PDI\training_resources\training\pipeline.config"
    PATH_TO_CHECKPOINT = r"C:\Users\matia\Documents\Scripts\PDI\training_resources\training\001\ckpt-16"

    #app.run(host='127.0.0.1',port='5000', debug=True)
    socketio.run(app)
