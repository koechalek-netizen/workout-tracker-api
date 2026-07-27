import os

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema, exercises_schema,
    workout_schema, workouts_schema,
    workout_exercise_schema
)

app = Flask(__name__)
# DATABASE_URL is overridden by the test suite so tests run against their
# own throwaway database instead of app.db.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)


# ---------------- Workouts ----------------

@app.get('/workouts')
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.get('/workouts/<int:id>')
def get_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return jsonify({'error': 'Workout not found'}), 404
    return jsonify(workout_schema.dump(workout)), 200


@app.post('/workouts')
def create_workout():
    data = request.get_json()

    try:
        validated = workout_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    try:
        workout = Workout(
            date=validated['date'],
            duration_minutes=validated['duration_minutes'],
            notes=validated.get('notes')
        )
        db.session.add(workout)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'errors': [str(err)]}), 400

    return jsonify(workout_schema.dump(workout)), 201


@app.delete('/workouts/<int:id>')
def delete_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return jsonify({'error': 'Workout not found'}), 404

    db.session.delete(workout)  # cascade also deletes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------------- Exercises ----------------

@app.get('/exercises')
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.get('/exercises/<int:id>')
def get_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404
    return jsonify(exercise_schema.dump(exercise)), 200


@app.post('/exercises')
def create_exercise():
    data = request.get_json()

    try:
        validated = exercise_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    try:
        exercise = Exercise(
            name=validated['name'],
            category=validated['category'],
            equipment_needed=validated['equipment_needed']
        )
        db.session.add(exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'errors': [str(err)]}), 400

    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete('/exercises/<int:id>')
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return jsonify({'error': 'Exercise not found'}), 404

    db.session.delete(exercise)  # cascade also deletes its WorkoutExercises
    db.session.commit()
    return make_response('', 204)


# ---------------- WorkoutExercises ----------------

@app.post('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises')
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)

    if not workout or not exercise:
        return jsonify({'error': 'Workout or Exercise not found'}), 404

    data = request.get_json() or {}
    data['workout_id'] = workout_id
    data['exercise_id'] = exercise_id

    try:
        validated = workout_exercise_schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=validated.get('reps'),
            sets=validated.get('sets'),
            duration_seconds=validated.get('duration_seconds')
        )
        db.session.add(workout_exercise)
        db.session.commit()
    except ValueError as err:
        db.session.rollback()
        return jsonify({'errors': [str(err)]}), 400

    return jsonify(workout_schema.dump(workout)), 201


if __name__ == '__main__':
    app.run(port=5555, debug=True)