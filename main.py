from SQLTables import *
from muscleEnum import Muscles

if __name__ == '__main__':
    create_tables()
    add_exercise("Bench Press", [Muscles.CHEST, Muscles.SHOULDERS, Muscles.TRICEPS], [])
    add_exercise("Shoulder Press", [Muscles.SHOULDERS], [Muscles.UPPERBACK])
    add_exercise("Cable Fly", [Muscles.CHEST], [Muscles.TRICEPS])
    add_exercise("Cable Lateral Raise", [Muscles.SHOULDERS], [])
    add_exercise("Triceps Extension", [Muscles.TRICEPS], [])
    add_exercise("Captain's Chair Leg Raise", [Muscles.ABS], [])
    add_workout("Push Day", ["Bench Press", "Shoulder Press", "Cable Fly", "Cable Lateral Raise", "Triceps Extension", "Captain's Chair Leg Raise"],
                [3, 3, 3, 3, 4, 4])