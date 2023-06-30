import cv2 as cv
import numpy as np
from ultralytics import YOLO
from django.core.cache import cache
import os

from django.conf import settings

# Distance constants
PERSON_WIDTH = 16  # INCHES
TO_CM = 0.119235

# Object detector constant
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.3

# Calculated focal
FOCAL_PERSON = 2652.75


def load_model():
    # Check if the model is already cached
    model = cache.get('model')
    if model is None:
        print("hehre")
        # model_path = os.path.join(settings.BASE_DIR,'recommend','utils', 'assets', 'yolov8n.pt')
        # print(model_path)
        model = YOLO('../assets/yolov8n.pt', task='detect')

        # Cache the model
        cache.set('model', model)

    return model


# Loading the pre-trianed YOLOv8 model
# object detector funciton/method
def object_detector(image):
    model = load_model()
    results = model.predict(source=image, conf=CONFIDENCE_THRESHOLD, imgsz=(640, 640),
                            iou=NMS_THRESHOLD, max_det=1, classes=0, save=False)[0]

    classes = results.boxes.cls.numpy().astype(dtype=np.int32)
    extras = results.boxes.xywh.numpy().astype(dtype=np.int32)

    for (classid,  extra) in zip(classes, extras):

        if classid == 0:  # person class id
            width_in_px, height_in_px = extra[2], extra[3]

            # returning the data
            # 1: object width in pixels, 2: object width in pixels, 3: position where have to draw text(distance)
            return {
                'width': width_in_px,
                'heigth': height_in_px,
            }
        else:
            return {
                'error': 'Image is not of a person'
            }

    return {
        'error': 'Image does not contain any object'
    }


# distance finder function
def distance_finder(focal_length, real_object_width, width_in_frmae):
    distance = (real_object_width * focal_length) / width_in_frmae
    return distance


def calculate_body_type(img):
    # reading the reference image from dir
    # Shape (3, 640, 640)
    # img = cv.imread(img_path)
    img = img.resize((640, 640))

    data = object_detector(img)

    if 'error' in data.keys():
        return data

    width = data.get('width')
    height = data.get('heigth')

    distance = distance_finder(FOCAL_PERSON, PERSON_WIDTH, width)
    distance = round(distance, 2)/2

    fin_heigth = (height*TO_CM) + (distance - 50)*1.8
    fin_width = (width*TO_CM) + (distance - 50)*1.5

    # fin_weight = (fin_heigth*fin_width*(fin_width*0.15))/1000

    # bmi = fin_weight / ((fin_heigth/100) ** 2)
    body_model = ((fin_width*fin_heigth)/100)


    body_type = 0

    if body_model < 50:
        body_type = 1  # very underweight
    elif body_model >= 50 and body_model < 100:
        body_type = 2  # underweight
    elif body_model >= 150 and body_model < 200:
        body_type = 3  # normal
    elif body_model >= 250 and body_model < 300:
        body_type = 4  # overweight
    elif body_model >= 300 and body_model < 400:
        body_type = 5  # obeseity (very overweight)

    return body_type, body_model
