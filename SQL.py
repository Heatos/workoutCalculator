import sqlite3 as sq
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
                );
                """)
    cur.execute("""
                create table Exercise
                (
                    ExerciseId INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    MusclesId INTEGER NOT NULL,
                    FOREIGN KEY (MusclesId) REFERENCES MusclesExercise (MusclesExerciseId)
                );
                """)
    cur.execute("""
                create table Workout
                (
                    WorkoutId INTEGER PRIMARY KEY AUTOINCREMENT
                );
                """)
    cur.execute("""
                create table WorkoutExercise
                (
                    WorkoutExerciseId INTEGER PRIMARY KEY AUTOINCREMENT,
                    ExerciseId INTEGER,
                    WorkoutId INTEGER,
                    Sets INTEGER NOT NULL,
                    FOREIGN KEY (ExerciseId) REFERENCES Exercise (ExerciseId),
                    FOREIGN KEY (WorkoutId) REFERENCES Workouts (WorkoutId)
                )
                """)

    muscles = ['Abs', 'Biceps', 'Calves', 'Chest', 'Forearms', 'Glutes', 'Hamstrings', 'Lats',
               'Lowerback', 'Quadriceps', 'Shoulders', 'Trapezius', 'Triceps', 'Upperback']
    cur.executemany("INSERT OR IGNORE INTO Muscles (Name) VALUES (?)", [(muscles,) for muscles in muscles])

    con.commit()
    con.close()