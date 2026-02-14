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



"""
Complete Flask app example with optimized live face detection
"""
from flask import Flask, Blueprint, request, jsonify, send_file
from flask_cors import CORS
import cv2 as cv
import numpy as np
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for your React frontend

# Create blueprint
open_cv_api = Blueprint('open_cv_api', __name__)

# ============================================
# CONFIGURATION
# ============================================
# Update this to your XML files location
XML_PATH = os.path.join(os.path.dirname(__file__), "xml_files")

# Alternative: Use OpenCV's built-in Haar cascades
# XML_PATH = cv.data.haarcascades

# Global cascade objects - loaded once at startup
FACE_CASCADE = None
EYE_CASCADE = None
NOSE_CASCADE = None
MOUTH_CASCADE = None

# ============================================
# INITIALIZE CASCADES (Called once at startup)
# ============================================
def initialize_cascades():
    """
    Load all cascade classifiers once when the server starts.
    This is MUCH faster than loading them on every request.
    """
    global FACE_CASCADE, EYE_CASCADE, NOSE_CASCADE, MOUTH_CASCADE
    
    print(f"Loading cascades from: {XML_PATH}")
    
    try:
        # Option 1: Use your custom XML files
        FACE_CASCADE = cv.CascadeClassifier(os.path.join(XML_PATH, "frontal_face.xml"))
        EYE_CASCADE = cv.CascadeClassifier(os.path.join(XML_PATH, "eye.xml"))
        NOSE_CASCADE = cv.CascadeClassifier(os.path.join(XML_PATH, "nose.xml"))
        MOUTH_CASCADE = cv.CascadeClassifier(os.path.join(XML_PATH, "mouth.xml"))
        
        # Option 2: Use OpenCV's built-in cascades (RECOMMENDED for testing)
        # FACE_CASCADE = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # EYE_CASCADE = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_eye.xml')
        # NOSE_CASCADE = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_mcs_nose.xml')
        # MOUTH_CASCADE = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_mcs_mouth.xml')
        
        # Verify they loaded correctly
        if FACE_CASCADE.empty():
            print(f"❌ ERROR: Face cascade failed to load from {XML_PATH}")
            print("   Try using OpenCV's built-in cascades by uncommenting Option 2 above")
            return False
        
        print("✅ Face cascade loaded successfully")
        
        if not EYE_CASCADE.empty():
            print("✅ Eye cascade loaded successfully")
        if not NOSE_CASCADE.empty():
            print("✅ Nose cascade loaded successfully")
        if not MOUTH_CASCADE.empty():
            print("✅ Mouth cascade loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR loading cascades: {e}")
        return False


# ============================================
# ENDPOINTS
# ============================================

@open_cv_api.route('/detect', methods=['POST'])
def detect():
    """
    Standard detection endpoint (for uploaded images).
    Can use higher quality settings since it's not real-time.
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image received"}), 400

        file = request.files['image']
        data = file.read()
        
        if not data:
            return jsonify({"error": "Empty file uploaded"}), 400

        img = cv.imdecode(np.frombuffer(data, np.uint8), cv.IMREAD_COLOR)
        
        if img is None:
            return jsonify({"error": "Unable to decode image"}), 400

        if FACE_CASCADE is None or FACE_CASCADE.empty():
            return jsonify({"error": "Cascades not initialized"}), 500

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        # Higher quality detection for uploads
        faces = FACE_CASCADE.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            if EYE_CASCADE is not None and not EYE_CASCADE.empty():
                eyes = EYE_CASCADE.detectMultiScale(roi_gray, 1.1, 5)
                for (ex, ey, ew, eh) in eyes:
                    cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            if NOSE_CASCADE is not None and not NOSE_CASCADE.empty():
                nose = NOSE_CASCADE.detectMultiScale(roi_gray, 1.1, 5)
                for (nx, ny, nw, nh) in nose:
                    cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

            if MOUTH_CASCADE is not None and not MOUTH_CASCADE.empty():
                mouth = MOUTH_CASCADE.detectMultiScale(roi_gray, 1.1, 5)
                for (mx, my, mw, mh) in mouth:
                    cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

        # High quality encoding for uploads
        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 95]
        _, buffer = cv.imencode('.jpg', img, encode_param)
        
        return send_file(BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        print(f"Error in detect: {str(e)}")
        return jsonify({"error": str(e)}), 500


@open_cv_api.route('/detect-live', methods=['POST'])
def detect_live():
    """
    OPTIMIZED live detection endpoint for real-time streaming.
    Uses lower quality settings for speed.
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image received"}), 400

        file = request.files['image']
        data = file.read()
        
        if not data:
            return jsonify({"error": "Empty file uploaded"}), 400

        img = cv.imdecode(np.frombuffer(data, np.uint8), cv.IMREAD_COLOR)
        
        if img is None:
            return jsonify({"error": "Unable to decode image"}), 400

        if FACE_CASCADE is None or FACE_CASCADE.empty():
            return jsonify({"error": "Cascades not initialized"}), 500

        # Optional: Resize for faster processing
        height, width = img.shape[:2]
        if width > 640:
            scale = 640 / width
            img = cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_LINEAR)

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        # Faster detection for live mode
        faces = FACE_CASCADE.detectMultiScale(
            gray,
            scaleFactor=1.2,  # Faster than 1.1
            minNeighbors=3,   # Less strict than 5
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            cv.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]

            if EYE_CASCADE is not None and not EYE_CASCADE.empty():
                eyes = EYE_CASCADE.detectMultiScale(roi_gray, 1.2, 3, minSize=(20, 20))
                for (ex, ey, ew, eh) in eyes:
                    cv.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

            if NOSE_CASCADE is not None and not NOSE_CASCADE.empty():
                nose = NOSE_CASCADE.detectMultiScale(roi_gray, 1.2, 3, minSize=(20, 20))
                for (nx, ny, nw, nh) in nose:
                    cv.rectangle(roi_color, (nx, ny), (nx+nw, ny+nh), (0, 0, 255), 2)

            if MOUTH_CASCADE is not None and not MOUTH_CASCADE.empty():
                mouth = MOUTH_CASCADE.detectMultiScale(roi_gray, 1.2, 3, minSize=(20, 20))
                for (mx, my, mw, mh) in mouth:
                    cv.rectangle(roi_color, (mx, my), (mx+mw, my+mh), (255, 255, 0), 2)

        # Lower quality for faster encoding
        encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 85]
        _, buffer = cv.imencode('.jpg', img, encode_param)
        
        return send_file(BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        print(f"Error in detect_live: {str(e)}")
        return jsonify({"error": str(e)}), 500


@open_cv_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify cascades are loaded"""
    status = {
        "status": "ok",
        "cascades": {
            "face": not (FACE_CASCADE is None or FACE_CASCADE.empty()),
            "eye": not (EYE_CASCADE is None or EYE_CASCADE.empty()),
            "nose": not (NOSE_CASCADE is None or NOSE_CASCADE.empty()),
            "mouth": not (MOUTH_CASCADE is None or MOUTH_CASCADE.empty())
        }
    }
    return jsonify(status)


# ============================================
# REGISTER BLUEPRINT AND START APP
# ============================================

app.register_blueprint(open_cv_api)

if __name__ == '__main__':
    print("=" * 60)
    print("Starting Face Detection API")
    print("=" * 60)
    
    # Initialize cascades before starting the server
    if not initialize_cascades():
        print("⚠️  WARNING: Cascades failed to load. Server may not work properly.")
        print("   Check your XML_PATH configuration above.")
    
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("=" * 60)
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True  # Important for handling multiple live detection requests
    )