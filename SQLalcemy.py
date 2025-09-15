from sqlalchemy import *
from muscleEnum import Muscles


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

def create_tables():
    with engine.begin() as conn:
        #creates muscles table and populates it
        conn.execute(
            text("CREATE TABLE muscles ( name TEXT PRIMARY KEY );"))
        conn.execute(
            text("INSERT OR IGNORE INTO muscles (name) VALUES (:name)"),
            [{"name": m.value} for m in Muscles],
        )
        #creates muscles_exercise join table
        conn.execute(
            text("""CREATE TABLE muscles_exercise (
                 muscles_exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 muscle_name TEXT NOT NULL,
                 is_main_muscle int DEFAULT 0,
                 FOREIGN KEY (muscle_name) REFERENCES muscles (name),
                 UNIQUE(muscle_name, is_main_muscle))""")
        )

        #create exercise table
        conn.execute(
            text("""create table exercise (
                exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                muscles_id INTEGER NOT NULL,
                FOREIGN KEY (muscles_id) REFERENCES muscles_exercise (muscles_exercise_id),
                UNIQUE(name)
                )""")
        )
        #create workout table
        conn.execute(
            text("""create table workout (
                 workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 exercise_id int NOT NULL,
                 sets int NOT NULL,
                 FOREIGN KEY (exercise_id) REFERENCES exercise (exercise_id),
                 UNIQUE(exercise_id, sets)
                 )""")
        )

def add_exercise(name, prime_muscles, second_muscles):
    with engine.begin() as conn:
        for i, (muscle, is_main) in enumerate(
                [(m, True) for m in prime_muscles] + [(m, False) for m in second_muscles],
                start=0
        ):
            conn.execute(
                text("""INSERT OR IGNORE INTO muscles_exercise (muscle_name, is_main_muscle) VALUES (:muscles_name, :is_main_muscle)"""),
                [{"muscles_name": muscle.value, "is_main_muscle": is_main}],
            )
            #need to do this because I don't know if the exercise exists or not meaning
            #if it does exist I have to go find it
            muscle_id = conn.execute(
                text("""SELECT muscles_exercise_id FROM muscles_exercise WHERE muscle_name = :muscle_name and is_main_muscle = :is_main_muscle"""),
                [{"muscle_name": muscle.value, "is_main_muscle": is_main}],
            ).fetchone()[0]
            conn.execute(
                text("""INSERT OR IGNORE INTO exercise (name, muscles_id) VALUES (:name, :muscles_id)"""),
                [{"name": name, "muscles_id": muscle_id}],
            )

def add_workout(name, exercises, sets):
    with engine.begin() as conn:
        for i, exercise in enumerate(exercises, start=0):
            exercise_id = conn.execute(
                text("""SELECT exercise_id FROM exercise WHERE name = :exercise_name"""),
                [{"exercise_name": exercise}],
            ).fetchone()[0]
            conn.execute(
                text("""INSERT OR IGNORE INTO workout (name, exercise_id, sets) VALUES (:name, :exercise_id, :sets)"""),
                [{"name": name, "exercise_id": exercise_id, "sets": sets[i]}],
            )