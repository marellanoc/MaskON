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

``` git clone https://github.com/tensorflow/models.git ```

Dentro de este repositorio hay una carpeta llamada research con todos los modelos, entre los cuales está object_detection, el que se ocupará para crear la imagen de docker utilizando el siguiente comando:

``` docker build -f research/object_detection/dockerfiles/tf2/Dockerfile -t od . ``` 

esta contendrá los archivos necesarios para realizar directamente el entrenamiento para detección de objetos, lo que se realizará más adelante.

## Procesamiento de las imágenes del Dataset.*

Este repositorio contiene una carpeta llamada "archive", en su interior, la carpeta images tiene las imágenes a procesar del dataset, y "annotations" contiene los archivos xml para cada imagen del dataset, con la descripción de región de interés de cada una y la etiqueta correspondiente a una de las tres categorías planteadas.