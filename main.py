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
import requests

load_dotenv()

app = Flask(__name__)
CORS(app)

cluster = MongoClient(os.getenv('URL'), tlsCAFile=certifi.where())

db          = cluster["ProjectDB"]
userLoginsC = db["UserLoginDB"]        #Username (str, PK), Email (str), Password(str)
glucoseC    = db["GlucoseDB"]          #username (str, FK), glucoseLevel (float), datetime (time), description(string)
nutritionC  = db["NutritionDB"]        #username (str, FK), foodName (str), quantity(float), datetime(time), calories(int)
exerciseC   = db["ExerciseDB"]         #username (str, FK), exerciseName (str), quantity (int), caloriesBurnt(int),  exerciseType(string), datetime(time)
goalsC      = db["GoalsDB"]            #username (str, FK), goalType (str), goal(int), dateSet(time)


AUTOCOMPLETE_APP_ID = os.getenv('AUTOCOMPLETE_FOOD_APP_ID')
AUTOCOMPLETE_APP_KEY = os.getenv('AUTOCOMPLETE_FOOD_APP_KEY')
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
                                "date_time"       : {'$gte': start_time}},
                                {"_id"            :0,  #setting to 0 so wont appear in output
                                 "username"       :0,
                                })

        return jsonify({"success": True, "values":list(search)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 401


@app.route("/nutrition", methods=["POST"])
def post_food_data():
    data = request.get_json()
    datetime_object = datetime.fromisoformat(data["dateTime"])
    try:
        food_name = data["foodName"]
        quantity = data["quantity"]
        macros = calculate_macros(food_name, quantity)

        if macros:
            food_info = {
                "calories"       : data["calories"] if data["calories"] else macros["calories"],
                "carbs_g"        : macros["carbohydrates_total_g"],
                "fat_saturated_g": macros["fat_saturated_g"],
                "fat_total_g"    : macros["fat_total_g"],
                "cholesterol_mg" : macros["cholesterol_mg"],
                "fiber_g"        : macros["fiber_g"],
                "potassium_mg"   : macros["potassium_mg"],
                "protein_g"      : macros["protein_g"],
                "sodium_mg"      : macros["sodium_mg"],
                "sugar_g"        : macros["sugar_g"]
            }
        else:
            food_info = {key: None for key in [
                "calories", "carbs_g", "fat_saturated_g",
                "fat_total_g", "cholesterol_mg", "fiber_g",
                "potassium_mg", "protein_g", "sodium_mg", "sugar_g"
            ]}
            food_info["calories"] = data["calories"]

        insert = nutritionC.insert_one({
            "username": data["username"],
            "date_time": datetime_object,
            "food_name": food_name,
            "quantitiy": f"{quantity}g" if quantity[-1] != "g" else quantity,
            **food_info
        })

        return jsonify({"success": True, "error": None if macros else "Food not found"}), 201 if macros else 202
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401


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
                                "date_time"       : {'$gte': start_time}},
                                {"_id"            :0,
                                 "username"       :0,
                                })
        return jsonify({"success": True, "values":list(search)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 401


def calculate_macros(food_name, quantity):
    if quantity[-1] == "g":
        quantity = quantity[:-1]
    param = f"{quantity}g {food_name}"
    response = requests.get(f"https://api.api-ninjas.com/v1/nutrition?query={param}", headers={"X-Api-Key": "nQjzGP7PAqn9meZuXO4FNQ==9otkCayUm9ju0N1Q"})
    try:
        json = response.json()[0]
        return json
    except Exception as e:
        return None


@app.route("/exercise", methods=["POST"])
def post_exercise_data():
    data = request.get_json()
    datetime_object = datetime.fromisoformat(data["dateTime"])
    try:
        exercise_name = data["exerciseName"]
        duration = data["duration"]
        info = calculate_calories_burnt(exercise_name, duration)
        if info:
            calories_burnt = data["caloriesBurnt"] if data["caloriesBurnt"] else info["total_calories"]
        else:
            calories_burnt = data["caloriesBurnt"]

        insert = exerciseC.insert_one({
            "username"       : data["username"],
            "date_time"      : datetime_object,
            "exercise_name"  : data["exerciseName"],
            "duration"       : data["duration"],
            "calories_burnt" : calories_burnt,
            "exercise_type"  : data["exerciseType"],
            })
        return jsonify({"success": True, "error": None if info else "Exercise not found"}), 201 if info else 202
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e), "info" : info}), 402


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
                                "date_time"       : {'$gte': start_time}},
                                {"_id"            :0,
                                 "username"       :0,
                                })
        return jsonify({"success": True, "values":list(search)}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e) }), 402


def calculate_calories_burnt(exercise_name, duration):
    response = requests.get(f"https://api.api-ninjas.com/v1/caloriesburned?activity={exercise_name}&duration={duration}", headers={"X-Api-Key": "nQjzGP7PAqn9meZuXO4FNQ==9otkCayUm9ju0N1Q"})
    try:
        json = response.json()[0]
        return json
    except Exception as e:
        return None


@app.route("/autocomplete_food", methods = ['GET'])
def get_autocomplete_food():
    partial_food = request.args.get('q')
    url = f"https://api.edamam.com/auto-complete?app_id={AUTOCOMPLETE_APP_ID}&app_key={AUTOCOMPLETE_APP_KEY}&q={partial_food}"
    response = requests.get(url)
    print(response.json())
    try:
        print(response.json())
        return jsonify({"success": True}, response.json()), 200
    except Exception as e:
        return jsonify({"success": False, "error": e}), 402


@app.route("/goal", methods = ["GET"])
def get_goal():
    data = request.get_json()

    username = data["username"]
    goal_type = data["goalType"]
    target = data["target"]
    field = data["field"]
    time_span = data["timeSpan"]

    if (goal_type not in ["nutrition", "exercise", "glucose"]):
        return jsonify({"success": False, "error": "Invalid goal type"}), 402

    try:
        goal = goalsC.find_one({
            "username" : username,
            "goal_type": goal_type,
            "target"   : target,
            "field"    : field,
            "time_span": time_span
        }, sort=[('dateSet', -1)])

        if goal:
            return jsonify({"success": True, "value": goal["goal"]}), 200
        else:
            return jsonify({"success": False, "error": "No goal found"}), 402
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 402


@app.route("/goal", methods = ["POST"])
def set_goal():
    data = request.get_json()

    username = data["username"]
    goal_type = data["goalType"]
    target = data["target"]
    field = data["field"]
    time_span = data["timeSpan"]

    if (goal_type not in ["nutrition", "exercise", "glucose"]):
        return jsonify({"success": False, "error": "Invalid goal type"}), 402

    try:
        find = goalsC.find_one({
            "username" : username,
            "goal_type": goal_type,
            "time_span": time_span
        })
        
        if find is not None and len(find) != 0:
            goalsC.update_one({
                "username" : username,
                "goal_type": goal_type,
                "time_span": time_span }, 
                {"$set": {
                "target" : target}
                })
        else:
            goalsC.insert_one({
                "username" : username,
                "goal_type": goal_type,
                "target"   : target,
                "field"    : field,
                "time_span": time_span,
                "dateSet"  : datetime.now()
            })
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 402


@app.route("/goal_progress", methods = ["GET"])
def check_goal_progress():
    #goal should be in the format "target(2000) field(e.g calories) time_span(day/week/month/year)"
    data = request.get_json()
    
    username = data["username"]
    goal_type = data["goalType"]
    target = data["target"]
    field = data["field"]
    time_span = data["timeSpan"]

    match goal_type:
        case "nutrition":
            collection = nutritionC
        case "exercise": 
            collection = exerciseC
        case "glucose":
            collection = glucoseC
    
    start_time = datetime.now()
    match time_span:
        case "day":
            start_time = datetime.now() - timedelta(days=1)
        case "week":
            start_time = datetime.now() - timedelta(weeks=1)
        case "month":
            start_time = datetime.now() - timedelta(weeks=4)
        case "year":
            start_time = datetime.now() - timedelta(weeks=52)

    try:
        search = collection.find({
            "username": username,
            "date_time": {'$gte': start_time}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 402

    current = 0
    count = 0
    for entry in search:
        count += 1
        current += entry[field]
    
    if goal_type == "glucose":
        current = current/count
    
    return jsonify({"success": True,
                    "current": current,
                    "progress": current/target}), 200
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000,debug=True)
