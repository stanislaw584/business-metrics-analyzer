"""Наполнение базы тестовыми данными (Faker, воспроизводимо: seed=42)."""
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from faker import Faker  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from src.database import SessionLocal  # noqa: E402
from src.models import Kpi, MetricSetting, Product, Report, Sale, User  # noqa: E402
from src.queries import get_kpi_dashboard  # noqa: E402

SEED = 42

CATALOG = {
    "Электроника": ["Смартфон", "Ноутбук", "Наушники", "Планшет", "Монитор"],
    "Одежда": ["Куртка", "Джинсы", "Футболка", "Кроссовки"],
    "Продукты": ["Кофе", "Чай", "Шоколад", "Крупа"],
    "Бытовая химия": ["Порошок стиральный", "Средство для посуды", "Освежитель воздуха"],
    "Книги": ["Роман", "Справочник", "Учебник"],
}


def seed_users(session: Session, fake: Faker, count: int = 10) -> list[User]:
    # Фиксированный набор ролей: гарантирует наличие менеджеров и директора
    roles = ["director", "admin", "analyst", "analyst"]
    roles += ["manager"] * max(count - len(roles), 0)
    users = [
        User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password_hash=fake.sha256(),
            role=role,
        )
        for role in roles[:count]
    ]
    session.add_all(users)
    session.flush()
    return users


def seed_products(session: Session, fake: Faker, rng: random.Random, count: int = 20) -> list[Product]:
    products = []
    for _ in range(count):
        category = rng.choice(list(CATALOG))
        kind = rng.choice(CATALOG[category])
        products.append(
            Product(
                name=f"{kind} {fake.bothify('??-###').upper()}",
                category=category,
                price=Decimal(rng.randint(10_000, 1_000_000)) / 100,
                description=f"{kind}: тестовая позиция категории «{category}»",
            )
        )
    session.add_all(products)
    session.flush()
    return products


def seed_metric_settings(session: Session) -> list[MetricSetting]:
    metrics = [
        MetricSetting(metric_name="revenue", formula="SUM(revenue)", is_active=True),
        MetricSetting(metric_name="profitability", formula="(revenue - cost) / revenue * 100", is_active=True),
        MetricSetting(metric_name="avg_check", formula="revenue / orders_count", is_active=True),
        MetricSetting(metric_name="conversion", formula="orders_count / visits * 100", is_active=False),
    ]
    session.add_all(metrics)
    session.flush()
    return metrics


def seed_sales(
    session: Session, rng: random.Random, users: list[User], products: list[Product], count: int = 500
) -> list[Sale]:
    managers = [u for u in users if u.role in ("manager", "director")]
    start_date = date(2026, 1, 1)
    sales = []
    for _ in range(count):
        sale_date = start_date + timedelta(days=rng.randint(0, 180))
        revenue = Decimal(rng.randint(100_000, 10_000_000)) / 100
        cost = (revenue * Decimal(rng.randint(40, 90)) / 100).quantize(Decimal("0.01"))
        sales.append(
            Sale(
                sale_date=sale_date,
                month=sale_date.strftime("%Y-%m"),
                revenue=revenue,
                cost=cost,
                orders_count=rng.randint(1, 20),
                manager_id=rng.choice(managers).id,
                product_id=rng.choice(products).id,
            )
        )
    session.add_all(sales)
    session.flush()
    return sales


def seed_kpi(session: Session, sales: list[Sale]) -> list[Kpi]:
    """Кэш KPI по месяцам для активных метрик."""
    active = set(session.scalars(select(MetricSetting.metric_name).where(MetricSetting.is_active)).all())
    kpis = []
    for month in sorted({s.month for s in sales}):
        d = get_kpi_dashboard(session, month)
        values = {
            "revenue": d["total_revenue"],
            "profitability": d["profitability"],
            "avg_check": d["avg_check"],
        }
        for name, value in values.items():
            if name in active:
                kpis.append(Kpi(period=month, metric_name=name, value=value))
    session.add_all(kpis)
    session.flush()
    return kpis


def seed_reports(session: Session, users: list[User], periods: list[str]) -> list[Report]:
    authors = [u for u in users if u.role in ("analyst", "director")]
    reports = [
        Report(
            report_type="monthly_kpi",
            period=period,
            file_path=f"reports/monthly_kpi_{period}.xlsx",
            created_by=authors[i % len(authors)].id,
        )
        for i, period in enumerate(periods)
    ]
    session.add_all(reports)
    session.flush()
    return reports


def seed_all(session: Session, seed: int = SEED, users_count: int = 10, products_count: int = 20,
             sales_count: int = 500) -> dict:
    """Единая точка входа: порядок вставки учитывает целостность связей."""
    fake = Faker("ru_RU")
    Faker.seed(seed)
    fake.unique.clear()
    rng = random.Random(seed)

    users = seed_users(session, fake, users_count)
    products = seed_products(session, fake, rng, products_count)
    seed_metric_settings(session)
    sales = seed_sales(session, rng, users, products, sales_count)
    kpis = seed_kpi(session, sales)
    reports = seed_reports(session, users, sorted({s.month for s in sales}))
    session.commit()
    return {"users": len(users), "products": len(products), "sales": len(sales),
            "kpi": len(kpis), "reports": len(reports)}


def main() -> None:
    session = SessionLocal()
    try:
        counts = seed_all(session)
        print("Создано:", ", ".join(f"{k} – {v}" for k, v in counts.items()))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
