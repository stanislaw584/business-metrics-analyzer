"""Проверка подключения к БД."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from src.database import engine  # noqa: E402

if __name__ == "__main__":
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Подключение успешно:", result.scalar())
