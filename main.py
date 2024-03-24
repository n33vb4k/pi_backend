from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import certifi

app = Flask(__name__)
CORS(app)

cluster = MongoClient("mongodb+srv://Neev:bypky6-pyjgic-favTus@piproject.oczoj3i.mongodb.net/?retryWrites=true&w=majority&appName=PIproject", tlsCAFile=certifi.where())

db = cluster["ProjectDB"]
userLoginsC = db["UserLoginDB"]
glucoseC = db["GlucoseDB"]
nutritionC = db["NutritionDB"]
exerciseC = db["ExerciseDB"]


@app.route("/post-blood-sugar-data", methods=["POST"])
def post_blood_sugar_data():
    data = request.get_json()
    try:
        insert = glucoseC.insert_one({"glucose-level": data["glucose-level"], "date-time": data["date-time"]})
        return jsonify({"success": True, "error": None})
    except Exception as e:
        return jsonify({"success": False, "error": str(e) })
    

@app.route("/post-food-data", methods=["POST"])
def post_food_data():
    data = request.get_json()

@app.route("/post-exercise-data", methods=["POST"])
def post_exercise_data():
    data = request.get_json()


if __name__ == "__main__":
    app.run(debug=True)

