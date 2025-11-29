from flask import Flask
from flask_cors import CORS
from app.API.cv import open_cv_api
from app.API.chat_bot import chat_bp
def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(open_cv_api)
    app.register_blueprint(chat_bp)    
    return app

