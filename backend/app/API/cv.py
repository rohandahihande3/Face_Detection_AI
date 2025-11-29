import os
from flask import Flask, request, send_file,Blueprint
from flask_cors import CORS
import cv2 as cv
import numpy as np
from io import BytesIO
from kafka import KafkaProducer
import json

# producer = KafkaProducer(
#     bootstrap_servers="localhost:9092",
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )

open_cv_api = Blueprint('open_cv_api', __name__)
CORS(open_cv_api)

BASE = os.path.dirname(__file__)  # /backend/app/API
XML_PATH = os.path.abspath(os.path.join(BASE, "..", "xml_files"))


@open_cv_api.route('/detect', methods=['POST'])
def detect():
    file = request.files['image']
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    
    # Load cascade XML files correctly
    face_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_facelt.xml"))
    if face_cascade.empty():
        return {"error": "Failed to load cascade from: " + XML_PATH}, 500
    eye_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
    nose_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
    mouth_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))
    
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    # Detect and draw face rectangle
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Optional: further detect inside face region
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        # Eyes
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
        for (ex, ey, ew, eh) in eyes:
            cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        # Nose
        nose = nose_cascade.detectMultiScale(roi_gray, 1.1, 3)
        for (nx, ny, nw, nh) in nose:
            cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

        # Mouth
        mouth = mouth_cascade.detectMultiScale(roi_gray, 1.1, 3)
        for (mx, my, mw, mh) in mouth:
            cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

    # Return modified image
    _, buffer = cv.imencode('.jpg', img)
    return send_file(BytesIO(buffer), mimetype='image/jpeg')

@open_cv_api.route('/detect-live', methods=['POST'])
def detect_live():
    if 'image' not in request.files:
        return {"error": "No image received"}, 400

    file = request.files['image']
    print(f"==>> file: {file}")
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)

    # Load cascades
    face_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_facelt.xml"))
    eye_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
    nose_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
    mouth_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
        for (ex, ey, ew, eh) in eyes:
            cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        nose = nose_cascade.detectMultiScale(roi_gray, 1.1, 3)
        for (nx, ny, nw, nh) in nose:
            cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

        mouth = mouth_cascade.detectMultiScale(roi_gray, 1.1, 3)
        for (mx, my, mw, mh) in mouth:
            cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

    # Return image
    _, buffer = cv.imencode('.jpg', img)
    return send_file(BytesIO(buffer), mimetype='image/jpeg')





# import cv2 as cv 

# def draw_boundary(img,classfier,scaleFactor,minNeighbour,color,text):
#     gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
#     featuers = classfier.detectMultiScale(gray_img,scaleFactor,minNeighbour)
#     coords = []
#     for (x,y,w,h) in featuers:
#         cv.rectangle(img,(x,y),(x+w,y+h),color,2)
#         cv.putText(img,text,(x,y-4),cv.FONT_HERSHEY_SIMPLEX,0.8,color,1,cv.LINE_AA)
#         coords = [x,y,w,h]
#     return coords

# def detect (img,facecascade,eyecascade,nosecascade,mouthcascade):
#     color = {"blue":(255,0,0),"red":(0,0,255),"green":(0,255,0)}
#     coords = draw_boundary(img,facecascade,1.1,10,color["blue"],"Face")
    
#     if len(coords)==4:
#        roi_img = img [coords[2]:coords[1]+coords[3],coords[0]:coords[0]+coords[1]]
#        coords = draw_boundary(roi_img,eyecascade,1.1,14,color["green"],"Eyes")
#        coords = draw_boundary(roi_img,nosecascade,1.1,5,color["red"],"Nose")
#        coords = draw_boundary(roi_img,mouthcascade,1.1,20,(255,255,255),"Mouth")

#     return img



# face = cv.CascadeClassifier("frontal_facelt.xml")
# nose = cv.CascadeClassifier("nose.xml")
# eye = cv.CascadeClassifier("eye.xml")
# mouth = cv .CascadeClassifier("mouth.xml")

# capture = cv.VideoCapture(0)
# # v = cv.imread("/home/rohan/Rohan_WorksSpace/OPENCV/opencv_git/IMG20221116125229.jpg")
# # img = detect(v,face,nose,mouth,eye)
# # cv.imshow("vins",v)
# # cv.waitKey(0)



# while True:
#     isTrue, img = capture.read()

#     img = detect(img,face,eye,nose,mouth)
  
#     if not isTrue:
#         break
    
#     cv.imshow('Video', img)
    
#     if cv.waitKey(20) & 0xFF == ord("d"):
#         break


# capture.release()

# cv.destroyAllWindows()
