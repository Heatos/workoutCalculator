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
    muscles_id: Mapped[int] = mapped_column(ForeignKey('muscles_exercise.id'))

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
    name: Mapped[str] = mapped_column(nullable=False)  # one row per workout

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
            select_muscle_id = (
                select(MusclesExercise.id)
                .where(MusclesExercise.muscle_name == muscle.value)
                .where(MusclesExercise.is_main_muscle == is_main)
                .scalar_subquery())
            conn.execute(
                insert(Exercise).values(name=name, muscles_id=select_muscle_id)
                .prefix_with("OR IGNORE")
            )

def add_workout(name, exercises, sets):
    with engine.begin() as conn:
        result = conn.execute(
            insert(Workout).values(name=name)
        )
        workout_id = result.inserted_primary_key[0]

        for i, exercise in enumerate(exercises):
            exercise_id = conn.execute(
                select(Exercise.id).where(Exercise.name == exercise)
            ).scalar_one()

            conn.execute(
                insert(WorkoutExercise).values(
                    workout_id=workout_id,
                    exercise_id=exercise_id,
                    sets=sets[i]
                )
            )

#return a list of all the workouts
def get_all_workouts():
    with engine.begin() as conn:
        workouts = conn.execute(
            select(Workout.id, Workout.name).order_by(Workout.name)
        ).all()

    return [(w.name, w.id) for w in workouts]

def get_exercises(workout_id):
    with engine.begin() as conn:
        # get all exercise_ids from the workout
        exercise_rows = conn.execute(
            select(WorkoutExercise.exercise_id).where(WorkoutExercise.id == workout_id)
        ).all()
        output = []
        for row in exercise_rows:
            exercise_id = row[0]
            exercise_name = conn.execute(
                select(Exercise.name).where(Exercise.id == exercise_id)
            ).scalar()
            output.append((exercise_name, exercise_id))

        return output

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