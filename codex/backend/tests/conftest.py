from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import ddms.db.models  # noqa: F401 - ensure models are registered
from ddms.db.base import Base

"""
NOTE: Avoid importing ddms.main at module scope to ensure we can monkeypatch
DB session dependencies before the app and routes are imported.
"""


@pytest.fixture()
def test_engine() -> Generator[Engine, None, None]:
    engine: Engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def test_session_local(test_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )


def _session_dep_factory(session_local: sessionmaker[Session]) -> Generator[Session, None, None]:
    session: Session = session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(monkeypatch, test_session_local):  # type: ignore[no-untyped-def]
    # Patch DB session dependency before importing the app/routes
    import ddms.db.session as session_mod  # noqa: PLC0415

    def _get_session() -> Generator[Session, None, None]:
        session: Session = test_session_local()
        try:
            yield session
        finally:
            session.close()

    monkeypatch.setattr(session_mod, "get_session", _get_session)

    # Import the app after patching
    import ddms.api.deps as deps_mod  # noqa: PLC0415
    import ddms.main as main_mod  # noqa: PLC0415

    # Ensure bootstrap uses the test SessionLocal
    monkeypatch.setattr(main_mod, "SessionLocal", test_session_local)

    # Ensure dependency overrides for any captured dependency functions
    main_mod.app.dependency_overrides[session_mod.get_session] = _get_session
    # mypy: ignore attribute export since get_session is imported into deps
    main_mod.app.dependency_overrides[deps_mod.get_session] = _get_session  # type: ignore[attr-defined]

    with TestClient(main_mod.app) as c:
        yield c
