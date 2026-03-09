from sqlalchemy import *
from sqlalchemy.orm import *
from pathlib import Path
from database.muscleEnum import Muscles

# Use persistent database file instead of in-memory
db_path = Path(__file__).parent.parent / "workout.db"
engine = create_engine(f"sqlite+pysqlite:///{db_path}", echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class MusclesTable(Base):
    __tablename__ = 'muscles'
    name: Mapped[str] = mapped_column(primary_key=True)

class MusclesExercise(Base):
    __tablename__ = 'muscles_exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    muscle_name: Mapped[str] = mapped_column(ForeignKey('muscles.name'))
    exercise_id: Mapped[int] = mapped_column(ForeignKey('exercise.id'))
    is_main_muscle: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    __table_args__ = (
        UniqueConstraint("muscle_name", "exercise_id", "is_main_muscle", name="uq_muscle_main"),
    )

class Exercise(Base):
    __tablename__ = 'exercise'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

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

def populate_muscle_table():
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        existing_muscles = {
            name for (name,) in session.query(MusclesTable.name).distinct().all()
        }
        for m in Muscles:
            if m.value not in existing_muscles:
                session.add(MusclesTable(name=m.value))
                session.flush()
        session.commit()

def add_exercise(name, prime_muscles, second_muscles):
    with SessionLocal() as session:
        exercise = get_or_create_exercise(name, session)
        for i, (muscle, is_main) in enumerate([(m, True) for m in prime_muscles] + [(m, False) for m in second_muscles],start=0):
            get_me = session.query(MusclesExercise).filter_by(exercise_id=exercise.id, muscle_name=muscle.value, is_main_muscle=is_main).first()
            if not get_me:
                session.add(MusclesExercise(muscle_name=muscle.value, exercise_id=exercise.id, is_main_muscle=is_main))
        session.commit()
        return exercise.id

def get_or_create_exercise(name, session):
    exercise = session.query(Exercise).filter_by(name=name).first()
    if exercise is not None:
        return exercise
    exercise = Exercise(name=name)
    session.add(exercise)
    session.flush()
    session.commit()
    return exercise

def add_workout(name, exercises, sets):
    with SessionLocal() as session:
        workout = Workout(name=name)
        session.add(workout)
        session.flush()
        for i, exercise in enumerate(exercises):
            exercise_id = get_exercise_id(exercise)
            we = WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=exercise_id,
                    sets=sets[i]
            )
            session.add(we)
        session.commit()
        return workout.id

def update_workout(workout_id, exercises, sets):
    with SessionLocal() as session:
        # Map: exercise_id -> WorkoutExercise row
        existing = {
            row.exercise_id: row
            for row in session.query(WorkoutExercise)
                              .filter_by(workout_id=workout_id)
                              .all()
        }
        # Track which exercise_ids we have processed
        seen = set()
        for i, exercise in enumerate(exercises):
            exercise_id = get_exercise_id(exercise)
            seen.add(exercise_id)

            if exercise_id in existing:
                # Update sets
                existing[exercise_id].sets = sets[i]
            else:
                # Add new exercise to workout
                we = WorkoutExercise(
                    workout_id=workout_id,
                    exercise_id=exercise_id,
                    sets=sets[i]
                )
                session.add(we)

        # Delete exercises that are no longer in the workout
        for exercise_id in existing:
            if exercise_id not in seen:
                session.query(WorkoutExercise).filter_by(
                    workout_id=workout_id,
                    exercise_id=exercise_id
                ).delete()

        session.commit()

def get_exercise_id(exercise):
    with SessionLocal() as session:
        e = session.query(Exercise).where(Exercise.name == exercise).first()
        return e.id

def get_exercises_in_workout(session, workout_id):
    return session.query(WorkoutExercise.exercise_id).filter(WorkoutExercise.workout_id == workout_id).all()

def get_exercise_name(session, exercise_id):
    return session.query(Exercise.name).filter(Exercise.id == exercise_id).first()[0]

def delete_exercise_id(workout_id, exercise_id):
    with SessionLocal as session:
        session.execute(
            delete(WorkoutExercise)
            .where(WorkoutExercise.workout_id == workout_id)
            .where(WorkoutExercise.exercise_id == exercise_id)
        )

#return a list of all the workouts
def get_all_workouts():
    with SessionLocal as session:
        workouts = session.execute(
            select(Workout.id, Workout.name)
        )

    return [dict(id=w.id, name=w.name) for w in workouts]

#return a list of all exercises
def get_all_exercises():
    with SessionLocal as session:
        exercises = session.execute(
            select(Exercise.id, Exercise.name)
        )
        result = []
        for e in exercises:
            # Fetch primary and secondary muscles here
            primary_muscles = [m.id for m in e.primary_muscles]  # if relationship
            secondary_muscles = [m.id for m in e.secondary_muscles]
            result.append({
                "id": e.id,
                "name": e.name,
                "primary_muscles": primary_muscles,
                "secondary_muscles": secondary_muscles
            })
        return result

def get_exercises(workout_id):
    with SessionLocal() as session:
        # get all exercise_ids from the workout
        exercise_rows = get_exercises_in_workout(session, workout_id)
        output = []
        for row in exercise_rows:
            exercise_id = row[0]
            exercise_name = get_exercise_name(session, exercise_id)
            output.append((exercise_name, exercise_id))
        return output

def get_workout_exercise(session, workout_id):
    return session.query(WorkoutExercise).filter_by(workout_id=workout_id).all()

#creates a dictionary from muscles to how many sets they have in this list of workout ids
def workout_list_to_muscles(workout_id_list):
    output_dict = {muscle.value: 0 for muscle in Muscles}
    for workout_id in workout_id_list:
        workout_to_workout_exercise(workout_id, output_dict)
    return output_dict

#adds to the dictionary the amount of sets a single workout adds to muscle groups
def workout_to_workout_exercise(workout_id, output_dict):
    #get exercise
    with SessionLocal() as session:
        workout_exercise = get_workout_exercise(session, workout_id)
        for work_exercise in workout_exercise:
            workout_exercise_to_exercise(session, work_exercise, output_dict)



def workout_exercise_to_exercise(session, workout_exercise, output_dict):
    exercise = session.query(Exercise).filter_by(id=workout_exercise.exercise_id).all()

#adds to the dictionary the amount of sets a single exercise adds
def exercise_to_muscle(session, work_exercise, output_dict):
    exercises = session.query(Exercise).filter_by(id=work_exercise.exercise.id).all()
    for exercise in exercises:
        muscles_to_muscle(session, exercise, output_dict, work_exercise.sets)

#adds the amount of sets a single exercise gives
def muscles_to_muscle(session, exercise, output_dict, sets):
    muscles = session.query(MusclesExercise).filter_by(exercise_id=exercise.id)
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
    with SessionLocal as session:
        for table_name, table in Base.metadata.tables.items():
            print(f"\n--- {table_name.upper()} ---")
            rows = session.execute(select(table)).all()
            if not rows:
                print("(empty)")
            else:
                for row in rows:
                    print(dict(row._mapping))  # Row -> dict for nice printing
