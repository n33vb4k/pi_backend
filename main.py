from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import certifi
import os

app = Flask(__name__)
CORS(app)

cluster = MongoClient(os.environ["URL"], tlsCAFile=certifi.where())

db          = cluster["ProjectDB"]
userLoginsC = db["UserLoginDB"]        #Username (str, PK), Email (str), Password(str)
glucoseC    = db["GlucoseDB"]          #username (str, FK), glucoseLevel (float), datetime (time), description(string)
nutritionC  = db["NutritionDB"]        #username (str, FK), foodName (str), quantity (float), calories(int)
exerciseC   = db["ExerciseDB"]         #username (str, FK), exerciseName (str), quantity (int), caloriesBurnt(int),  exerciseType(string)

# ---------------------------------config------------------------------


@app.route("/username-exists", methods = ["GET"])
def check_user():
    data = request.get_json()
    try:
        check = userLoginsC.find_one({
            "username" : data["username"]
        })
        if check and len(check) != 0:
            return jsonify({"success": True, "message": "User exists"}), 200
        else:
            return jsonify({"success": True, "message": "User not found, please register"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    

@app.route("/login" , methods = ["GET"])
def login():
    data = request.get_json()
    try:
        check = userLoginsC.find_one({
            "username" : data["username"],
            "password" : data["password"]
        })
        if check and len(check) != 0:
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            return jsonify({"success": False, "message": "Login failed"}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
    


@app.route("/register", methods = ["POST"])
def register():
    pass


@app.route("/post-glucose", methods=["POST"])
def post_blood_sugar_data():
    data = request.get_json()
    try:
        insert = glucoseC.insert_one({
            "glucose_level" : data["glucoseLevel"], 
            "date_time"     : data["dateTime"],
            })
        return jsonify({"success": True, "error": None}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 400
    

@app.route("/post-nutrition", methods=["POST"])
def post_food_data():
    data = request.get_json()
    #check if calories are null, then use API to calculate the calories
    try:
        insert = nutritionC.insert_one({
            "food_name": data["foodName"], 
            "quantitiy": data["quantity"], 
            "calories" : data["calories"],
            })
        return jsonify({"success": True, "error": None}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 401


@app.route("/post-exercise", methods=["POST"])
def post_exercise_data():
    data = request.get_json()
    #check if caloriesBurnt is null, then use api to calculate 
    try:
        insert = exerciseC.insert_one({
            "exercise_name"  : data["exerciseName"], 
            "reps"           : data["reps"], 
            "calories_burnt" : data["caloriesBurnt"],
            })
        return jsonify({"success": True, "error": None}), 202
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 402


if __name__ == "__main__":
    app.run(debug=True)

