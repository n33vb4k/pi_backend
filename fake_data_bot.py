from datetime import datetime, timedelta
from random import randint, choice
import requests
from time import sleep

def create_fake_exercise_data():
  # 1 exercise per day for the last 90 days
  # between 300 and 2000 calories burned
  # between 30 and 120 minutes

  exercise_types = ["running", "cycling", "swimming", "weightlifting", "yoga"]

  size_words = ["small", "medium", "large"]

  current_date = datetime.now()
  for i in range(90):
    chosen_exercise = choice(exercise_types)


    exercise_data = {
      "dateTime": current_date.isoformat(),
      "caloriesBurnt": randint(300, 2000),
      "exerciseName": f"{choice(size_words)} {chosen_exercise}",
      "duration": randint(30, 120),
      "username": "Neev123",
      "exerciseType": chosen_exercise
    }

    print(exercise_data)
    # Send a POST request to the API
    response = requests.post("http://127.0.0.1:10000/exercise", json=exercise_data)

    # Sleep for a second
    sleep(1)

    current_date -= timedelta(days=1)

def create_fake_glucose_data():
  # 1 reading every 2 hours for the last 30 days
  # between 4.0 and 10.0 mmol/L

  current_date = datetime.now()
  for i in range(30 * 12):
    glucose_data = {
      "dateTime": current_date.isoformat(),
      "glucoseLevel": randint(40, 100) / 10.0,
      "username": "Neev123",
      "description": "Random glucose reading"
    }

    print(glucose_data)
    # Send a POST request to the API
    response = requests.post("http://127.0.0.1:10000/glucose", json=glucose_data)

    current_date -= timedelta(hours=2)


def create_fake_nutrition_data():
  # 3 meals per day for the last 30 days
  # between 800 and 1200 calories

  breakfasts = ["cereal", "toast", "eggs", "pancakes", "fruit", "yogurt"]

  # Add breakfasts
  current_date = datetime.now() - timedelta(hours=6)
  for i in range(30):
    nutrition_data = {
      "dateTime": current_date.isoformat(),
      "foodName": choice(breakfasts),
      "quantity": f"{randint(200, 800)}g",
      "calories": randint(300, 500),
      "username": "Neev123"
    }

    print(nutrition_data)
    # Send a POST request to the API
    response = requests.post("http://127.0.0.1:10000/nutrition", json=nutrition_data)

    current_date -= timedelta(days=1)

    sleep(1)

  # Add lunches
  current_date = datetime.now() - timedelta(hours=1)

  lunches = ["sandwich", "salad", "soup", "pasta", "burger", "pizza"]

  for i in range(30):
    nutrition_data = {
      "dateTime": current_date.isoformat(),
      "foodName": choice(lunches),
      "quantity": f"{randint(300, 800)}g",
      "calories": f"{randint(400, 800)}",
      "username": "Neev123"
    }

    print(nutrition_data)
    # Send a POST request to the API
    response = requests.post("http://127.0.0.1:10000/nutrition", json=nutrition_data)

    current_date -= timedelta(days=1)

  # Add dinners
  current_date = datetime.now() + timedelta(hours=3)

  dinners = ["steak", "chicken", "fish", "curry", "stir fry", "roast dinner"]

  for i in range(30):
    nutrition_data = {
      "dateTime": current_date.isoformat(),
      "foodName": choice(dinners),
      "quantity": f"{randint(400, 800)}g",
      "calories": f"{randint(500, 1000)}",
      "username": "Neev123"
    }

    print(nutrition_data)
    # Send a POST request to the API
    response = requests.post("http://127.0.0.1:10000/nutrition", json=nutrition_data)

# if __name__ == "__main__":
  # create_fake_exercise_data()
  # requests.delete('http://127.0.0.1:10000/glucose?username=Neev123')
  # create_fake_glucose_data()
  # create_fake_nutrition_data()