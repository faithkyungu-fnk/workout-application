from datetime import date
from server.app import app
from server.models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    db.create_all()

    # Create some sample exercises
    exercise1 = Exercise(name="Push-ups", category="Chest", equipment_needed=False)
    exercise2 = Exercise(name="Squats", category="Legs", equipment_needed=False)
    exercise3 = Exercise(name="Bench Press", category="Chest", equipment_needed=True)

    db.session.add_all([exercise1, exercise2, exercise3])
    db.session.commit()

    # Create a sample workout
    workout = Workout(date=date.today(), duration_minutes=60, notes="Great workout!")
    db.session.add(workout)
    db.session.commit()

    # Create sample workout exercises
    workout_exercise1 = WorkoutExercise(workout_id=workout.id, exercise_id=exercise1.id, reps=10, sets=3)
    workout_exercise2 = WorkoutExercise(workout_id=workout.id, exercise_id=exercise2.id, reps=15, sets=3)
    workout_exercise3 = WorkoutExercise(workout_id=workout.id, exercise_id=exercise3.id, duration_seconds=60)

    db.session.add_all([workout_exercise1, workout_exercise2, workout_exercise3])
    db.session.commit()

    if __name__ == '__main__':
        print("Database seeded successfully.")
        