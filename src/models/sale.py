from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.product import Product
    from src.models.user import User


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("revenue >= 0", name="ck_sales_revenue"),
        CheckConstraint("cost >= 0", name="ck_sales_cost"),
        CheckConstraint("orders_count >= 1", name="ck_sales_orders_count"),
        Index("idx_sales_month", "month"),
        Index("idx_sales_manager_id", "manager_id"),
        Index("idx_sales_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_date: Mapped[date] = mapped_column(Date, nullable=False)
    # month = YYYY-MM, производный от sale_date; хранится осознанно для быстрых группировок
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    orders_count: Mapped[int] = mapped_column(default=1)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    product: Mapped["Product"] = relationship(back_populates="sales")
    manager: Mapped["User"] = relationship(back_populates="sales")

    def __repr__(self) -> str:
        return f"Sale(id={self.id!r}, date={self.sale_date!r}, revenue={self.revenue!r})"
