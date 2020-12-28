## Tutorial de instalación
# MaskON: Detección y uso correcto de mascarilla

Proyecto desarrollado por:
* José Benavente,
* Matías Concha,
* Jorge Fernandez,
* María Rivas,
* Juan Sánchez, 

en el marco de la asignatura ELO328 Procesamiento Digital de Imágenes, Universidad Técnica Federico Santa María, 2020.

[[[ **introducir acá breve introducción del proyecto** ]]]

Este tutorial tiene como objetivo permitir instalar de forma local todos los elementos necesarios para ejecutar el código contenido en este repositorio y poder poner a prueba su funcionamiento.

## Estructura del proyecto
```
.
+-- archive
    +-- annotations -> descripción de ROI en un XML por cada imagen del dataset
    +-- dataset -> resultado del preprocesamiento del dataset
    +-- images -> imágenes a procesar del dataset
+-- cuda (ignorado en git)
+-- object_detection (ignorado)
+-- templates
    +-- alarm.mp3
    +-- index.html
+-- training_resources
    +-- checkpoint -> Directorio una red neuronal previamente entrenada para reconocer rostros.
    +-- training -> salidas con redes neuronales entrenadas para reconocimiendo de mascarillas (ignorado en git).
    +-- pipeline.config -> archivo de configuración de entrenamiento de la red neuronal.
+-- main.py -> archivo principal del proyecto
+-- tfrecord_converter.py -> script para el preprocesamiento del dataset
+-- web.py -> aplicación web para la visualización de la aplicación.
```

## Preparación del equipo con las herramientas necesarias:

### Prerrequisitos:

* Docker
* Ambiente de conda con los siguientes paquetes instalados:
    * OpenCV
    * Tensorflow2
    * Tensorboard
    * playsound
    * flask
    
    Es posible que algunas dependencias de los estos paquetes paquetes no sean provistas directamente por conda, en ese caso, instalarlas manualmente solo de ser requeridos. Algunas paquetes pueden ser:

    * scipy
    * absl-py
    * tf-models-official
    * tf-slim

    NOTA: Si se usa un ambiente de conda, instalar estos paquetes con el gestor de paquetes de conda (conda install) y no con pip ya que puede generar problemas. Solo cuando se requiera instalar un paquete que NO EXISTE en alguno de los repositorios de conda, instalarlo con pip. 

    

### Instalación:

1. API de Tensorflow para el reconocimiento de objetos.

Esta API será utilizada en dos ocasiones, acá para montar un contenedor de Docker para realizar el entrenamiento, y más adelante, para poder utilizar la red neuronal ya entrenada para el reconocimiento de mascarillas.

Para obtener el modelo de reconocimiento de objetos, se puede clonar directamente el repositorio de tensorflow en github con todos los modelos que se tienen disponibles 

` git clone https://github.com/tensorflow/models.git `

Dentro de este repositorio hay una carpeta llamada research con todos los modelos, entre los cuales está object_detection, el que se ocupará para crear la imagen de docker utilizando el siguiente comando:

` docker build -f research/object_detection/dockerfiles/tf2/Dockerfile -t od . ` 

esta contendrá los archivos necesarios para realizar directamente el entrenamiento para detección de objetos, lo que se realizará más adelante.

## Preprocesamiento de las imágenes del dataset (opcional)

Este repositorio contiene una carpeta llamada "archive", en su interior, está el dataset sin procesar, en las carpetas images y annotations, y el dataset procesado en la carpeta dataset. Solo es necesario preprocesar el dataset si se desean añadir más imágenes. Para esto se ejecuta el script

` python tfrecord_converter.py `

Este script fue obtenido directamente de la documentación de Tensorflow para el reconocimiento de objetos.

## Entrenamiento (opcional: se provee en git del último checkpoint obtenido durante el desarrollo del proyecto)

Esta etapa requiere de una buena capacidad de procesamiento o de núcleos cuda para su ejecución dado que acá se realiza la creación y entrenamiento de la red neuronal convolucional con la que se posteriormente se analizarán frames en tiempo real desde una fuente de video como una webcam o cámara IP, para el reconocimiento del uso de mascarilla en rostros de personas.

El entrenamiento de esta red neuronal usa un modelo previamente entrenado sobre el dataset COCO 2017 obenido del Zoo de modelos de Tensorflos para detección de objetos (TFOD Model Zoo). Particularmente se utiliza SSD_MobileNet_V2_FPNLite_320x320. Este repositorio contiene el checkpoint mencionado en 

`training_resources/checkpoint`

Para realizar el entrenamiento, este repositorio provee de un archivo de configuración en:

`training_resources/training/pipeline.config`

con los ajustes necesarios para realizar directamente el entrenamiento. A grandes rasgos, este archivo instruye que para entrenar esta red neuronal se requieren:

* 15000 pasos de entrenamiento
* 3 clusteres (las tres categorías de mascarillas determinadas en el preprocesamiento del dataset)
* Modo de entrenamiento: detection
* Rutas al dataset y al checkpoint del modelo previamente entrenado

Estos parámetros pueden ser modificados directamente en este archivo si se desea.

Para iniciar un entrenamiento, se debe crear una carpeta llamada 00X en `training_resources/training/`, con X el número de la iteración del entrenamiento. Si no se ha realizado uno previamente, comenzar con 0 o 1.

Luego, se debe levantar un contenedor de docker que tenga acceso al directorio `training_resources`, para esto se ejecuta el siguiente comando:

`docker run -it -v ruta_al_repositorio/MaskON/training_resources:/home/tensorflow/training_resources od`

Dado que este contenedor ya contiene todos los modelos de detección de objetos, solo basta con comenzar a entrenar la red neuronal invocando al script provisto por tensorflow para dicho efecto, entregándole como parámetros la ruta al archivo de configuración `pipeline.config` y la ruta de salida del modelo resultatne: 

`python ~/models/research/object_detection/model_main_tf2.py --pipeline_config_path ~/training_resources/training/pipeline.config --model_dir ~/training_resources/training/00X`

Luego de esperar un mínimo de 9 a 12 horas dependiendo del rendimiento del computador donde se ejecute este script (tiempos obtenidos por los integrantes del equipo) la red neuronal está lista para ser utilizada por la aplicación principal del proyecto. Esta puede ser ejecutada directamente con:

`python main.py`
o desde fuera de la carpeta del repositorio con
`python MaskON`

Esto levantará un servidor local en 

http://localhost:5000 con la aplicación final del proyecto.


## Análisis de la red neuronal

Adicionalmente, puede levantarse un servidor local con Tensorboard para observar el resultado del entrenamiento de la red neuronal y así corroborar que el resultado es el correcto, comparando las imágenes designadas para evaluación con las imágenes de entrenamiento.

Lo primero que se debe hacer, es desde el terminal con el contenedor de docker, ejecutar: 

`python ~/models/research/object_detection/model_main_tf2.py --pipeline_config_path ~/training_resources/training/pipeline.config --model_dir ~/training_resources/training/00X 
--checkpoint_dir ~/training_resources/training/00X`

(esto se puede realizar durante el entrenamiento. Para acceder a un nuevo terminal hacia el contenedor de docker ejecutar: 

`docker exec -it nombre_del_contenedor bash` 

y ejecutar el comando anterior)

Finalmente, invocar una instancia de Tensorboard (en un terminal del computador, no en docker) hacia la carpeta de salida del modelo que se está entrenando:

`tensorboard --host=127.0.0.1 --logdir=ruta_al_repositorio/training_resources/training/00X`

Para observar la instancia, se debe acceder desde un navegador a http://localhost:6006 o el puerto que tensorboard muestre por consola.