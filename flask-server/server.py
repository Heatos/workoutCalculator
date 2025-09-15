from flask import Flask
import database.main
import database.SQLTables as sq

app = Flask(__name__)

#members API route
@app.route("/members")
def members():
    return {"members": ["Member 1", "Member 2", "Member 3"]}

@app.route("/workouts")
def workouts():
    database.main.test()
    all_workouts = sq.get_all_workouts()
    # convert SQLAlchemy objects to dictionaries
    workouts_list = [
        {"id": w.id, "name": w.name}  # include any columns you want
        for w in all_workouts
    ]
    return {"workouts": workouts_list}

if __name__ == "__main__":
    app.run(debug=True)

