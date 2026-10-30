import pytest
from datetime import date
from server.app import create_app
from server.models import db, Workout, Exercise, WorkoutExercise

@pytest.fixture
def app(tmp_path):
    database_path = tmp_path / "test_fitness.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
    })
    with app.app_context():
        db.create_all()

        exercise1 = Exercise(
            name="Push-ups",
            category="Chest",
            equipment_needed=False,
        )
        exercise2 = Exercise(
            name="Squats",
            category="Legs",
            equipment_needed=False,
        )
        workout = Workout(
            date=date(2026, 10, 25),
            duration_minutes=45,
            notes="Test workout",
        )

        db.session.add_all([exercise1, exercise2, workout])
        db.session.commit()

        association = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=exercise1.id,
            reps=10,
            sets=3,
        )
        db.session.add(association)
        db.session.commit()

    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200

def test_get_all_workouts(client):
    response = client.get("/workouts")
    assert response.status_code == 200
    assert len(response.json) == 1

def test_get_workout_with_exercises(client):
    response = client.get("/workouts/1")
    assert response.status_code == 200
    assert len(response.json["workout_exercises"]) == 1

def test_get_missing_workout(client):
    response = client.get("/workouts/999")
    assert response.status_code == 404

def test_create_workout(client):
    response = client.post(
        "/workouts",
        json={
            "date": "2026-10-26",
            "duration_minutes": 30,
            "notes": "New workout",
        },
    )
    assert response.status_code == 201
    assert response.json["duration_minutes"] == 30

def test_reject_invalid_workout(client):
    response = client.post(
        "/workouts",
        json={
            "date": "2026-10-26",
            "duration_minutes": 0,
        },
    )
    assert response.status_code == 400

def test_delete_workout(client):
    response = client.delete("/workouts/1")
    assert response.status_code == 200
    assert client.get("/workouts/1").status_code == 404

def test_get_all_exercises(client):
    response = client.get("/exercises")
    assert response.status_code == 200
    assert len(response.json) == 2

def test_get_exercise_with_workouts(client):
    response = client.get("/exercises/1")
    assert response.status_code == 200
    assert len(response.json["workout_exercises"]) == 1

def test_get_missing_exercise(client):
    response = client.get("/exercises/999")
    assert response.status_code == 404

def test_create_exercise(client):
    response = client.post(
        "/exercises",
        json={
            "name": "Lunges",
            "category": "Legs",
            "equipment_needed": False,
        },
    )
    assert response.status_code == 201
    assert response.json["name"] == "Lunges"

def test_reject_empty_exercise_name(client):
    response = client.post(
        "/exercises",
        json={
            "name": "",
            "category": "Legs",
        },
    )
    assert response.status_code == 400

def test_delete_exercise(client):
    response = client.delete("/exercises/2")
    assert response.status_code == 200
    assert client.get("/exercises/2").status_code == 404

def test_add_exercise_to_workout(client):
    response = client.post(
        "/workouts/1/exercises/2/workout_exercises",
        json={"reps": 12, "sets": 3},
    )
    assert response.status_code == 201
    assert response.json["reps"] == 12

def test_reject_association_without_training_details(client):
    response = client.post(
        "/workouts/1/exercises/2/workout_exercises",
        json={},
    )
    assert response.status_code == 400

def test_reject_duplicate_association(client):
    response = client.post(
        "/workouts/1/exercises/1/workout_exercises",
        json={"reps": 8, "sets": 2},
    )
    assert response.status_code == 409
