######## BIBLIOTECAS ########

#Bibliotecas para el reconocimiento de mascarillas
import numpy as np
from cv2 import cv2
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder

# Bibliotecas para el servidor web que publica el streaming de la cámara
from flask import Flask, render_template, request, jsonify, redirect, Response
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

import json, os
import requests

# Servidor flask para levantar el streaming
app = Flask(__name__, template_folder='templates')

URL = "http://localhost:5000/test" # Endpoint para activar y desactivar la alarma

######## FUNCIONES ########

#Esta función se encarga de realizar la detección de mascarillas sobre un frame de video.
def detect(image, detection_model):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)

    return detections, prediction_dict, tf.reshape(shapes, [-1])

# Esta función ejecuta el sistema completo de reconocimiento de mascarilla
def run(label_map_path, config_file_path, checkpoint_path, cam_ip):
    global app

    # Activa el uso de GPU para el procesamiento si es que está disponible
    gpus = tf.config.experimental.list_physical_devices('GPU')

    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

    # Obtención de los datos de configuración
    configs = config_util.get_configs_from_pipeline_file(config_file_path)
    model_config = configs['model']
    detection_model = model_builder.build(model_config=model_config, is_training=False)

    # Recupera el checkpoint entregado desde la red neuronal.
    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    ckpt.restore(checkpoint_path).expect_partial()

    category_index = label_map_util.create_category_index_from_labelmap(label_map_path, use_display_name=True)

    # Solicitud de conexión a la Cámara IP sobre esta IP
    # Obtención del streming de video desde una Cámara IP y capturado por OpenCV.
    videoStreamAddress = cam_ip
    cap = cv2.VideoCapture(videoStreamAddress)
    
    # Este ciclo infinito realiza la detección de mascarillas sobre cada frame recibido.
    while True:
        border_color = 'green'
        _, image_np = cap.read()

        # Procesamiento del frame con la función detect pasandole por parámetro el modelo de la CNN.
        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections, _, _ = detect(input_tensor, detection_model)

        detection_boxes = detections['detection_boxes'][0].numpy()
        detection_classes = detections['detection_classes'][0].numpy()
        detection_scores = detections['detection_scores'][0].numpy()

        indexes = np.array(tf.image.non_max_suppression(
            detection_boxes,
            detection_scores,
            max_output_size=100,
            iou_threshold=0.5,
            score_threshold=0.3))

        detection_boxes = detection_boxes[indexes]
        detection_classes = detection_classes[indexes]
        detection_scores = detection_scores[indexes]

        label_id_offset = 1
        image_np_with_detections = image_np.copy()

        # Interpretación del resultado de la detección con bonding boxes sobre los rostros detectados
        if indexes.shape != 0:
            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detection_boxes,
                (detection_classes + label_id_offset).astype(int),
                detection_scores,
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=10,
                min_score_thresh=.30,
                agnostic_mode=False,
                semaphore_mode=True)

            ### Integración de la detección con la intefaz web ###
            # Caso sin mascarilla o mascarilla mal puesta en al menos una detección del frame en curso 
            if any(c == 0 or c == 2 for c in detection_classes): 
                requests.get(url=URL + '1') # Se envía una señal de activación al endpoint de acción de la alarma
                border_color = 'blue' #rojo (bug de TF)
                
            # sino, todo ok, verde
            else:
                requests.get(url=URL + '0')
                border_color = 'green' #verde
            
            # Bounding box en el contorno de la imagen para facilitar la visualización de la alerta
            viz_utils.draw_bounding_box_on_image_array(
                image_np_with_detections,
                0, 0, 1, 1, 
                color = border_color,
                thickness = 20)

        # Retorno de la imagen resultante para su streaming
        frame = cv2.resize(image_np_with_detections, (800, 600))
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_encoded_jpeg = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded_jpeg + b'\r\n\r\n')

    cap.release()
    cv2.destroyAllWindows()

####### RUTA SERVIDOR WEB FLASK PARA STREAMING DE VIDEO ########

# Al recibir una solicitud GET en esta ruta del servidor, se ejecuta la función run()
@app.route('/cam')
def cam():
    return Response(
        run(
            PATH_TO_LABELMAP,
            PATH_TO_CONFIG,
            PATH_TO_CHECKPOINT,
            CAMERA_IP),
        mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    #PARÁMETROS DEL MODELO DE LA RED NEURONAL A UTILIZAR
    PATH_TO_LABELMAP = r"C:\Users\matia\Documents\Scripts\PDI\training_resources\training\001\label_map.pbtxt"
    PATH_TO_CONFIG = r"C:\Users\matia\Documents\Scripts\PDI\training_resources\training\pipeline.config"
    PATH_TO_CHECKPOINT = r"C:\Users\matia\Documents\Scripts\PDI\training_resources\training\001\ckpt-16"
    CAMERA_IP = "http://192.168.1.102:4747/video"

    # ejecución del servidor flask al ejecutar el archivo.
    app.run(port=8000, debug=True)
