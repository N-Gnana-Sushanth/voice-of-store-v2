import os
import sys
from datetime import datetime, timezone
from typing import Generator, List
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_voice_of_store.db"
os.environ["SECRET_KEY"] = "TEST_SECRET_KEY_EXACTLY_64_CHARACTERS_FOR_TESTING_PURPOSES_ONLY_123"

from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.store import Store
from app.models.user import User, UserRole

# Use separate test database
TEST_DB_URL = "sqlite:///./test_voice_of_store.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before test session and drop when finished."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_voice_of_store.db"):
        try:
            os.remove("./test_voice_of_store.db")
        except Exception:
            pass


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Provide transactional database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Provide FastAPI test client with database dependency override."""
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
def test_stores(db: Session) -> List[Store]:
    """Create two test stores with distinct exposure measures."""
    store1 = Store(
        id="store-uuid-001",
        store_number="STORE-101",
        name="Main Street Supercenter",
        city="Chicago",
        state="IL",
        size_sqft=25000.0,
        avg_daily_transactions=3000.0,
        is_active=True,
    )
    store2 = Store(
        id="store-uuid-002",
        store_number="STORE-102",
        name="Airport Express Store",
        city="Chicago",
        state="IL",
        size_sqft=5000.0,
        avg_daily_transactions=800.0,
        is_active=True,
    )
    db.add_all([store1, store2])
    db.flush()
    return [store1, store2]


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create test admin user."""
    user = User(
        id="user-admin-uuid",
        email="admin@test.internal",
        hashed_password=hash_password("admin_secret_123!"),
        full_name="Admin Tester",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def store_manager_user(db: Session, test_stores: List[Store]) -> User:
    """Create test store manager user restricted to STORE-101."""
    user = User(
        id="user-sm-uuid",
        email="manager101@test.internal",
        hashed_password=hash_password("manager_secret_123!"),
        full_name="Store 101 Manager",
        role=UserRole.STORE_MANAGER,
        store_id=test_stores[0].id,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def analyst_user(db: Session) -> User:
    """Create test analyst user."""
    user = User(
        id="user-analyst-uuid",
        email="analyst@test.internal",
        hashed_password=hash_password("analyst_secret_123!"),
        full_name="Operations Analyst",
        role=UserRole.ANALYST,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


@pytest.fixture
def admin_headers(admin_user: User) -> dict:
    token = create_access_token(subject=admin_user.id, role=admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def store_manager_headers(store_manager_user: User) -> dict:
    token = create_access_token(
        subject=store_manager_user.id,
        role=store_manager_user.role,
        store_id=store_manager_user.store_id,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analyst_headers(analyst_user: User) -> dict:
    token = create_access_token(subject=analyst_user.id, role=analyst_user.role)
    return {"Authorization": f"Bearer {token}"}
