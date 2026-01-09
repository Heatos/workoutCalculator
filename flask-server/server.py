import sys
from pathlib import Path

# Add parent directory to path so we can import database
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify
from flask_cors import CORS  # type: ignore
import database.SQLTables as sq

app = Flask(__name__)
CORS(app)  # Enable CORS for React app

# Initialize database tables on startup
sq.create_tables()

#members API route
@app.route("/members")
def members():
    return {"members": ["Member 1", "Member 2", "Member 3"]}

@app.route("/workouts", methods=["GET"])
def get_workouts():
    all_workouts = sq.get_all_workouts()
    return {"workouts": all_workouts}

@app.route("/workouts", methods=["POST"])
def add_workout():
    try:
        data = request.get_json()
        name = data.get("name")
        exercises = data.get("exercises", [])
        sets = data.get("sets", [])
        
        if not name:
            return jsonify({"error": "Workout name is required"}), 400
        
        if not exercises or not sets:
            return jsonify({"error": "Exercises and sets are required"}), 400
        
        if len(exercises) != len(sets):
            return jsonify({"error": "Number of exercises must match number of sets"}), 400
        
        # Convert sets to integers
        sets = [int(s) for s in sets]
        
        sq.add_workout(name, exercises, sets)
        return jsonify({"message": "Workout added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/exercises", methods=["GET"])
def get_exercises():
    all_exercises = sq.get_all_exercises()
    return {"exercises": all_exercises}

if __name__ == "__main__":
    app.run(debug=True)

