from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.models import Product, Sale, User  # noqa: F401  (регистрация моделей в metadata)


def make_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, _):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session():
    engine = make_engine()
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample(session):
    """Менеджер, товар и три продажи: две в январе, одна в феврале."""
    manager = User(username="mgr1", email="mgr1@example.com", password_hash="x", role="manager")
    product = Product(name="Товар 1", category="Категория A", price=100)
    session.add_all([manager, product])
    session.commit()
    rows = [
        (date(2026, 1, 15), "2026-01", 1000, 700, 5),
        (date(2026, 1, 20), "2026-01", 500, 300, 5),
        (date(2026, 2, 3), "2026-02", 800, 400, 2),
    ]
    session.add_all(
        Sale(sale_date=d, month=m, revenue=r, cost=c, orders_count=o,
             manager_id=manager.id, product_id=product.id)
        for d, m, r, c, o in rows
    )
    session.commit()
    return session
