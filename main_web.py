# imports de Flask
from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# imports para manejo de json y rutas dentro del disco
import json, os

# carpeta donde se suben las alarmas
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.getcwd()), 'static')
UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'alarms')

# diccionario que guarda las configuraciones
data = dict()
# se cargan las configuraciones desde el json de configuraciones
with open('config.json') as json_file:
    data = json.load(json_file)

#creacion del server y configuracion de la carpeta de subida
app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app) # socket que enviará mensajes al front


# Rutas

#ruta que redirecciona de root hacia home
@app.route('/')
def old_index():
    return redirect("home", code=303)

#ruta principal, aqui se encuentra el stream de video
@app.route('/home')
def index():
    resp = render_template("template.html")
    return resp

# ruta que muestra la pagina de configuracion
@app.route('/settings')
def settings():
    resp = render_template("settings.html")
    return resp

# ruta utilizada para encender y apagar la alarma en la pagina web
@app.route('/test<n>')
def test(n):
    emit('alarm', {'alarm': n}, namespace='/', broadcast=True) # se avisa a la pagina por medio del socket
    return "200"

# ruta para enviar la configuracion a la figuracion
@app.route('/get_config')
def get_settings():
    return jsonify(data)

# ruta utilizada para guardar las configuraciones realizadas en la pagina web
@app.route('/post_config', methods=['POST'])
def post_settings():
    global data

    if request.method == 'POST':
        data = request.get_json() # se sobreescribe la variable que guara la configuracion

        # se sobreescribe el archivo de configuraciones
        with open('config.json', 'w') as fp:
            json.dump(data, fp)

    return '200'

# ruta para guardar los tonos de alarma
@app.route('/post_file', methods=['POST'])
def post_file():

    f = request.files['file']
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))) # se utiliza secure_filename para eliminar caracteres no permitidos
    
    return '200'

#listener utilizado para testear conexion con el front
@socketio.on('alarm_change')
def alarm_event(json):
    print(json)



if __name__ == '__main__':
    # app.run(host='192.168.0.13',port='5000', debug=True)
    #se envuelve el server en el socket y se ejecuta
    socketio.run(app)