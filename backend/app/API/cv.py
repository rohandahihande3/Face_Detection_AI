# import os
# from flask import Flask, request, send_file,Blueprint,jsonify
# from flask_cors import CORS
# import cv2 as cv
# import numpy as np
# from io import BytesIO
# from kafka import KafkaProducer
# import json

# # producer = KafkaProducer(
# #     bootstrap_servers="localhost:9092",
# #     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# # )

# open_cv_api = Blueprint('open_cv_api', __name__)
# CORS(open_cv_api)

# BASE = os.path.dirname(__file__)  # /backend/app/API
# XML_PATH = os.path.abspath(os.path.join(BASE, "..", "xml_files"))

# # def load_cascade(filename_candidates):
# #     """Try multiple candidate filenames and return a loaded CascadeClassifier or None."""
# #     for fname in filename_candidates:
# #         path = os.path.join(XML_PATH, fname)
# #         if os.path.exists(path):
# #             cascade = cv.CascadeClassifier(path)
# #             if not cascade.empty():
# #                 return cascade
# #     return None

# @open_cv_api.route('/detect', methods=['POST'])
# def detect():
#     file = request.files['image']
#     img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    
#     # Load cascade XML files correctly
#     face_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_face.xml"))
#     if face_cascade.empty():
#         return {"error": "Failed to load cascade from: " + XML_PATH}, 500
#     eye_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
#     nose_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
#     mouth_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))
    
#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
#     # Detect and draw face rectangle
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#     for (x, y, w, h) in faces:
#         cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
#         # Optional: further detect inside face region
#         roi_gray = gray[y:y+h, x:x+w]
#         roi_color = img[y:y+h, x:x+w]

#         # Eyes
#         eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
#         for (ex, ey, ew, eh) in eyes:
#             cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

#         # Nose
#         nose = nose_cascade.detectMultiScale(roi_gray, 1.1, 3)
#         for (nx, ny, nw, nh) in nose:
#             cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

#         # Mouth
#         mouth = mouth_cascade.detectMultiScale(roi_gray, 1.1, 3)
#         for (mx, my, mw, mh) in mouth:
#             cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

#     # Return modified image
#     _, buffer = cv.imencode('.jpg', img)
#     return send_file(BytesIO(buffer), mimetype='image/jpeg')

# @open_cv_api.route('/detect-live', methods=['POST'])
# def detect_live():
#     try:
#         if 'image' not in request.files:
#             return jsonify({"error": "No image received"}), 400

#         file = request.files['image']
#         print(f"==>> file: {file}")
#         data = file.read()
#         if not data:
#             return jsonify({"error": "Empty file uploaded"}), 400

#         img = cv.imdecode(np.frombuffer(data, np.uint8), cv.IMREAD_COLOR)
#         if img is None:
#             return jsonify({"error": "Unable to decode image"}), 400

#         # Try to load cascades (use typical filenames; adjust to what you included)
#         face_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_face.xml"))
#         eye_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
#         nose_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
#         mouth_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))

#         if face_cascade is None:
#             return jsonify({"error": f"Face cascade not found. Looked in {XML_PATH}"}), 500

#         gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#         for (x, y, w, h) in faces:
#             cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
#             roi_gray = gray[y:y+h, x:x+w]
#             roi_color = img[y:y+h, x:x+w]

#             if eye_cascade is not None:
#                 eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
#                 for (ex, ey, ew, eh) in eyes:
#                     cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

#             if nose_cascade is not None:
#                 nose = nose_cascade.detectMultiScale(roi_gray, 1.1, 3)
#                 for (nx, ny, nw, nh) in nose:
#                     cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

#             if mouth_cascade is not None:
#                 mouth = mouth_cascade.detectMultiScale(roi_gray, 1.1, 3)
#                 for (mx, my, mw, mh) in mouth:
#                     cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

#         # Return image
#         _, buffer = cv.imencode('.jpg', img)
#         return send_file(BytesIO(buffer), mimetype='image/jpeg')

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


import os
from flask import Flask, request, send_file,Blueprint,jsonify
from ultralytics import YOLO
from flask_cors import CORS
import cv2 as cv
import numpy as np
from io import BytesIO
from kafka import KafkaProducer
import json

CPU_THREADS = min(8, os.cpu_count() or 1)

# producer = KafkaProducer(
#     bootstrap_servers="localhost:9092",
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )

open_cv_api = Blueprint('open_cv_api', __name__)
CORS(open_cv_api)

BASE = os.path.dirname(__file__)  # /backend/app/API
XML_PATH = os.path.abspath(os.path.join(BASE, "..", "xml_files"))


# model = YOLO("yolov8n-face.pt")
model = YOLO("yolov8n.pt")
model.to("cpu")   # explicit CPU

# Use available CPU cores efficiently in container/server mode.
cv.setNumThreads(CPU_THREADS)
cv.ocl.setUseOpenCL(False)
try:
    import torch

    torch.set_num_threads(CPU_THREADS)
    torch.set_num_interop_threads(1)
except Exception:
    # Keep API startup resilient even if torch settings are unavailable.
    pass

# @open_cv_api.route('/detect', methods=['POST'])
# def detect():
#     file = request.files['image']
#     img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)
    
#     # Load cascade XML files correctly
#     face_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_face.xml"))
#     if face_cascade.empty():
#         return {"error": "Failed to load cascade from: " + XML_PATH}, 500
#     eye_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
#     nose_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
#     mouth_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))
    
#     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
#     # Detect and draw face rectangle
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#     for (x, y, w, h) in faces:
#         cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
#         # Optional: further detect inside face region
#         roi_gray = gray[y:y+h, x:x+w]
#         roi_color = img[y:y+h, x:x+w]

#         # Eyes
#         eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
#         for (ex, ey, ew, eh) in eyes:
#             cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

#         # Nose
#         nose = nose_cascade.detectMultiScale(roi_gray, 1.1, 3)
#         for (nx, ny, nw, nh) in nose:
#             cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

#         # Mouth
#         mouth = mouth_cascade.detectMultiScale(roi_gray, 1.1, 3)
#         for (mx, my, mw, mh) in mouth:
#             cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

#     # Return modified image
#     _, buffer = cv.imencode('.jpg', img)
#     return send_file(BytesIO(buffer), mimetype='image/jpeg')

@open_cv_api.route('/detect', methods=['POST'])
def detect_yolo():
    file = request.files['image']
    img = cv.imdecode(np.frombuffer(file.read(), np.uint8), cv.IMREAD_COLOR)

    img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    results = model(img_rgb, imgsz=320, conf=0.4, device="cpu")

    for r in results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box[:4])
            cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    _, buffer = cv.imencode('.jpg', img)
    return send_file(BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ⚡ LIVE DETECT (same logic)
# =========================
@open_cv_api.route('/detect-live', methods=['POST'])
# def detect_live():
#     try:
#         if 'image' not in request.files:
#             return jsonify({"error": "No image received"}), 400

#         file = request.files['image']
#         print(f"==>> file: {file}")
#         data = file.read()
#         if not data:
#             return jsonify({"error": "Empty file uploaded"}), 400

#         img = cv.imdecode(np.frombuffer(data, np.uint8), cv.IMREAD_COLOR)
#         if img is None:
#             return jsonify({"error": "Unable to decode image"}), 400

#         # Try to load cascades (use typical filenames; adjust to what you included)
#         face_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_face.xml"))
#         eye_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
#         nose_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
#         mouth_cascade = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))

#         if face_cascade is None:
#             return jsonify({"error": f"Face cascade not found. Looked in {XML_PATH}"}), 500

#         gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
#         faces = face_cascade.detectMultiScale(gray, 1.3, 5)

#         for (x, y, w, h) in faces:
#             cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
#             roi_gray = gray[y:y+h, x:x+w]
#             roi_color = img[y:y+h, x:x+w]

#             if eye_cascade is not None:
#                 eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
#                 for (ex, ey, ew, eh) in eyes:
#                     cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

#             if nose_cascade is not None:
#                 nose = nose_cascade.detectMultiScale(roi_gray, 1.1, 3)
#                 for (nx, ny, nw, nh) in nose:
#                     cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

#             if mouth_cascade is not None:
#                 mouth = mouth_cascade.detectMultiScale(roi_gray, 1.1, 3)
#                 for (mx, my, mw, mh) in mouth:
#                     cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

#         # Return image
#         _, buffer = cv.imencode('.jpg', img)
#         return send_file(BytesIO(buffer), mimetype='image/jpeg')

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

def detect_live():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image received"}), 400

        file = request.files['image']
        data = file.read()


        if not data:
            return jsonify({"error": "Empty file"}), 400

        img = cv.imdecode(np.frombuffer(data, np.uint8), cv.IMREAD_COLOR)

        if img is None:
            return jsonify({"error": "Decode failed"}), 400

        # Resize for CPU speed (IMPORTANT)
        img = cv.resize(img, (640, 480))

        # Convert BGR → RGB
        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        # YOLO inference (CPU optimized)
        results = model(
            img_rgb,
            imgsz=320,   # 👈 speed boost
            conf=0.4,
            device="cpu"
        )

        # Draw bounding boxes
        for r in results:
            if r.boxes is not None:
                for box in r.boxes.xyxy:
                    x1, y1, x2, y2 = map(int, box[:4])
                    cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Encode and return image
        _, buffer = cv.imencode('.jpg', img)
        return send_file(BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        return jsonify({"error": str(e)}), 500
