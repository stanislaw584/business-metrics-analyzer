"""Диаграмма компонентов REST API Business Metrics Analyzer (docs/architecture/components.png).

Запуск: python docs/architecture/draw_components.py
Текстовая версия диаграммы в нотации PlantUML: components.puml.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

W, H = 2640, 1640
FONT = "DejaVu Sans"
INK = "#1E2A3A"
DEP = "#44546A"
BLUE, BLUE_FILL = "#2F5D8A", "#E3EEF9"
ORANGE, ORANGE_FILL = "#C27A2C", "#FFF6EC"
GREY, GREY_FILL = "#7A8494", "#EEF0F3"

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")
fig.patch.set_facecolor("white")

ax.text(W / 2, 48, "Диаграмма компонентов REST API: слоистая архитектура с элементами Clean Architecture",
        ha="center", va="center", fontsize=21, fontweight="bold", color=INK, family=FONT)

# слои
layers = [
    ("Presentation\n(API)", 100, 270, "#F4F8FC"),
    ("Application\n(Service\nLayer)", 290, 560, "#F7FAFD"),
    ("Domain", 580, 830, "#FBF8F2"),
    ("Infrastructure", 850, 1110, "#F4F8FC"),
]
for name, y0, y1, fill in layers:
    ax.add_patch(FancyBboxPatch((40, y0), W - 80, y1 - y0, boxstyle="round,pad=0,rounding_size=14",
                                fc=fill, ec="#B9C7D8", lw=1.6, zorder=0))
    ax.text(70, (y0 + y1) / 2, name, ha="left", va="center", fontsize=17, fontweight="bold",
            color=BLUE, family=FONT, linespacing=1.3)

BW, BH = 260, 70
boxes = {}


def component(key, x, y, name, w=BW, kind="comp"):
    if kind == "iface":
        ec, fc = ORANGE, ORANGE_FILL
    elif kind == "ext":
        ec, fc = GREY, GREY_FILL
    else:
        ec, fc = BLUE, BLUE_FILL
    ax.add_patch(FancyBboxPatch((x - w / 2, y - BH / 2), w, BH, boxstyle="round,pad=0,rounding_size=8",
                                fc=fc, ec=ec, lw=1.8, zorder=3))
    if kind == "iface":
        ax.text(x, y - 14, "«interface»", ha="center", va="center", fontsize=12, style="italic",
                color=ORANGE, family=FONT, zorder=4)
        ax.text(x, y + 12, name, ha="center", va="center", fontsize=14.5, color=INK, family=FONT,
                zorder=4)
    else:
        tx = x - 14 if kind == "comp" else x
        ax.text(tx, y, name, ha="center", va="center", fontsize=14.5, color=INK, family=FONT, zorder=4,
                linespacing=1.2)
    if kind == "comp":  # значок компонента UML
        ix, iy = x + w / 2 - 30, y - BH / 2 + 10
        ax.add_patch(Rectangle((ix, iy), 18, 22, fc="white", ec=ec, lw=1.2, zorder=4))
        ax.add_patch(Rectangle((ix - 5, iy + 4), 10, 5, fc="white", ec=ec, lw=1.2, zorder=5))
        ax.add_patch(Rectangle((ix - 5, iy + 13), 10, 5, fc="white", ec=ec, lw=1.2, zorder=5))
    boxes[key] = (x, y, w)


def database(key, x, y, name, w=230):
    h, e = 90, 22
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=GREY_FILL, ec="none", zorder=3))
    ax.plot([x - w / 2, x - w / 2], [y - h / 2, y + h / 2], color=GREY, lw=1.8, zorder=4)
    ax.plot([x + w / 2, x + w / 2], [y - h / 2, y + h / 2], color=GREY, lw=1.8, zorder=4)
    from matplotlib.patches import Ellipse, Arc
    ax.add_patch(Ellipse((x, y - h / 2), w, e, fc=GREY_FILL, ec=GREY, lw=1.8, zorder=5))
    ax.add_patch(Arc((x, y + h / 2), w, e, theta1=0, theta2=180, ec=GREY, lw=1.8, zorder=5))
    ax.add_patch(Ellipse((x, y + h / 2), w, e, fc=GREY_FILL, ec="none", zorder=2))
    ax.add_patch(Arc((x, y + h / 2), w, e, theta1=180, theta2=360, ec=GREY, lw=1.8, zorder=4))
    ax.text(x, y + 6, name, ha="center", va="center", fontsize=14.5, color=INK, family=FONT, zorder=6,
            linespacing=1.2)
    boxes[key] = (x, y - h / 2 - e / 2 + 6, w)


def top(key, dx=0):
    x, y, _ = boxes[key]
    return x + dx, y - BH / 2


def bottom(key, dx=0):
    x, y, _ = boxes[key]
    return x + dx, y + BH / 2


def side(key, right=True):
    x, y, w = boxes[key]
    return (x + w / 2 if right else x - w / 2), y


def arrow(p1, p2, style="dep"):
    if style == "real":  # реализация интерфейса
        a = FancyArrowPatch(p1, p2, arrowstyle="-|>,head_length=14,head_width=8", lw=1.7,
                            color=ORANGE, linestyle=(0, (6, 4)), zorder=2, shrinkA=0, shrinkB=0)
        a.set_facecolor("white")
    else:
        a = FancyArrowPatch(p1, p2, arrowstyle="->,head_length=11,head_width=6", lw=1.7, color=DEP,
                            linestyle=(0, (6, 4)), zorder=2, shrinkA=0, shrinkB=0)
    ax.add_patch(a)


def lollipop(key, label, left=False):
    x, y, _ = boxes[key]
    cy = y - BH / 2 - 52
    ax.plot([x, x], [cy + 14, y - BH / 2], color=ORANGE, lw=1.8, zorder=2)
    ax.add_patch(plt.Circle((x, cy), 14, fc=ORANGE_FILL, ec=ORANGE, lw=1.8, zorder=4))
    ax.text(x - 22 if left else x + 22, cy, label, ha="right" if left else "left", va="center", fontsize=13.5, color=ORANGE, family=FONT,
            style="italic", zorder=4)
    return x, cy - 14


# Presentation
YP, YA, YD, YI, YE = 185, 470, 705, 980, 1250
component("ac", 400, YP, "AuthController")
component("sc", 1000, YP, "SalesController")
component("kc", 1640, YP, "KpiController")
component("rc", 2150, YP, "ReportsController", w=290)

# Application
component("as", 400, YA, "AuthService")
component("us", 690, YA, "UserService", w=250)
component("sis", 1010, YA, "SalesImportService", w=300)
component("ks", 1640, YA, "KpiService", w=300)
component("rs", 2150, YA, "ReportService", w=300)
i_auth = lollipop("as", "IAuthService")
i_sales = lollipop("sis", "ISalesImportService")
i_kpi = lollipop("ks", "IKpiService", left=True)
i_rep = lollipop("rs", "IReportService")

# Domain
component("ur", 690, YD, "UserRepository", kind="iface", w=250)
component("val", 930, YD, "Validators", w=180)
component("sr", 1300, YD, "SaleRepository", kind="iface", w=250)
component("str", 1560, YD, "KpiStrategy", w=210)
component("mod", 2430, YD, "Модели: Sale, User,\nKpi, Report", w=250, kind="model")

# Infrastructure
component("jwt", 400, YI, "JwtProvider")
component("sur", 690, YI, "SqlUserRepository", w=270)
component("uow", 1010, YI, "UnitOfWork", w=220)
component("ssr", 1300, YI, "SqlSaleRepository", w=270)
component("rkc", 1730, YI, "RedisKpiCache", w=240)
component("xls", 2020, YI, "ExcelReportGenerator", w=300)
component("mail", 2330, YI, "EmailNotifier", w=230)

# Внешние ресурсы
database("pg", 985, YE, "PostgreSQL")
database("redis", 1730, YE, "Redis")
database("minio", 2020, YE, "MinIO (S3)")
component("smtp", 2330, YE, "SMTP-сервер", w=230, kind="ext")

# Presentation -> интерфейсы сервисов
arrow(bottom("ac"), i_auth)
arrow(bottom("sc"), i_sales)
arrow(bottom("kc"), i_kpi)
arrow(bottom("rc"), i_rep)

# Application
arrow(side("as"), side("us", right=False))
arrow(bottom("as"), top("jwt"))
arrow(bottom("us"), top("ur"))
arrow(bottom("sis", -90), top("val"))
arrow(bottom("sis", 40), top("uow", 40))
arrow(bottom("ks", -110), top("sr", 60))
arrow(bottom("ks", -80), top("str"))
arrow(bottom("ks", 90), top("rkc"))
arrow((boxes["rs"][0] - 150, YA - 10), (i_kpi[0] + 14, i_kpi[1] + 14))
arrow(bottom("rs", -130), top("xls"))
arrow(bottom("rs", 120), top("mail", -60))

# Реализация интерфейсов из Domain
arrow(top("sur"), bottom("ur"), style="real")
arrow(top("ssr"), bottom("sr"), style="real")

# Infrastructure
arrow(side("uow", right=False), side("sur"))
arrow(side("uow"), side("ssr", right=False))
arrow(bottom("sur"), (boxes["pg"][0] - 70, boxes["pg"][1]))
arrow(bottom("ssr"), (boxes["pg"][0] + 70, boxes["pg"][1]))
arrow(bottom("rkc"), (boxes["redis"][0], boxes["redis"][1]))
arrow(bottom("xls"), (boxes["minio"][0], boxes["minio"][1]))
arrow(bottom("mail"), top("smtp"))

ax.text(2430, YD + 62, "используются всеми слоями", ha="center", va="center", fontsize=12.5,
        style="italic", color="#6A7179", family=FONT)

# Легенда
ly = 1450
ax.add_patch(FancyBboxPatch((60, ly - 30), 1430, 150, boxstyle="round,pad=0,rounding_size=10",
                            fc="white", ec="#C9D3DF", lw=1.3))
ax.add_patch(plt.Circle((105, ly + 10), 12, fc=ORANGE_FILL, ec=ORANGE, lw=1.6))
ax.text(135, ly + 10, "предоставляемый интерфейс сервиса", va="center", fontsize=13.5, color=INK,
        family=FONT)
ax.add_patch(FancyArrowPatch((80, ly + 70), (180, ly + 70), arrowstyle="->,head_length=11,head_width=6",
                             lw=1.7, color=DEP, linestyle=(0, (6, 4))))
ax.text(200, ly + 70, "зависимость (использует)", va="center", fontsize=13.5, color=INK, family=FONT)
ax.add_patch(FancyArrowPatch((660, ly + 10), (760, ly + 10), arrowstyle="-|>,head_length=14,head_width=8",
                             lw=1.7, color=ORANGE, linestyle=(0, (6, 4)), fc="white"))
ax.text(780, ly + 10, "реализует интерфейс (инверсия зависимостей)", va="center", fontsize=13.5,
        color=INK, family=FONT)
ax.add_patch(FancyBboxPatch((680, ly + 52), 70, 36, boxstyle="round,pad=0,rounding_size=6",
                            fc=GREY_FILL, ec=GREY, lw=1.5))
ax.text(780, ly + 70, "внешний ресурс (контейнер или сервис)", va="center", fontsize=13.5, color=INK,
        family=FONT)

out = Path(__file__).with_name("components.png")
fig.savefig(out, dpi=150, facecolor="white")
print("saved", out)
