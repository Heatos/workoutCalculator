from django.core.checks import database

from database.SQLTables import *
from database.muscleEnum import Muscles

if __name__ == '__main__':
    create_tables()
    add_exercise("Bench Press", [Muscles.CHEST, Muscles.SHOULDERS, Muscles.TRICEPS], [])
    add_exercise("Shoulder Press", [Muscles.SHOULDERS], [Muscles.UPPERBACK])
    add_exercise("Cable Fly", [Muscles.CHEST], [Muscles.TRICEPS])
    add_exercise("Cable Lateral Raise", [Muscles.SHOULDERS], [])
    add_exercise("Triceps Extension", [Muscles.TRICEPS], [])
    add_exercise("Captain's Chair Leg Raise", [Muscles.ABS], [])
    add_workout("Push Day", ["Bench Press", "Shoulder Press", "Cable Fly", "Cable Lateral Raise", "Triceps Extension",
                             "Captain's Chair Leg Raise"],
                [3, 3, 3, 3, 4, 4])
    add_workout("Push Day", ["Bench Press", "Shoulder Press", "Cable Fly", "Cable Lateral Raise", "Triceps Extension"],
                [3, 3, 3, 3, 4])
    print(workout_list_to_muscles(get_workout_ids(get_all_workouts())))


def test_get_all_workouts():
    create_tables()
    add_exercise("Bench Press", [Muscles.CHEST, Muscles.SHOULDERS, Muscles.TRICEPS], [])
    add_exercise("Shoulder Press", [Muscles.SHOULDERS], [Muscles.UPPERBACK])
    add_exercise("Cable Fly", [Muscles.CHEST], [Muscles.TRICEPS])
    add_exercise("Cable Lateral Raise", [Muscles.SHOULDERS], [])
    add_exercise("Triceps Extension", [Muscles.TRICEPS], [])
    add_exercise("Captain's Chair Leg Raise", [Muscles.ABS], [])
    add_workout("Push Day", ["Bench Press", "Shoulder Press", "Cable Fly", "Cable Lateral Raise", "Triceps Extension", "Captain's Chair Leg Raise"],
                [3, 3, 3, 3, 4, 4])
    add_workout("Push Day", ["Bench Press", "Shoulder Press", "Cable Fly", "Cable Lateral Raise", "Triceps Extension"],
                [3, 3, 3, 3, 4])

def test_add_workout():
    create_tables()
    add_exercise("Bench Press", [Muscles.CHEST, Muscles.SHOULDERS, Muscles.TRICEPS], [])
    add_exercise("Shoulder Press", [Muscles.SHOULDERS], [Muscles.UPPERBACK])
    add_exercise("Cable Fly", [Muscles.CHEST], [Muscles.TRICEPS])
    add_exercise("Cable Lateral Raise", [Muscles.SHOULDERS], [])
    add_exercise("Triceps Extension", [Muscles.TRICEPS], [])
    add_exercise("Captain's Chair Leg Raise", [Muscles.ABS], [])
    add_workout("Push Day", ["Bench Press", "Shoulder Press", "Cable Fly", "Cable Lateral Raise", "Triceps Extension", "Captain's Chair Leg Raise"],
                [3, 3, 3, 3, 4, 4])

def test_add_exercise():
    create_tables()
    add_exercise("Bench Press", [Muscles.CHEST, Muscles.SHOULDERS, Muscles.TRICEPS], [])

def test_create_tables():
    create_tables()