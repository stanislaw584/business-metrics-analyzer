from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from scripts.seed_data import seed_all
from src.models import Kpi, Sale, User
from tests.conftest import make_engine


def _snapshot(seed):
    session = sessionmaker(bind=make_engine())()
    counts = seed_all(session, seed=seed, sales_count=50)
    users = [(u.username, u.email, u.role) for u in session.scalars(select(User).order_by(User.id))]
    sales = [(s.sale_date, str(s.revenue), str(s.cost), s.orders_count, s.manager_id, s.product_id)
             for s in session.scalars(select(Sale).order_by(Sale.id))]
    session.close()
    return counts, users, sales


def test_seed_is_reproducible():
    assert _snapshot(42) == _snapshot(42)


def test_seed_differs_for_other_seed():
    assert _snapshot(42) != _snapshot(7)


def test_seed_creates_all_entities_and_kpi():
    session = sessionmaker(bind=make_engine())()
    counts = seed_all(session, sales_count=50)
    assert counts["users"] == 10 and counts["products"] == 20 and counts["sales"] == 50
    assert session.scalars(select(Kpi)).first() is not None
    session.close()
