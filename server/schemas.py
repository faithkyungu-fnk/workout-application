
from marshmallow import Schema, fields, validate, validates_schema, ValidationError


# Validates the basic information for an exercise.
class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    equipment_needed = fields.Bool(load_default=False)


# Provides basic workout details when another object refers to a workout.
class WorkoutSummarySchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(allow_none=True, load_default=None)


# Validates the details connecting an exercise to a workout.
class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=1))

    # Includes the related exercise and workout in API responses.
    exercise = fields.Nested(ExerciseSchema, dump_only=True)
    workout = fields.Nested(WorkoutSummarySchema, dump_only=True)

    @validates_schema
    def validate_training_details(self, data, **kwargs):
        reps = data.get('reps')
        sets = data.get('sets')
        duration_seconds = data.get('duration_seconds')

        if not ((reps is not None and sets is not None) or duration_seconds is not None):
            raise ValidationError(
                'Provide both reps and sets, or provide duration_seconds.'
            )


# Serializes a workout with its associated exercises.
class WorkoutSchema(WorkoutSummarySchema):
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True
    )


# Serializes an exercise with its associated workouts.
class ExerciseDetailSchema(ExerciseSchema):
    workout_exercises = fields.Nested(
        WorkoutExerciseSchema, many=True, dump_only=True
    )

