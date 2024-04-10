# ---------------------------------config------------------------------
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import certifi
import os
from datetime import datetime, timedelta
from uuid import uuid4
from dotenv import load_dotenv
import bcrypt

load_dotenv()

app = Flask(__name__)
CORS(app)

cluster = MongoClient(os.getenv('URL'), tlsCAFile=certifi.where())

db          = cluster["ProjectDB"]
userLoginsC = db["UserLoginDB"]        #Username (str, PK), Email (str), Password(str)
glucoseC    = db["GlucoseDB"]          #username (str, FK), glucoseLevel (float), datetime (time), description(string)
nutritionC  = db["NutritionDB"]        #username (str, FK), foodName (str), quantity(float), datetime(time), calories(int)
exerciseC   = db["ExerciseDB"]         #username (str, FK), exerciseName (str), quantity (int), caloriesBurnt(int),  exerciseType(string), datetime(time)

# ---------------------------------routes------------------------------


@app.route("/username-exists", methods = ["POST"])
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
    

@app.route("/login" , methods = ["POST"])
def login():
    data = request.get_json()
    try:
        check = userLoginsC.find_one({
            "username" : data["username"]
        })
        print(check)
        if not check or len(check) == 0:
            print("No user found")
            return jsonify({"success": False, "error": str(e)}), 401
        else:

            hashed_password = str(check["password"]).encode()
            print(hashed_password)

            comparison = bcrypt.checkpw(str(data["password"]).encode(), hashed_password)


            if comparison:
                print("Password correct")
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "token"  : str(uuid4())
                }), 200
            
            else:
                print("Password")
                return jsonify({"success": False, "message": "Login failed"}), 201
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 401
    


@app.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    print("hashing password")
    hashed_password = bcrypt.hashpw(str(data["password"]).encode(), bcrypt.gensalt(12))

    try:
        insert = userLoginsC.insert_one({
            "username"  : data["username"],
            "email"     : data["email"], 
            "password"  : hashed_password.decode()
        })
        return jsonify({
            "success": True,
            "message": "user added",
            "token": str(uuid4())
        }), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e) }), 400
    


@app.route("/glucose", methods=["POST"])
def post_blood_sugar_data():
    data = request.get_json()
    datetime_object = datetime.fromisoformat(data["dateTime"])
    try:
        insert = glucoseC.insert_one({
            "username"      : data["username"],
            "glucose_level" : data["glucoseLevel"], 
            "date_time"     : datetime_object,
            "description"   : data["description"]
            })
        return jsonify({"success": True, "error": None}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 400


@app.route("/glucose", methods = ["GET"])
def get_blood_sugar_data():
    username = request.args.get("username")
    time_span = request.args.get("timeSpan") #day week month or year
    start_time = datetime.now()
    match time_span:
        case "day":
            start_time -= timedelta(days=1)
        case "week":
            start_time -= timedelta(weeks=1)
        case "month":
            start_time -= timedelta(weeks=4)
        case "year":
            start_time -= timedelta(weeks=52)

    try:
        search = glucoseC.find({"username"        : username,
                                "date-time"       : {'$gte': start_time}}, 
                                {"_id"            :0,  #setting to 0 - wont appear in output
                                 "username"       :0, 
                                })
        
        return jsonify({"success": True, "values":list(search)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 401


@app.route("/nutrition", methods=["POST"])
def post_food_data():
    data = request.get_json()
    datetime_object = datetime.fromisoformat(data["dateTime"])
    #check if calories are null, then use API to calculate the calories
    try:
        insert = nutritionC.insert_one({
            "username"  : data["username"],
            "food_name" : data["foodName"], 
            "quantitiy" : data["quantity"], 
            "calories"  : data["calories"],
            "date_time" : datetime_object
            })
        return jsonify({"success": True, "error": None}), 201
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e) }), 401


@app.route("/nutrition", methods = ["GET"])
def get_food_data():
    username = request.args.get("username")
    time_span = request.args.get("timeSpan")
    start_time = datetime.now()
    match time_span:
        case "day":
            start_time -= timedelta(days=1)
        case "week":
            start_time -= timedelta(weeks=1)
        case "month":
            start_time -= timedelta(weeks=4)
        case "year":
            start_time -= timedelta(weeks=52)
    
    try:
        search = nutritionC.find({"username"      : username,
                                "date-time"       : {'$gte': start_time}}, 
                                {"_id"            :0,
                                 "username"       :0, 
                                })
        return jsonify({"success": True, "values":list(search)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 401


@app.route("/exercise", methods=["POST"])
def post_exercise_data():
    data = request.get_json()
    datetime_object = datetime.fromisoformat(data["dateTime"])
    #check if caloriesBurnt is null, then use api to calculate 
    try:
        insert = exerciseC.insert_one({
            "username"       : data["username"],
            "exercise_name"  : data["exerciseName"], 
            "duration"       : data["duration"], 
            "calories_burnt" : data["caloriesBurnt"],
            "exercise_type"  : data["exerciseType"],
            "date_time"      : datetime_object,
            })
        return jsonify({"success": True, "error": None}), 202
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e) }), 402


@app.route("/exercise", methods = ["GET"])
def get_exercise_data():
    username = request.args.get("username")
    time_span = request.args.get("timeSpan")
    start_time = datetime.now()
    match time_span:
        case "day":
            start_time -= timedelta(days=1)
        case "week":
            start_time -= timedelta(weeks=1)
        case "month":
            start_time -= timedelta(weeks=4)
        case "year":
            start_time -= timedelta(weeks=52)
    
    try:
        search = exerciseC.find({"username"       : username,
                                "date-time"       : {'$gte': start_time}}, 
                                {"_id"            :0,
                                 "username"       :0, 
                                })
        return jsonify({"success": True, "values":list(search)}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 402


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000,debug=True)

