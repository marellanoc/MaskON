"""
Serialization tutorial: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/using_your_own_dataset.md
Serialization example of Pascal VOC dataset: https://github.com/tensorflow/models/blob/master/research/object_detection/dataset_tools/create_pascal_tf_record.py
"""

from object_detection.utils import dataset_util
import xml.etree.ElementTree as ET
import tensorflow as tf
from PIL import Image
from os import path
import numpy as np
import random
import glob


class Example:
    class_name_dict = {}
    class_count = 0

    def __init__(self, filename, width, height):
        self.filename = filename
        self.height = height
        self.width = width

        self.xmins = []
        self.xmaxs = []
        self.ymins = []
        self.ymaxs = []

        self.class_names = []
        self.class_ids = []

    def add_xmin(self, xmin):
        xmin_normalized = xmin / self.width
        self.xmins.append(xmin_normalized)

    def add_xmax(self, xmax):
        xmax_normalized = xmax / self.width
        self.xmaxs.append(xmax_normalized)

    def add_ymin(self, ymin):
        ymin_normalized = ymin / self.height
        self.ymins.append(ymin_normalized)

    def add_ymax(self, ymax):
        ymax_normalized = ymax / self.height
        self.ymaxs.append(ymax_normalized)

    def add_class_name(self, class_name):
        if class_name not in Example.class_name_dict:
            Example.class_count += 1
            Example.class_name_dict[class_name] = Example.class_count

        self.class_names.append(class_name.encode('utf8'))
        self.class_ids.append(Example.class_name_dict[class_name])

    @staticmethod
    def create_label_map(output_labelmap_path):
        keys = Example.class_name_dict.keys()
        label_map_string = ""
        for key in keys:
            id = Example.class_name_dict[key]
            name = key
            item_string = \
                "item { \n" \
                f"  id: {id}\n" \
                f"  name: \"{name}\"\n" \
                "}\n\n"
            label_map_string += item_string

        with open(output_labelmap_path, "w") as text_file:
            print(label_map_string, file=text_file)


def load_annotations(annotation_folder_path):
    '''
    Finds all xml files in annotation_folder_path and parse it into a Example object
    '''
    xml_file_paths = glob.glob(path.join(annotation_folder_path, '*.xml'))
    examples = []
    for xml_file_path in xml_file_paths:
        print(f'Cargando los datos de {xml_file_path}')
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        objects = root.findall('object')
        example = Example(
            filename=root.find('filename').text,
            width=int(root.find('size')[0].text),
            height=int(root.find('size')[1].text))

        for object in objects:
            boundary_box = object.find('bndbox')
            example.add_xmin(int(boundary_box.find('xmin').text))
            example.add_ymin(int(boundary_box.find('ymin').text))
            example.add_xmax(int(boundary_box.find('xmax').text))
            example.add_ymax(int(boundary_box.find('ymax').text))

            example.add_class_name(object.find('name').text)

        examples.append(example)

    return examples


def create_tf_example(example, images_folder_path, img_format):
    print(f'Creando registro TFRecord del archivo:  {example.filename}')
    height = example.height  # Image height
    width = example.width  # Image width
    filename = example.filename.encode('utf8')  # Filename of the image. Empty if image is not from file
    encoded_image_data = encode_image(full_img_path=path.join(images_folder_path, example.filename), img_format=img_format)

    image_format = str.encode(img_format)

    xmins = example.xmins  # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = example.xmaxs  # List of normalized right x coordinates in bounding box (1 per box)
    ymins = example.ymins  # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = example.ymaxs  # List of normalized bottom y coordinates in bounding box (1 per box)
    classes_text = example.class_names  # List of string class name of bounding box (1 per box)
    classes = example.class_ids  # List of integer class id of bounding box (1 per box)

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_image_data),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def encode_image(full_img_path, img_format):

    im = Image.open(full_img_path)
    rgb_im = im.convert('RGB')

    if img_format == 'png':
        return tf.io.encode_png(np.asarray(rgb_im)).numpy()

    if img_format == 'jpeg':
        return tf.io.encode_jpeg(np.asarray(rgb_im)).numpy()


def split_dataset(examples, train_ratio=0.8):
    random.shuffle(examples)
    split_index = int(len(examples) * train_ratio)

    train_examples = examples[:split_index]
    validation_examples = examples[split_index:]

    return train_examples, validation_examples


def create_tf_record_file(examples, images_folder_path, img_format, output_file_path):
    writer = tf.compat.v1.python_io.TFRecordWriter(output_file_path)
    for example in examples:
        tf_example = create_tf_example(example, images_folder_path, img_format)
        writer.write(tf_example.SerializeToString())
    writer.close()


if __name__ == '__main__':
    annotation_folder_path = path.normpath(r"C:\Users\matia\Documents\Scripts\PDI\archive\annotations")
    images_folder_path = path.normpath(r"C:\Users\matia\Documents\Scripts\PDI\archive\images")
    output_folder_path = path.normpath(r"C:\Users\matia\Documents\Scripts\PDI\training_resources\dataset")
    train_ratio = 0.6
    img_format = 'jpeg'  # png or jpeg

    examples = load_annotations(annotation_folder_path)
    (train_examples, validation_examples) = split_dataset(examples=examples, train_ratio=train_ratio)

    create_tf_record_file(train_examples, images_folder_path, img_format, path.join(output_folder_path, "train.record"))
    create_tf_record_file(validation_examples, images_folder_path, img_format, path.join(output_folder_path, "eval.record"))
    Example.create_label_map(output_labelmap_path=path.join(output_folder_path, "label_map.pbtxt"))
