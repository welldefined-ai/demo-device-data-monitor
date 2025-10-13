from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ddms.db.base import Base
import ddms.db.models  # noqa: F401 - ensure models are registered
"""
NOTE: Avoid importing ddms.main at module scope to ensure we can monkeypatch
DB session dependencies before the app and routes are imported.
"""


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def TestSessionLocal(test_engine):  # type: ignore[no-untyped-def]
    return sessionmaker(bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False)


def _session_dep_factory(SessionLocal) -> Generator[Session, None, None]:  # noqa: N802
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(monkeypatch, TestSessionLocal):  # type: ignore[no-untyped-def]
    # Patch DB session dependency before importing the app/routes
    import ddms.db.session as session_mod

    def _get_session():  # type: ignore[no-untyped-def]
        session: Session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    monkeypatch.setattr(session_mod, "get_session", _get_session)

    # Import the app after patching
    import ddms.main as main_mod
    import ddms.api.deps as deps_mod
    import ddms.api.routes_auth as routes_auth_mod

    # Ensure bootstrap uses the test SessionLocal
    monkeypatch.setattr(main_mod, "SessionLocal", TestSessionLocal)

    # Ensure dependency overrides for any captured dependency functions
    main_mod.app.dependency_overrides[deps_mod.get_session] = _get_session
    main_mod.app.dependency_overrides[routes_auth_mod.get_session] = _get_session

    with TestClient(main_mod.app) as c:
        yield c
