from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.kpi import Kpi


class MetricSetting(Base):
    __tablename__ = "metric_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique: на это поле ссылается kpi.metric_name
    metric_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    formula: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    kpis: Mapped[List["Kpi"]] = relationship(back_populates="metric")

    def __repr__(self) -> str:
        return f"MetricSetting(id={self.id!r}, metric_name={self.metric_name!r}, active={self.is_active!r})"
