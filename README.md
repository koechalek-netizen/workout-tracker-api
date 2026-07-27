# Workout Tracker API

A Flask + SQLAlchemy + Marshmallow backend API for a workout tracking application used by personal trainers. Trainers can create reusable exercises, build workouts, and attach exercises to a workout with reps, sets, or duration.

## Project Description

The API manages three resources:

- **Exercise** — a reusable movement (e.g. "Push Up"), with a `category` and whether `equipment_needed`.
- **Workout** — a logged session with a `date`, `duration_minutes`, and `notes`.
- **WorkoutExercise** — the join between a Workout and an Exercise, tracking `reps`, `sets`, and `duration_seconds` for that pairing.

A Workout has many Exercises through WorkoutExercises, and an Exercise has many Workouts through WorkoutExercises.

## Installation

1. Clone the repo and move into the `server/` directory:
   ```bash
   git clone <your-repo-url>
   cd workout-tracker-api
   ```
2. Install dependencies:
   ```bash
   pipenv install
   pipenv shell
   ```
3. From inside `server/`, set up the database:
   ```bash
   cd server
   export FLASK_APP=app.py
   flask db init
   flask db migrate -m "initial migration"
   flask db upgrade head
   ```
4. Seed the database with sample data:
   ```bash
   python seed.py
   ```

## Running the App

From the `server/` directory:

```bash
python app.py
```

The API runs at `http://localhost:5555`.

## Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Get a single workout, including its exercises with reps/sets/duration |
| POST | `/workouts` | Create a workout. Body: `{"date", "duration_minutes", "notes"}` |
| DELETE | `/workouts/<id>` | Delete a workout and its associated WorkoutExercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Get a single exercise, including workouts it's used in |
| POST | `/exercises` | Create an exercise. Body: `{"name", "category", "equipment_needed"}` |
| DELETE | `/exercises/<id>` | Delete an exercise and its associated WorkoutExercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Attach an exercise to a workout. Body: `{"reps", "sets", "duration_seconds"}` |

### Validation

- `category` must be one of `cardio`, `strength`, `flexibility`, `balance` (table constraint, model validation, and schema validation).
- `duration_minutes` must be a positive integer (table constraint, model validation, and schema validation).
- `reps` / `sets` cannot be negative (table constraints, model validations, and schema validations).
- Failed validation returns a `400` with an `errors` object describing what went wrong.

## Running Tests

From the project root (not `server/`):

```bash
pipenv install --dev
pytest tests/ -v
```

The suite covers:
- **Model validations** — invalid category, non-positive duration, negative reps/sets all raise `ValueError`.
- **Table constraints** — bypassing the Python validators with raw SQL still gets rejected by the database's `CheckConstraint`s.
- **Relationships** — the `Workout.exercises` / `Exercise.workouts` association proxy and cascade deletes.
- **Routes** — success and failure (400/404) responses for every endpoint.

Tests run against a temporary sqlite file, so they never touch `app.db`.

## Verifying in the Flask Shell

```bash
flask shell
>>> from models import Exercise
>>> Exercise(name="Bad", category="not-a-category", equipment_needed=False)
# raises ValueError from the model validation
```