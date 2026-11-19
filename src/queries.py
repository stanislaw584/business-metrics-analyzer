"""Запросы к БД через select() и Session.execute() (SQLAlchemy 2.0)."""
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Product, Sale, User

ZERO = Decimal("0.00")


def get_sales_by_month(session: Session, month: str) -> list[Sale]:
    """Возвращает все продажи за указанный месяц."""
    stmt = select(Sale).where(Sale.month == month).order_by(Sale.sale_date, Sale.id)
    return list(session.scalars(stmt).all())


def get_total_revenue(session: Session, month: str) -> Decimal:
    """Возвращает суммарную выручку за месяц."""
    stmt = select(func.sum(Sale.revenue)).where(Sale.month == month)
    result = session.execute(stmt).scalar()
    return Decimal(str(result)) if result is not None else ZERO


def get_sales_with_manager_and_product(session: Session, month: str):
    """Продажи с именем менеджера и названием товара (JOIN)."""
    stmt = (
        select(Sale, User.username, Product.name)
        .join(User, Sale.manager_id == User.id)
        .join(Product, Sale.product_id == Product.id)
        .where(Sale.month == month)
        .order_by(Sale.sale_date, Sale.id)
    )
    return session.execute(stmt).all()


def get_kpi_dashboard(session: Session, month: str) -> dict:
    """Агрегированный дашборд KPI за месяц."""
    stmt = select(
        func.sum(Sale.revenue).label("total_revenue"),
        func.sum(Sale.cost).label("total_cost"),
        func.sum(Sale.orders_count).label("total_orders"),
    ).where(Sale.month == month)
    row = session.execute(stmt).one()

    total_revenue = Decimal(str(row.total_revenue)) if row.total_revenue is not None else ZERO
    total_cost = Decimal(str(row.total_cost)) if row.total_cost is not None else ZERO
    total_orders = int(row.total_orders or 0)

    # Средний чек считаем как выручка / число заказов (а не среднее по строкам)
    avg_check = (total_revenue / total_orders).quantize(Decimal("0.01")) if total_orders else ZERO
    profitability = (
        ((total_revenue - total_cost) / total_revenue * 100).quantize(Decimal("0.01"))
        if total_revenue > 0
        else ZERO
    )
    return {
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_orders": total_orders,
        "avg_check": avg_check,
        "profitability": profitability,
    }


def get_revenue_by_manager(session: Session, month: str):
    """Выручка по менеджерам за месяц (GROUP BY), по убыванию."""
    stmt = (
        select(User.username, func.sum(Sale.revenue).label("revenue"))
        .join(User, Sale.manager_id == User.id)
        .where(Sale.month == month)
        .group_by(User.username)
        .order_by(func.sum(Sale.revenue).desc())
    )
    return session.execute(stmt).all()


def get_top_products(session: Session, month: str, limit: int = 5):
    """Топ товаров по выручке за месяц."""
    stmt = (
        select(Product.name, Product.category, func.sum(Sale.revenue).label("revenue"))
        .join(Product, Sale.product_id == Product.id)
        .where(Sale.month == month)
        .group_by(Product.id, Product.name, Product.category)
        .order_by(func.sum(Sale.revenue).desc())
        .limit(limit)
    )
    return session.execute(stmt).all()


def get_monthly_revenue(session: Session):
    """Динамика выручки по месяцам."""
    stmt = select(Sale.month, func.sum(Sale.revenue)).group_by(Sale.month).order_by(Sale.month)
    return session.execute(stmt).all()
