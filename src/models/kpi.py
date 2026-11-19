from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.metric_setting import MetricSetting


class Kpi(Base):
    """Рассчитанные KPI за период (кэш результатов)."""

    __tablename__ = "kpi"
    __table_args__ = (UniqueConstraint("period", "metric_name", name="uq_kpi_period_metric"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    metric_name: Mapped[str] = mapped_column(ForeignKey("metric_settings.metric_name"), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    metric: Mapped["MetricSetting"] = relationship(back_populates="kpis")

    def __repr__(self) -> str:
        return f"Kpi(period={self.period!r}, metric={self.metric_name!r}, value={self.value!r})"
