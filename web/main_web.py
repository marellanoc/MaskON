# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

import json, os


settings = 'settings'

data = dict()
alarm_actual_state = False
ALLOWED_EXTENSIONS = ['mp3']
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.getcwd()), 'static')
UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'alarms')


with open('config.json') as json_file:
    data = json.load(json_file)


app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def old_index():
    return redirect("home", code=303)


@app.route('/home')
def index():
    resp = render_template("template.html")
    return resp


@app.route('/settings')
def settings():
    resp = render_template("settings.html")
    return resp


@app.route('/test<n>')
def test(n):
    emit('alarm', {'alarm': n}, namespace='/', broadcast=True)
    return "hola"


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


@socketio.on('alarm_change')
def alarm_event(json):
    print(json)
    emit('my response', json, broadcast=True)


if __name__ == '__main__':
    # app.run(host='192.168.0.13',port='5000', debug=True)
    socketio.run(app)