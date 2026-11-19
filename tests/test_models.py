from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.database import Base
from src.models import Sale, User


def test_metadata_tables():
    assert set(Base.metadata.tables) == {"users", "products", "sales", "kpi", "reports", "metric_settings"}


def test_unique_username(session):
    session.add(User(username="a", email="a@x.ru", password_hash="x", role="manager"))
    session.commit()
    session.add(User(username="a", email="b@x.ru", password_hash="x", role="manager"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_invalid_role_rejected(session):
    session.add(User(username="a", email="a@x.ru", password_hash="x", role="hacker"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_sale_requires_existing_manager_and_product(session):
    session.add(Sale(sale_date=date(2026, 1, 1), month="2026-01", revenue=1, cost=1,
                     orders_count=1, manager_id=999, product_id=999))
    with pytest.raises(IntegrityError):
        session.commit()


def test_negative_revenue_rejected(sample):
    sample.add(Sale(sale_date=date(2026, 1, 1), month="2026-01", revenue=-1, cost=0,
                    orders_count=1, manager_id=1, product_id=1))
    with pytest.raises(IntegrityError):
        sample.commit()
