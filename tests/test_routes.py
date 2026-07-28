from datetime import date

from models import db, Exercise, Workout


def _create_exercise(app, name='Push Up', category='strength', equipment_needed=False):
    with app.app_context():
        exercise = Exercise(name=name, category=category, equipment_needed=equipment_needed)
        db.session.add(exercise)
        db.session.commit()
        return exercise.id


def _create_workout(app, duration_minutes=30, notes='Test workout'):
    with app.app_context():
        workout = Workout(date=date(2026, 7, 20), duration_minutes=duration_minutes, notes=notes)
        db.session.add(workout)
        db.session.commit()
        return workout.id


class TestWorkoutRoutes:
    def test_get_workouts_empty(self, client):
        response = client.get('/workouts')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_get_workouts_returns_created_workout(self, client, app):
        _create_workout(app, notes='Push day')
        response = client.get('/workouts')
        assert response.status_code == 200
        assert len(response.get_json()) == 1

    def test_create_workout_success(self, client):
        response = client.post('/workouts', json={
            'date': '2026-07-20', 'duration_minutes': 45, 'notes': 'Push day'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['duration_minutes'] == 45
        assert data['notes'] == 'Push day'

    def test_create_workout_missing_required_field(self, client):
        response = client.post('/workouts', json={'notes': 'no date or duration'})
        assert response.status_code == 400
        assert 'errors' in response.get_json()

    def test_create_workout_invalid_duration(self, client):
        response = client.post('/workouts', json={
            'date': '2026-07-20', 'duration_minutes': -5, 'notes': 'bad'
        })
        assert response.status_code == 400

    def test_get_single_workout_not_found(self, client):
        response = client.get('/workouts/999')
        assert response.status_code == 404

    def test_get_single_workout_found(self, client, app):
        workout_id = _create_workout(app)
        response = client.get(f'/workouts/{workout_id}')
        assert response.status_code == 200
        assert response.get_json()['id'] == workout_id

    def test_delete_workout(self, client, app):
        workout_id = _create_workout(app)
        response = client.delete(f'/workouts/{workout_id}')
        assert response.status_code == 204
        assert client.get(f'/workouts/{workout_id}').status_code == 404

    def test_delete_workout_not_found(self, client):
        response = client.delete('/workouts/999')
        assert response.status_code == 404


class TestExerciseRoutes:
    def test_get_exercises_empty(self, client):
        response = client.get('/exercises')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_exercise_success(self, client):
        response = client.post('/exercises', json={
            'name': 'Squat', 'category': 'strength', 'equipment_needed': False
        })
        assert response.status_code == 201
        assert response.get_json()['name'] == 'Squat'

    def test_create_exercise_invalid_category(self, client):
        response = client.post('/exercises', json={
            'name': 'Mystery', 'category': 'nonsense', 'equipment_needed': False
        })
        assert response.status_code == 400
        assert 'category' in response.get_json()['errors']

    def test_create_exercise_missing_name(self, client):
        response = client.post('/exercises', json={
            'category': 'strength', 'equipment_needed': False
        })
        assert response.status_code == 400

    def test_get_exercise_not_found(self, client):
        response = client.get('/exercises/999')
        assert response.status_code == 404

    def test_get_exercise_found(self, client, app):
        exercise_id = _create_exercise(app)
        response = client.get(f'/exercises/{exercise_id}')
        assert response.status_code == 200
        assert response.get_json()['id'] == exercise_id

    def test_delete_exercise(self, client, app):
        exercise_id = _create_exercise(app)
        response = client.delete(f'/exercises/{exercise_id}')
        assert response.status_code == 204
        assert client.get(f'/exercises/{exercise_id}').status_code == 404

    def test_delete_exercise_not_found(self, client):
        response = client.delete('/exercises/999')
        assert response.status_code == 404


class TestWorkoutExerciseRoutes:
    def test_add_exercise_to_workout_success(self, client, app):
        workout_id = _create_workout(app)
        exercise_id = _create_exercise(app)

        response = client.post(
            f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises',
            json={'reps': 12, 'sets': 3}
        )
        assert response.status_code == 201
        data = response.get_json()
        linked_exercise_ids = [we['exercise_id'] for we in data['workout_exercises']]
        assert exercise_id in linked_exercise_ids

    def test_add_exercise_to_workout_invalid_reps(self, client, app):
        workout_id = _create_workout(app)
        exercise_id = _create_exercise(app)

        response = client.post(
            f'/workouts/{workout_id}/exercises/{exercise_id}/workout_exercises',
            json={'reps': -5, 'sets': 3}
        )
        assert response.status_code == 400

    def test_add_exercise_to_missing_workout(self, client, app):
        exercise_id = _create_exercise(app)
        response = client.post(
            f'/workouts/999/exercises/{exercise_id}/workout_exercises',
            json={'reps': 5, 'sets': 3}
        )
        assert response.status_code == 404

    def test_add_missing_exercise_to_workout(self, client, app):
        workout_id = _create_workout(app)
        response = client.post(
            f'/workouts/{workout_id}/exercises/999/workout_exercises',
            json={'reps': 5, 'sets': 3}
        )
        assert response.status_code == 404
