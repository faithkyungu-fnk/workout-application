from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from server.models import db, Workout, Exercise, WorkoutExercise
from server.schemas import (
    WorkoutSchema,
    WorkoutSummarySchema,
    ExerciseSchema,
    ExerciseDetailSchema,
    WorkoutExerciseSchema,
)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    workout_schema = WorkoutSchema()
    workouts_schema = WorkoutSchema(many=True)
    workout_input_schema = WorkoutSummarySchema()

    exercise_schema = ExerciseSchema()
    exercises_schema = ExerciseSchema(many=True)
    exercise_detail_schema = ExerciseDetailSchema()

    workout_exercise_schema = WorkoutExerciseSchema()

    @app.route('/')
    def index():
        return jsonify({"message": "Welcome to the Fitness App!"}), 200

    # 1. Get all workouts.
    @app.route('/workouts', methods=['GET'])
    def get_workouts():
        workouts = Workout.query.all()
        return jsonify(workouts_schema.dump(workouts)), 200

    # 2. Get one workout and its exercises.
    @app.route('/workouts/<int:workout_id>', methods=['GET'])
    def get_workout(workout_id):
        workout = db.session.get(Workout, workout_id)

        if workout is None:
            return jsonify({"error": "Workout not found"}), 404

        return jsonify(workout_schema.dump(workout)), 200

    # 3. Create a workout.
    @app.route('/workouts', methods=['POST'])
    def create_workout():
        try:
            data = workout_input_schema.load(
                request.get_json(silent=True) or {}
            )
            workout = Workout(**data)

            db.session.add(workout)
            db.session.commit()

            return jsonify(workout_schema.dump(workout)), 201

        except ValidationError as error:
            db.session.rollback()
            return jsonify({"errors": error.messages}), 400
        except ValueError as error:
            db.session.rollback()
            return jsonify({"error": str(error)}), 400
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Could not create workout"}), 400

    # 4. Delete a workout.
    @app.route('/workouts/<int:workout_id>', methods=['DELETE'])
    def delete_workout(workout_id):
        workout = db.session.get(Workout, workout_id)

        if workout is None:
            return jsonify({"error": "Workout not found"}), 404

        db.session.delete(workout)
        db.session.commit()

        return jsonify({"message": "Workout deleted successfully"}), 200

    # 5. Get all exercises.
    @app.route('/exercises', methods=['GET'])
    def get_exercises():
        exercises = Exercise.query.all()
        return jsonify(exercises_schema.dump(exercises)), 200

    # 6. Get one exercise and its workouts.
    @app.route('/exercises/<int:exercise_id>', methods=['GET'])
    def get_exercise(exercise_id):
        exercise = db.session.get(Exercise, exercise_id)

        if exercise is None:
            return jsonify({"error": "Exercise not found"}), 404

        return jsonify(exercise_detail_schema.dump(exercise)), 200

    # 7. Create an exercise.
    @app.route('/exercises', methods=['POST'])
    def create_exercise():
        try:
            data = exercise_schema.load(
                request.get_json(silent=True) or {}
            )
            exercise = Exercise(**data)

            db.session.add(exercise)
            db.session.commit()

            return jsonify(exercise_schema.dump(exercise)), 201

        except ValidationError as error:
            db.session.rollback()
            return jsonify({"errors": error.messages}), 400
        except ValueError as error:
            db.session.rollback()
            return jsonify({"error": str(error)}), 400
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "error": "Could not create exercise. The name may already exist."
            }), 409

    # 8. Delete an exercise.
    @app.route('/exercises/<int:exercise_id>', methods=['DELETE'])
    def delete_exercise(exercise_id):
        exercise = db.session.get(Exercise, exercise_id)

        if exercise is None:
            return jsonify({"error": "Exercise not found"}), 404

        db.session.delete(exercise)
        db.session.commit()

        return jsonify({"message": "Exercise deleted successfully"}), 200

    # 9. Add an exercise to a workout.
    @app.route(
        '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
        methods=['POST']
    )
    def add_exercise_to_workout(workout_id, exercise_id):
        workout = db.session.get(Workout, workout_id)
        exercise = db.session.get(Exercise, exercise_id)

        if workout is None:
            return jsonify({"error": "Workout not found"}), 404

        if exercise is None:
            return jsonify({"error": "Exercise not found"}), 404

        try:
            data = workout_exercise_schema.load(
                request.get_json(silent=True) or {}
            )

            workout_exercise = WorkoutExercise(
                workout_id=workout_id,
                exercise_id=exercise_id,
                **data
            )

            db.session.add(workout_exercise)
            db.session.commit()

            return jsonify(
                workout_exercise_schema.dump(workout_exercise)
            ), 201

        except ValidationError as error:
            db.session.rollback()
            return jsonify({"errors": error.messages}), 400
        except ValueError as error:
            db.session.rollback()
            return jsonify({"error": str(error)}), 400
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "error": "Could not add exercise. It may already be in this workout."
            }), 409

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)

