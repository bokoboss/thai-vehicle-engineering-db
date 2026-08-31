from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import make_engine
from app.main import app
from app.seed.fixtures import seed_phase0_fixtures
from app.seed.registry import seed_registry
from app.db.session import get_session


@pytest.fixture
def session(tmp_path) -> Generator[Session, None, None]:
    database_path = tmp_path / "test.sqlite"
    engine = make_engine(f"sqlite:///{database_path}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = factory()
    seed_registry(db)
    seed_phase0_fixtures(db)
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
