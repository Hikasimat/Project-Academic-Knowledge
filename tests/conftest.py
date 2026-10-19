import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import tempfile

from app.database import Base, get_db
from app.main import app
from app.cli import seed_courses_if_needed
from app.models.user import User
from app.security import get_password_hash, create_access_token

# Use a temporary SQLite database for tests
TEST_DB_FILE = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
TEST_DB_URL = f"sqlite:///{TEST_DB_FILE.name}"

engine_test = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    seed_courses_if_needed(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)
    try:
        os.remove(TEST_DB_FILE.name)
    except OSError:
        pass

@pytest.fixture
def db():
    connection = engine_test.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    yield db

    db.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_user(db):
    user = User(
        email="test_admin@plusuae.com",
        full_name="Test Administrator",
        hashed_password=get_password_hash("AdminPass123!"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"})

@pytest.fixture
def learner_user(db):
    user = User(
        email="test_learner@plusuae.com",
        full_name="Fatima Al-Mansoor",
        hashed_password=get_password_hash("LearnerPass123!"),
        role="learner",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def learner_token(learner_user):
    return create_access_token(data={"sub": str(learner_user.id), "email": learner_user.email, "role": "learner"})
