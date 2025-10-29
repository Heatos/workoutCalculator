from sqlalchemy import *
from sqlalchemy.orm import *
from database.muscleEnum import Muscles

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

class Base(DeclarativeBase):
    pass

class MusclesTable(Base):
    __tablename__ = 'muscles'
    name: Mapped[str] = mapped_column(primary_key=True)

class MusclesExercise(Base):
    __tablename__ = 'muscles_exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    muscle_name: Mapped[str] = mapped_column(ForeignKey('muscles.name'))
    is_main_muscle: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint("muscle_name", "is_main_muscle", name="uq_muscle_main"),
    )

class Exercise(Base):
    __tablename__ = 'exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    muscles_exercise_id: Mapped[int] = mapped_column(ForeignKey('muscles_exercise.id'))

class WorkoutExercise(Base):
    __tablename__ = 'workout_exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workout_id: Mapped[int] = mapped_column(ForeignKey('workout.id'))
    exercise_id: Mapped[int] = mapped_column(ForeignKey('exercise.id'))
    sets: Mapped[int] = mapped_column(nullable=False, default=0)
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise"),
    )

class Workout(Base):
    __tablename__ = 'workout'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

def create_tables():
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        for m in Muscles:
            conn.execute(insert(MusclesTable).values(name=m.value))

def add_exercise(name, prime_muscles, second_muscles):
    with engine.begin() as conn:
        for i, (muscle, is_main) in enumerate(
                [(m, True) for m in prime_muscles] + [(m, False) for m in second_muscles],
                start=0
        ):
            conn.execute(
                insert(MusclesExercise).values(muscle_name=muscle.value, is_main_muscle=is_main)
                .prefix_with("OR IGNORE"))
            select_muscle_id = get_muscle_id(is_main, muscle)
            conn.execute(
                insert(Exercise).values(name=name, muscles_exercise_id=select_muscle_id)
                .prefix_with("OR IGNORE")
            )

def add_workout(name, exercises, sets):
    with engine.begin() as conn:
        result = conn.execute(
            insert(Workout).values(name=name)
        )
        workout_id = result.inserted_primary_key[0]

        for i, exercise in enumerate(exercises):
            exercise_id = get_exercise_id(exercise, conn)

            conn.execute(
                insert(WorkoutExercise).values(
                    workout_id=workout_id,
                    exercise_id=exercise_id,
                    sets=sets[i]
                )
            )

def update_workout(workout_id, exercises, sets):

    with engine.begin() as conn:
        current_workout_exercises = conn.execute(
            select(WorkoutExercise.exercise_id)
            .where(WorkoutExercise.workout_id == workout_id)
        ).scalars().all()

        #get exercise_id
        for i, exercise in enumerate(exercises):
            exercise_id = get_exercise_id(exercise, conn)
            if exercise_id in current_workout_exercises:
                current_workout_exercises.remove(exercise_id)
                conn.execute(
                    update(WorkoutExercise)
                    .where(WorkoutExercise.workout_id == workout_id)
                    .where(WorkoutExercise.exercise_id == exercise_id)
                    .values(sets=sets[i])
                )
            else:
                delete_exercise_id(workout_id, exercise_id, conn)
        for exercise_id in current_workout_exercises:
            delete_exercise_id(workout_id, exercise_id, conn)

def get_exercise_id(exercise, conn):
        return conn.execute(
            select(Exercise.id).where(Exercise.name == exercise)
        ).scalar_one()

def get_muscle_id(is_main, muscle):
    return (
        select(MusclesExercise.id)
        .where(MusclesExercise.muscle_name == muscle.value)
        .where(MusclesExercise.is_main_muscle == is_main)
        .scalar_subquery())

def get_exercises_in_workout(conn, workout_id):
    return conn.execute(
        select(WorkoutExercise.exercise_id).where(WorkoutExercise.id == workout_id)
    ).all()

def get_exercise_name(conn, exercise_id):
    return conn.execute(
        select(Exercise.name).where(Exercise.id == exercise_id)
    ).scalar()

def delete_exercise_id(workout_id, exercise_id, conn):
    conn.execute(
        delete(WorkoutExercise)
        .where(WorkoutExercise.workout_id == workout_id)
        .where(WorkoutExercise.exercise_id == exercise_id)
    )

#return a list of all the workouts
def get_all_workouts():
    with engine.begin() as conn:
        workouts = conn.execute(
            select(Workout.id, Workout.name)
        )

    return [dict(id = w.id, name = w.name) for w in workouts]

def get_exercises(workout_id):
    with engine.begin() as conn:
        # get all exercise_ids from the workout
        exercise_rows = get_exercises_in_workout(conn, workout_id)
        output = []
        for row in exercise_rows:
            exercise_id = row[0]
            exercise_name = get_exercise_name(conn, exercise_id)
            output.append((exercise_name, exercise_id))
        return output

def get_workout_exercise(conn, workout_id):
    return conn.execute(
        select(WorkoutExercise.id, WorkoutExercise.sets)
        .where(WorkoutExercise.workout_id == workout_id)
    )

#creates a dictionary from muscles to how many sets they have in this list of workout ids
def workout_list_to_muscles(workout_id_list):
    output_dict = {muscle.value: 0 for muscle in Muscles}

    for workout_id in workout_id_list:
        workout_to_muscles(workout_id, output_dict)
    return output_dict

#adds to the dictionary the amount of sets a single workout adds to muscle groups
def workout_to_muscles(workout_id, output_dict):
    #get exercise
    with engine.begin() as conn:
        workout_exercise = get_workout_exercise(conn, workout_id)
        for work_exercise in workout_exercise:
            exercise_to_muscle(work_exercise, output_dict)

#adds to the dictionary the amount of sets a single exercise adds
def exercise_to_muscle(work_exercise, output_dict):
    with engine.begin() as conn:
        exercises = conn.execute(
            select(Exercise.id, Exercise.muscles_exercise_id)
            .where(Exercise.muscles_exercise_id == work_exercise.id)
        )
        for exercise in exercises:
            muscles_to_muscle(exercise, output_dict, work_exercise.sets)

#adds the amount of sets a single exercise gives
def muscles_to_muscle(exercise, output_dict, sets):
    with engine.begin() as conn:
        muscles = conn.execute(
            select(MusclesExercise.muscle_name, MusclesExercise.is_main_muscle)
            .where(MusclesExercise.id == exercise.muscles_exercise_id)
        )
    for muscle in muscles:
        if muscle.is_main_muscle:
            output_dict[muscle.muscle_name] += sets
        else:
            output_dict[muscle.muscle_name] += (sets * 0.5)

def get_workout_ids(workouts_1):
    out_list = []
    for workout in workouts_1:
        out_list.append(workout['id'])  # add the id to the output list
    return out_list

def print_all_tables():
    with engine.begin() as conn:
        for table_name, table in Base.metadata.tables.items():
            print(f"\n--- {table_name.upper()} ---")
            rows = conn.execute(select(table)).all()
            if not rows:
                print("(empty)")
            else:
                for row in rows:
                    print(dict(row._mapping))  # Row -> dict for nice printing