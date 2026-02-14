from flask import Blueprint ,request,jsonify

main_app = Blueprint("main_app",__name__)

main_app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Face Detection AI API!"})