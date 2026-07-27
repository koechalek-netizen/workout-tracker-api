#!/usr/bin/env python3
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print('Clearing existing data...')
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print('Seeding exercises...')
    push_up = Exercise(name='Push Up', category='strength', equipment_needed=False)
    squat = Exercise(name='Squat', category='strength', equipment_needed=False)
    running = Exercise(name='Running', category='cardio', equipment_needed=False)
    yoga_flow = Exercise(name='Yoga Flow', category='flexibility', equipment_needed=True)

    db.session.add_all([push_up, squat, running, yoga_flow])
    db.session.commit()

    print('Seeding workouts...')
    morning_workout = Workout(
        date=date(2026, 7, 20),
        duration_minutes=45,
        notes='Morning strength session'
    )
    evening_run = Workout(
        date=date(2026, 7, 21),
        duration_minutes=30,
        notes='Evening cardio run'
    )

    db.session.add_all([morning_workout, evening_run])
    db.session.commit()

    print('Linking exercises to workouts...')
    we1 = WorkoutExercise(workout_id=morning_workout.id, exercise_id=push_up.id, reps=15, sets=3)
    we2 = WorkoutExercise(workout_id=morning_workout.id, exercise_id=squat.id, reps=12, sets=4)
    we3 = WorkoutExercise(workout_id=evening_run.id, exercise_id=running.id, duration_seconds=1800)

    db.session.add_all([we1, we2, we3])
    db.session.commit()

    print('Done seeding!')