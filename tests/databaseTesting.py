import pytest
from database.SQLTables import *
from database.muscleEnum import Muscles as m


# ---------------- FIXTURES ---------------- #

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def conn(engine):
    with engine.begin() as connection:
        yield connection


# ---------------- TESTS ---------------- #

def test_create_tables(conn):
    # Ensure tables exist
    tables = Base.metadata.tables
    assert "muscles" in tables
    assert "exercise" in tables
    assert "workout" in tables


def test_insert_muscles():
    with SessionLocal() as session:
        # Run create_tables() which inserts enum muscles
        create_tables()

        rows = session.execute(select(MusclesTable.name)).scalars().all()
        assert set(rows) == {m.value for m in m}


def test_add_exercise():
    with SessionLocal() as session:
        create_tables()

        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
        # Exercise should exist
        exercise = session.execute(
            select(Exercise).where(Exercise.name == "Bench Press")
        ).scalar()

        assert exercise.name == "Bench Press"

def test_create_tables():
    assert create_tables() is not None

def test_add_exercises():
    conn = add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    assert conn.execute(select(Exercise.name).where(Exercise.name == "Bench Press")).scalar() is not None

        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])  # Should not duplicate

        exercises = session.execute(select(Exercise).where(Exercise.name == "Bench Press")).all()
        assert len(exercises) == 1


def test_add_workout():
    with SessionLocal() as session:
        create_tables()
        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
        add_workout("Push Day", ["Bench Press"], [4])

        workouts = session.execute(select(Workout)).where(Workout.name == "Push Day")
        workout_id = workouts.scalar().id
        assert len(workouts) >= 1

        workout_exercises = session.execute(select(WorkoutExercise)).where(workout_id == WorkoutExercise.id).scalars().all()
        assert len(workout_exercises) >= 1
        assert workout_exercises[0].sets == 4


def test_update_workout():
    with SessionLocal() as session:
        create_tables()
        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
        add_exercise("Dips", [m.TRICEPS], [m.CHEST])

        add_workout("Push Day", ["Bench Press"], [4])

        workout_id = session.execute(select(Workout.id)).scalar_one()

        update_workout(workout_id, ["Dips"], [5])

        # Bench Press should be removed, Dips added
        rows = session.execute(select(WorkoutExercise)).all()
        assert len(rows) == 1
        assert rows[0].sets == 5


def test_workout_list_to_muscles():
    with SessionLocal() as session:
        create_tables()

        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
        add_exercise("Dips", [m.TRICEPS], [m.CHEST])

        add_workout("Push Day", ["Bench Press", "Dips"], [4, 6])

        workout_id = session.execute(select(Workout.id)).scalar_one()

        result = workout_list_to_muscles([workout_id])

        # Bench Press: chest +4, triceps +2
        # Dips: triceps +6, chest +3
        assert result[m.CHEST.value] == 7
        assert result[m.TRICEPS.value] == 8


def test_get_all_workouts():
    create_tables()
    add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
    add_workout("Push Day", ["Bench Press"], [4])

    workouts = get_all_workouts()
    assert len(workouts) == 1
    assert workouts[0]["name"] == "Push Day"


def test_get_exercises():
    with SessionLocal() as session:
        create_tables()
        add_exercise("Bench Press", [m.CHEST], [m.TRICEPS])
        add_workout("Push Day", ["Bench Press"], [4])

        workout_id = session.execute(select(Workout.id)).scalar_one()

        exercises = get_exercises(workout_id)
        assert len(exercises) == 1
        assert exercises[0][0] == "Bench Press"
