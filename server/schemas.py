from marshmallow import Schema, fields, validate


class ExerciseSummarySchema(Schema):
    """Lightweight Exercise view, used when nesting inside a WorkoutExercise."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()


class WorkoutSummarySchema(Schema):
    """Lightweight Workout view, used when nesting inside an Exercise."""
    id = fields.Int(dump_only=True)
    date = fields.Date()
    duration_minutes = fields.Int()


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(allow_none=True, validate=validate.Range(min=0, max=1000))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=0, max=100))
    duration_seconds = fields.Int(allow_none=True, validate=validate.Range(min=0, max=36000))
    exercise = fields.Nested(ExerciseSummarySchema, dump_only=True)


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(
        required=True,
        validate=validate.OneOf(['cardio', 'strength', 'flexibility', 'balance'])
    )
    equipment_needed = fields.Bool(required=True)
    workouts = fields.List(fields.Nested(WorkoutSummarySchema), dump_only=True)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=600))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()