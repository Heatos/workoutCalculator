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
    id: Mapped[int] = mapped_column( primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    muscles_id: Mapped[int] = mapped_column(ForeignKey('muscles_exercise.id'))
    __table_args__ = (
        UniqueConstraint("name", name="uq_muscle_exercise_name"),
    )

class Workout(Base):
    __tablename__ = 'workout'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey('exercise.id'))
    sets: Mapped[int] = mapped_column(nullable=False, default=0)
    __table_args__ = (
        UniqueConstraint("exercise_id", "sets", name="uq_workout_exercise_sets"),
    )

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
        for i, exercise in enumerate(exercises, start=0):
            exercise_id = (
                select(Exercise.id)
                .where(Exercise.name == exercise)
                .scalar_subquery()
            )
            conn.execute(
                insert(Workout).values(name=name, exercise_id=exercise_id, sets=sets[i])
                .prefix_with("OR IGNORE")
            )

#return a list of all the workouts
def get_all_workouts():
    with Session(engine) as session:
        workouts = session.query(Workout).all()
        # workouts is now a list of Workout objects
        return workouts