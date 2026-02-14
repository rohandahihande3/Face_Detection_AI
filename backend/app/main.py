from flask import Flask
from flask_cors import CORS
from app.API.cv import open_cv_api
from app.API.chat_bot import chat_bp
from app.API import main_app
def create_app():
    app = Flask(__name__)
    # CORS(app, resources={r"/*": {
    #     "origins": [
    #         "https://facedetectionai-projects.vercel.app",     # your frontend domain
    #         "http://localhost:3000"                            # development
    #     ],
    #     "methods": ["GET", "POST", "OPTIONS"],
    #     "allow_headers": ["Content-Type"],
    # }})

    CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"],
    }})
    app.register_blueprint(open_cv_api)
    app.register_blueprint(chat_bp)
    app.register_blueprint(main_app)    
    return app

