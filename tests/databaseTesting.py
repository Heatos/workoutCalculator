import pytest
from database.SQLTables import *
from database.muscleEnum import Muscles as m


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# ---------------- TESTS ---------------- #

def test_create_tables():
    # Ensure tables exist
    populate_muscle_table()
    tables = Base.metadata.tables
    assert "muscles" in tables
    assert "exercise" in tables
    assert "workout" in tables


def test_insert_muscles():
    # Run create_tables() which inserts enum muscles
    populate_muscle_table()
    with SessionLocal() as session:
        rows = session.execute(select(MusclesTable.name)).scalars().all()
        assert set(rows) == {m.value for m in m}


def test_add_exercise():
    populate_muscle_table()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    with SessionLocal() as session:
        exercise = session.query(Exercise).filter_by(name="Bench Press").first()
        assert exercise is not None


def test_add_exercise_unique_constraint():
    populate_muscle_table()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])  # Should not duplicate
    with SessionLocal() as session:
        exercises = session.query(Exercise).filter(Exercise.name == "Bench Press").all()
        assert len(exercises) == 1

def test_add_workout():
    populate_muscle_table()
    exercise = add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    workout_id = add_workout("Push Day", ["Bench Press"], [4])

    with SessionLocal() as session:
        workout = session.query(WorkoutExercise.sets).filter_by(workout_id=workout_id, exercise_id=exercise.id).first()
        #workouts = session.execute(select(Workout).where(Workout.id == workout_id))
        assert workout is not None
        assert workout.sets == (4,)


def test_update_workout():
    populate_muscle_table()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    exercise_id = add_exercise("Dips", [m.TRICEPS], [m.CHEST])
    checked_id = add_workout("Push Day", ["Bench Press"], [4])
    update_workout(checked_id, ["Dips"], [5])

    with SessionLocal() as session:
        sets = session.execute(select(WorkoutExercise.sets).where(Workout.id == checked_id)).first()
        exercise = get_exercises(checked_id)
        assert sets == (5,)
        assert exercise.__contains__("Dips")


def test_workout_list_to_muscles():
    populate_muscle_table()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    add_exercise("Dips", [m.TRICEPS], [m.CHEST])
    add_workout("Push Day", ["Bench Press", "Dips"], [4, 6])

    with SessionLocal() as session:
        workout_id = session.execute(select(Workout.id)).scalar_one()

        result = workout_list_to_muscles([workout_id])

        # Bench Press: chest +4, triceps +2
        # Dips: triceps +6, chest +3
        assert result[m.CHEST.value] == 7
        assert result[m.TRICEPS.value] == 8


def test_get_all_workouts():
    populate_muscle_table()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    add_workout("Push Day", ["Bench Press"], [4])

    workouts = get_all_workouts()
    assert len(workouts) == 1
    assert workouts[0]["name"] == "Push Day"


def test_get_exercises():
    populate_muscle_table()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    add_workout("Push Day", ["Bench Press"], [4])
    with SessionLocal() as session:
        workout_id = session.execute(select(Workout.id)).scalar_one()
        exercises = get_exercises(workout_id)
        assert len(exercises) == 1
        assert exercises[0][0] == "Bench Press"
