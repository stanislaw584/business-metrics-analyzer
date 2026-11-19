"""Очистка таблиц перед повторным наполнением (схема и миграции не затрагиваются)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from src.database import engine  # noqa: E402

# Сначала дочерние таблицы, затем родительские
DELETE_ORDER = ["kpi", "reports", "sales", "products", "metric_settings", "users"]


def reset() -> None:
    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text(f"TRUNCATE {', '.join(DELETE_ORDER)} RESTART IDENTITY CASCADE"))
        else:
            for table in DELETE_ORDER:
                conn.execute(text(f"DELETE FROM {table}"))
            if engine.dialect.name == "sqlite":
                has_seq = conn.execute(
                    text("SELECT 1 FROM sqlite_master WHERE name = 'sqlite_sequence'")
                ).first()
                if has_seq:
                    conn.execute(text("DELETE FROM sqlite_sequence"))
    print("Таблицы очищены:", ", ".join(DELETE_ORDER))


if __name__ == "__main__":
    reset()
