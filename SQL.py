import sqlite3 as sq
from muscleEnum import Muscles

con = sq.connect('database.db')
cur = con.cursor()

def create_tables():

    cur.execute("""
                CREATE TABLE Muscles
                (
                    Name TEXT PRIMARY KEY
                );
                """)
    cur.execute("""
                CREATE TABLE MusclesExercise
                (
                    MusclesExerciseId INTEGER PRIMARY KEY AUTOINCREMENT,
                    MuscleName TEXT NOT NULL,
                    IsMainMuscle INTEGER DEFAULT 0,
                    FOREIGN KEY (MuscleName) REFERENCES Muscles (Name)
                    UNIQUE(MuscleName, IsMainMuscle)
                );
                """)
    cur.execute("""
                create table Exercise
                (
                    ExerciseId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    MusclesId INTEGER NOT NULL,
                    FOREIGN KEY (MusclesId) REFERENCES MusclesExercise (MusclesExerciseId),
                    UNIQUE(Name)
                );
                """)
    cur.execute("""
                create table Workout
                (
                    WorkoutId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    ExerciseId INTEGER,
                    Sets INTEGER NOT NULL,
                    FOREIGN KEY (ExerciseId) REFERENCES Exercise (ExerciseId),
                    UNIQUE(ExerciseId, Sets)
                )
                """)

    cur.executemany("INSERT OR IGNORE INTO Muscles (Name) VALUES (?)",
                    [(m.value,) for m in Muscles])

    con.commit()
#name is the name of the exercise
#prime_muscles is a list of muscles that this exercise primary uses
#second_muscles is a list of muscles that this exercise uses secondary

def add_exercise(name, prime_muscles, second_muscles):
    try:
        for i, (muscle, is_main) in enumerate(
                [(m, True) for m in prime_muscles] + [(m, False) for m in second_muscles],
                start=0
        ):
            cur.execute(
                "INSERT OR IGNORE INTO MusclesExercise (MuscleName, IsMainMuscle) VALUES (?, ?);",
                (muscle.value, is_main))
            muscle_id = cur.execute(
                "SELECT MusclesExerciseId FROM MusclesExercise WHERE MuscleName=? AND IsMainMuscle=?;",
                (muscle.value, is_main)
            ).fetchone()[0]
            cur.execute(
                "INSERT OR IGNORE INTO Exercise (Name, MusclesId) VALUES (?, ?);",
                (name, muscle_id))
        """for muscle in second_muscles:
            cur.execute("INSERT OR IGNORE INTO MusclesExercise (MusclesName, IsMainMuscle) VALUES (?, ?);",
                        (muscle.value, False))
            muscle_id = cur.execute("SELECT MusclesId FROM MusclesExercise WHERE MusclesName=?;", muscle.value).fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO Exercise (Name, MuscleId) VALUES (?, ?);",
                        (name, muscle_id))"""
    except sq.IntegrityError:
        return False
    finally:
        con.commit()

def add_workout(name, exercises, sets):
    try:
        for i, exercise in enumerate(exercises, start=0):
            exercise_id = cur.execute(
                "SELECT ExerciseId FROM Exercise WHERE Name=?;",
                (exercise,)
            ).fetchone()[0]
            cur.execute(
                """INSERT OR IGNORE INTO Workout (Name, ExerciseId, Sets) VALUES (?, ?, ?)""",
                (name, exercise_id, sets[i])
            )
    except sq.IntegrityError:
        return False
    finally:
        con.commit()