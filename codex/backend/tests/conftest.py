from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ddms.db.base import Base
import ddms.db.models  # noqa: F401 - ensure models are registered
from ddms.main import app


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
    # Patch session dependency in all entry points
    import ddms.main as main_mod
    import ddms.db.session as session_mod
    import ddms.api.deps as deps_mod

    monkeypatch.setattr(main_mod, "SessionLocal", TestSessionLocal)

    def _get_session():
        return _session_dep_factory(TestSessionLocal)

    monkeypatch.setattr(session_mod, "get_session", _get_session)
    monkeypatch.setattr(deps_mod, "get_session", _get_session)

    with TestClient(app) as c:
        # Trigger startup (owner bootstrap) against the test DB
        yield c
