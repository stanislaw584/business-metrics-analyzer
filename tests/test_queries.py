from decimal import Decimal

from src.queries import (
    get_kpi_dashboard,
    get_monthly_revenue,
    get_revenue_by_manager,
    get_sales_by_month,
    get_sales_with_manager_and_product,
    get_top_products,
    get_total_revenue,
)


def test_get_total_revenue(sample):
    assert get_total_revenue(sample, "2026-01") == 1500


def test_get_total_revenue_empty_month(sample):
    assert get_total_revenue(sample, "2030-01") == Decimal("0.00")


def test_get_sales_by_month_sorted(sample):
    sales = get_sales_by_month(sample, "2026-01")
    assert [s.sale_date.day for s in sales] == [15, 20]


def test_get_sales_with_manager_and_product(sample):
    rows = get_sales_with_manager_and_product(sample, "2026-02")
    assert len(rows) == 1
    sale, username, product_name = rows[0]
    assert (username, product_name) == ("mgr1", "Товар 1")


def test_get_kpi_dashboard(sample):
    d = get_kpi_dashboard(sample, "2026-01")
    assert d["total_revenue"] == 1500
    assert d["total_cost"] == 1000
    assert d["total_orders"] == 10
    assert d["avg_check"] == 150
    assert d["profitability"] == Decimal("33.33")


def test_get_kpi_dashboard_empty_month(sample):
    d = get_kpi_dashboard(sample, "2030-01")
    assert d["total_orders"] == 0 and d["profitability"] == 0


def test_get_revenue_by_manager(sample):
    rows = get_revenue_by_manager(sample, "2026-01")
    assert [(r.username, r.revenue) for r in rows] == [("mgr1", 1500)]


def test_get_top_products(sample):
    rows = get_top_products(sample, "2026-01", limit=3)
    assert rows[0].name == "Товар 1" and rows[0].revenue == 1500


def test_get_monthly_revenue(sample):
    assert [(m, float(v)) for m, v in get_monthly_revenue(sample)] == [("2026-01", 1500.0), ("2026-02", 800.0)]
