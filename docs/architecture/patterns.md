# Паттерны проектирования – Business Metrics Analyzer

Паттерны выбраны под функциональные области из [README архитектуры](README.md) и под слои [диаграммы компонентов](components.png). Для каждого указано, где он применяется, почему выбран и от какой альтернативы отказались.

## 1. Сводная таблица

| Паттерн | Функциональная область | Где применяется | Обоснование | Альтернативы |
|---|---|---|---|---|
| Repository | 1, 2, 3 | `SqlSaleRepository`, `SqlUserRepository` в слое Infrastructure, интерфейсы `SaleRepository`, `UserRepository` в Domain | изолирует бизнес-логику от SQLAlchemy и PostgreSQL, сервисы тестируются с репозиторием в памяти | прямые запросы к ORM из сервисов |
| Unit of Work | 2 | импорт данных о продажах, сохранение настроек метрик | импорт файла в 100 тыс. строк записывается атомарно: при ошибке откатывается весь пакет, а не часть строк | ручной `commit` / `rollback` в каждом сервисе |
| Service Layer | 1–6 | `AuthService`, `SalesImportService`, `KpiService`, `ReportService`, `UserService` | бизнес-сценарии (User Stories) живут в одном месте, контроллеры FastAPI остаются тонкими | логика в контроллерах |
| Strategy | 3 | `KpiStrategy`: выручка, средний чек, конверсия, рентабельность | новый KPI (US-08 «Настройка метрик») добавляется новым классом без изменения `KpiService` | `if / elif` по названию метрики |
| Factory | 5 | `ReportFactory` создаёт генератор отчёта по типу (по отделам, по менеджерам, по периодам) и формату (Excel, PDF) | контроллер не знает конкретных классов отчётов, новый тип отчёта не ломает существующие | условные операторы в `ReportService` |
| DTO | 1–6 | Pydantic-схемы запросов и ответов API: `KpiResultDto`, `DashboardDto`, `ImportResultDto` | чёткий контракт API, ORM-модели и внутренние поля не утекают наружу, версия API меняется независимо от БД | отдавать ORM-модели напрямую |
| Adapter | 2, 5 | `OneCSalesAdapter`, `CsvSalesAdapter`, `ExcelSalesAdapter`, `SmtpNotifier` | разные форматы источников (1С, CSV, Excel) приводятся к одному виду `SaleRecord`, смена почтового сервиса не затрагивает бизнес-логику | разбор каждого формата внутри сервиса импорта |
| Observer | 4, 7 | событие `SalesImported` оповещает подписчиков: сброс кэша KPI, пересчёт дашборда, запись в журнал аудита, уведомление о падении KPI (US-09) | импорт не знает, кто реагирует на загрузку данных, новые подписчики добавляются без изменения импорта | периодический опрос базы, прямые вызовы из импорта |

Номера функциональных областей: 1 – аутентификация и пользователи, 2 – импорт данных, 3 – расчёт KPI, 4 – визуализация и дашборды, 5 – отчёты и экспорт, 6 – настройка метрик и справочников, 7 – логирование и аудит.

## 2. Фрагменты кода

### 2.1 Repository + Unit of Work

Интерфейс репозитория объявлен в слое Domain, реализация на SQLAlchemy – в Infrastructure. Сервис импорта работает через Unit of Work и не знает о базе данных.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class SaleRecord:
    id: int | None
    sale_date: date
    department: str
    manager: str
    revenue: Decimal
    cost: Decimal
    receipts: int
    visitors: int


class SaleRepository(ABC):
    """Domain: что нужно бизнес-логике от хранилища продаж."""

    @abstractmethod
    def add_many(self, records: list[SaleRecord]) -> None: ...

    @abstractmethod
    def get_by_period(self, start: date, end: date, department: str | None = None) -> list[SaleRecord]: ...


class SqlSaleRepository(SaleRepository):
    """Infrastructure: реализация на SQLAlchemy."""

    def __init__(self, session):
        self.session = session

    def add_many(self, records: list[SaleRecord]) -> None:
        self.session.add_all([SaleModel.from_domain(r) for r in records])

    def get_by_period(self, start, end, department=None):
        query = self.session.query(SaleModel).filter(SaleModel.sale_date.between(start, end))
        if department:
            query = query.filter(SaleModel.department == department)
        return [row.to_domain() for row in query.all()]


class UnitOfWork:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.sales = SqlSaleRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()


class SalesImportService:
    def __init__(self, uow_factory, validator):
        self.uow_factory = uow_factory
        self.validator = validator

    def import_records(self, records: list[SaleRecord]) -> "ImportResultDto":
        valid, errors = self.validator.split(records)
        with self.uow_factory() as uow:  # весь пакет – одна транзакция
            uow.sales.add_many(valid)
        return ImportResultDto(loaded=len(valid), errors=errors)
```

### 2.2 Strategy для расчёта KPI

Каждый KPI – отдельная стратегия с общим интерфейсом. `KpiService` перебирает зарегистрированные стратегии, поэтому новая метрика не требует правок сервиса.

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PeriodTotals:
    revenue: float
    cost: float
    receipts: int
    visitors: int


class KpiStrategy(ABC):
    code: str

    @abstractmethod
    def calculate(self, totals: PeriodTotals) -> float: ...


class RevenueStrategy(KpiStrategy):
    code = "revenue"

    def calculate(self, totals: PeriodTotals) -> float:
        return totals.revenue


class AverageCheckStrategy(KpiStrategy):
    code = "average_check"

    def calculate(self, totals: PeriodTotals) -> float:
        return 0.0 if totals.receipts == 0 else totals.revenue / totals.receipts


class ConversionStrategy(KpiStrategy):
    code = "conversion"

    def calculate(self, totals: PeriodTotals) -> float:
        return 0.0 if totals.visitors == 0 else totals.receipts / totals.visitors * 100


class ProfitabilityStrategy(KpiStrategy):
    code = "profitability"

    def calculate(self, totals: PeriodTotals) -> float:
        return 0.0 if totals.revenue == 0 else (totals.revenue - totals.cost) / totals.revenue * 100


class KpiService:
    def __init__(self, strategies: list[KpiStrategy]):
        self.strategies = strategies

    def calculate_all(self, totals: PeriodTotals) -> dict[str, float]:
        return {s.code: round(s.calculate(totals), 2) for s in self.strategies}


service = KpiService([RevenueStrategy(), AverageCheckStrategy(), ConversionStrategy(), ProfitabilityStrategy()])
print(service.calculate_all(PeriodTotals(revenue=150_000, cost=120_000, receipts=600, visitors=2_400)))
# {'revenue': 150000, 'average_check': 250.0, 'conversion': 25.0, 'profitability': 20.0}
```

### 2.3 Factory для отчётов

`ReportFactory` выбирает генератор по формату. Контроллер и `ReportService` работают только с интерфейсом `ReportGenerator`.

```python
from abc import ABC, abstractmethod


class ReportGenerator(ABC):
    extension: str

    @abstractmethod
    def render(self, rows: list[dict]) -> bytes: ...


class ExcelReportGenerator(ReportGenerator):
    extension = "xlsx"

    def render(self, rows: list[dict]) -> bytes:
        from io import BytesIO
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.append(list(rows[0].keys()))
        for row in rows:
            ws.append(list(row.values()))
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()


class PdfReportGenerator(ReportGenerator):
    extension = "pdf"

    def render(self, rows: list[dict]) -> bytes:
        ...  # формирование PDF, например через reportlab


class ReportFactory:
    _generators: dict[str, type[ReportGenerator]] = {
        "xlsx": ExcelReportGenerator,
        "pdf": PdfReportGenerator,
    }

    @classmethod
    def create(cls, fmt: str) -> ReportGenerator:
        try:
            return cls._generators[fmt]()
        except KeyError:
            raise ValueError(f"Неподдерживаемый формат отчёта: {fmt}") from None
```

### 2.4 Adapter для источников данных

Все источники приводятся к одному интерфейсу `SalesSource`, поэтому сервис импорта одинаково работает с 1С, CSV и Excel.

```python
from abc import ABC, abstractmethod

import pandas as pd

COLUMNS = {"Дата": "sale_date", "Отдел": "department", "Менеджер": "manager",
           "Сумма": "revenue", "Себестоимость": "cost", "Чеки": "receipts", "Посетители": "visitors"}


class SalesSource(ABC):
    @abstractmethod
    def read(self) -> pd.DataFrame: ...


class CsvSalesAdapter(SalesSource):
    def __init__(self, path: str):
        self.path = path

    def read(self) -> pd.DataFrame:
        return pd.read_csv(self.path, sep=";").rename(columns=COLUMNS)


class ExcelSalesAdapter(SalesSource):
    def __init__(self, path: str):
        self.path = path

    def read(self) -> pd.DataFrame:
        return pd.read_excel(self.path).rename(columns=COLUMNS)


class OneCSalesAdapter(SalesSource):
    """Адаптер к HTTP-сервису 1С: другой формат полей приводится к общему виду."""

    def __init__(self, client):
        self.client = client

    def read(self) -> pd.DataFrame:
        raw = self.client.get_sales()  # [{"Period": ..., "Division": ..., "Amount": ...}, ...]
        df = pd.DataFrame(raw)
        return df.rename(columns={"Period": "sale_date", "Division": "department", "Seller": "manager",
                                  "Amount": "revenue", "CostPrice": "cost", "Checks": "receipts",
                                  "Traffic": "visitors"})
```

## 3. Итог

Исходя из таблицы, паттерны покрывают все функциональные области системы. Repository, Unit of Work и Adapter изолируют бизнес-логику от базы данных и внешних систем. Service Layer и DTO задают границы между слоями. Strategy, Factory и Observer позволяют добавлять новые метрики, отчёты и реакции на события без изменения существующего кода (принцип открытости / закрытости).
