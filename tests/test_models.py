from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise


class TestExercise:
    def test_creates_valid_exercise(self, app):
        with app.app_context():
            exercise = Exercise(name='Deadlift', category='strength', equipment_needed=True)
            db.session.add(exercise)
            db.session.commit()
            assert exercise.id is not None

    def test_model_validation_rejects_empty_name(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                Exercise(name='   ', category='strength', equipment_needed=False)

    def test_model_validation_rejects_invalid_category(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                Exercise(name='Mystery Move', category='not-a-real-category', equipment_needed=False)

    def test_table_constraint_blocks_bad_category_on_raw_insert(self, app):
        # Bypasses the Python-level @validates check to prove the database
        # itself (the CheckConstraint) also refuses bad data.
        with app.app_context():
            with pytest.raises(IntegrityError):
                db.session.execute(text(
                    "INSERT INTO exercises (name, category, equipment_needed) "
                    "VALUES ('Sneaky', 'not-a-real-category', 0)"
                ))
                db.session.commit()
            db.session.rollback()

    def test_table_constraint_blocks_duplicate_name(self, app):
        with app.app_context():
            db.session.add(Exercise(name='Burpee', category='cardio', equipment_needed=False))
            db.session.commit()

            db.session.add(Exercise(name='Burpee', category='cardio', equipment_needed=False))
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()


class TestWorkout:
    def test_creates_valid_workout(self, app):
        with app.app_context():
            workout = Workout(date=date(2026, 7, 20), duration_minutes=30, notes='Legs day')
            db.session.add(workout)
            db.session.commit()
            assert workout.id is not None

    def test_model_validation_rejects_zero_duration(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                Workout(date=date(2026, 7, 20), duration_minutes=0, notes='bad')

    def test_model_validation_rejects_negative_duration(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                Workout(date=date(2026, 7, 20), duration_minutes=-10, notes='bad')

    def test_table_constraint_blocks_bad_duration_on_raw_insert(self, app):
        with app.app_context():
            with pytest.raises(IntegrityError):
                db.session.execute(text(
                    "INSERT INTO workouts (date, duration_minutes) VALUES ('2026-07-20', -5)"
                ))
                db.session.commit()
            db.session.rollback()


class TestWorkoutExercise:
    def test_model_validation_rejects_negative_reps(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                WorkoutExercise(workout_id=1, exercise_id=1, reps=-5, sets=3)

    def test_model_validation_rejects_negative_sets(self, app):
        with app.app_context():
            with pytest.raises(ValueError):
                WorkoutExercise(workout_id=1, exercise_id=1, reps=5, sets=-1)

    def test_table_constraint_blocks_negative_reps_on_raw_insert(self, app):
        with app.app_context():
            exercise = Exercise(name='Row', category='strength', equipment_needed=True)
            workout = Workout(date=date(2026, 7, 20), duration_minutes=30, notes='Back day')
            db.session.add_all([exercise, workout])
            db.session.commit()

            with pytest.raises(IntegrityError):
                db.session.execute(text(
                    "INSERT INTO workout_exercises (workout_id, exercise_id, reps, sets) "
                    f"VALUES ({workout.id}, {exercise.id}, -5, 3)"
                ))
                db.session.commit()
            db.session.rollback()

    def test_relationships_through_association_proxy(self, app):
        with app.app_context():
            exercise = Exercise(name='Lunge', category='strength', equipment_needed=False)
            workout = Workout(date=date(2026, 7, 22), duration_minutes=40, notes='Legs')
            db.session.add_all([exercise, workout])
            db.session.commit()

            workout_exercise = WorkoutExercise(
                workout_id=workout.id, exercise_id=exercise.id, reps=10, sets=3
            )
            db.session.add(workout_exercise)
            db.session.commit()

            assert exercise in workout.exercises
            assert workout in exercise.workouts

    def test_cascade_delete_removes_workout_exercises(self, app):
        with app.app_context():
            exercise = Exercise(name='Curl', category='strength', equipment_needed=True)
            workout = Workout(date=date(2026, 7, 22), duration_minutes=25, notes='Arms')
            db.session.add_all([exercise, workout])
            db.session.commit()

            db.session.add(WorkoutExercise(workout_id=workout.id, exercise_id=exercise.id, reps=8, sets=3))
            db.session.commit()

            db.session.delete(workout)
            db.session.commit()

            assert WorkoutExercise.query.count() == 0
