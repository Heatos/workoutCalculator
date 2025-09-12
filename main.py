from SQL import *
from muscleEnum import Muscles

if __name__ == '__main__':
    add_exercise("Bench Press", [Muscles.CHEST, Muscles.SHOULDERS, Muscles.TRICEPS], [])
    add_exercise("Seated Dumbbell Shoulder Press", [Muscles.SHOULDERS], [Muscles.TRAPEZIUS])
    add_exercise("Cable Fly", [Muscles.CHEST], [Muscles.SHOULDERS, Muscles.TRICEPS])
    add_exercise("Triceps Extension", [Muscles.TRICEPS], [])
    add_exercise("Cable Later Raise", [Muscles.SHOULDERS], [])
    add_exercise("Captain's Chair Leg Raise", [Muscles.ABS], [])

    add_workout("PushDay", ["Bench Press", "Seated Dumbbell Shoulder Press", "Cable Fly",
                             "Triceps Extension", "Cable Later Raise", "Captain's Chair Leg Raise"], [3, 3, 3, 4, 3, 4])