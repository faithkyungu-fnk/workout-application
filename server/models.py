from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()


# Stores the exercises available in the application.
class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Connects an exercise to its workout association records.
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan'
    )

    # Lets us access all workouts containing this exercise.
    workouts = db.relationship(
        'Workout',
        secondary='workout_exercises',
        back_populates='exercises',
        viewonly=True
    )

    @validates('name', 'category')
    def validate_text(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} cannot be empty.")
        return value.strip()

    def __repr__(self):
        return f"<Exercise {self.name}>"


# Stores information about each workout session.
class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (
        CheckConstraint(
            'duration_minutes > 0',
            name='check_workout_duration_positive'
        ),
    )

    # Connects a workout to its exercise association records.
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan'
    )

    # Lets us access all exercises included in this workout.
    exercises = db.relationship(
        'Exercise',
        secondary='workout_exercises',
        back_populates='workouts',
        viewonly=True
    )

    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("Workout duration must be a positive integer.")
        return value

    def __repr__(self):
        return f"<Workout {self.id}>"


# Connects workouts and exercises and stores training details.
class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey('workouts.id'),
        nullable=False
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey('exercises.id'),
        nullable=False
    )

    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            'workout_id',
            'exercise_id',
            name='unique_workout_exercise'
        ),
        CheckConstraint('reps IS NULL OR reps > 0', name='check_reps_positive'),
        CheckConstraint('sets IS NULL OR sets > 0', name='check_sets_positive'),
        CheckConstraint(
            'duration_seconds IS NULL OR duration_seconds > 0',
            name='check_duration_positive'
        ),
        CheckConstraint(
            '(reps IS NOT NULL AND sets IS NOT NULL) OR duration_seconds IS NOT NULL',
            name='check_exercise_training_details'
        ),
    )

    # Connects this record to its workout and exercise.
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    @validates('reps', 'sets', 'duration_seconds')
    def validate_training_details(self, key, value):
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{key} must be a positive integer or None.")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout={self.workout_id} "
            f"exercise={self.exercise_id}>"
        )

