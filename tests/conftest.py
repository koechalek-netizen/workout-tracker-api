import os
import sys
import tempfile

# Make `server/` importable so tests can `from app import app`, `from models import ...`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

# Point the app at a throwaway sqlite file before it's imported, so we never
# touch the real app.db used for development.
db_fd, db_path = tempfile.mkstemp(suffix='.db')
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

import pytest  # noqa: E402

from app import app as flask_app  # noqa: E402
from models import db as _db  # noqa: E402


@pytest.fixture(scope='session')
def app():
    flask_app.config.update(TESTING=True)
    yield flask_app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def _fresh_db(app):
    """Create all tables before each test and drop them after, so tests
    never see leftover data from a previous test."""
    with app.app_context():
        _db.create_all()
        yield
        _db.session.remove()
        _db.drop_all()
