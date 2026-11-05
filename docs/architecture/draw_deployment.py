"""Диаграмма развёртывания Business Metrics Analyzer (docs/architecture/deployment.png).

Запуск: python docs/architecture/draw_deployment.py
Текстовая версия диаграммы в нотации PlantUML: deployment.puml.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

W, H = 2640, 1320
FONT = "DejaVu Sans"
INK = "#1E2A3A"
DEP = "#44546A"
BLUE, BLUE_FILL = "#2F5D8A", "#E3EEF9"
ORANGE, ORANGE_FILL = "#C27A2C", "#FFF6EC"
GREY, GREY_FILL = "#7A8494", "#EEF0F3"
D = 22  # глубина объёмного узла

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.text(W / 2, 46, "Диаграмма развёртывания Business Metrics Analyzer (Docker, облако)", ha="center",
        va="center", fontsize=21, fontweight="bold", color=INK, family=FONT)


def node(x0, y0, x1, y1, title, sub="", ec=BLUE, fc="#F7FAFD", z=1, title_size=16):
    """UML-узел: объёмный прямоугольник."""
    top = Polygon([(x0, y0), (x0 + D, y0 - D), (x1 + D, y0 - D), (x1, y0)], closed=True, fc=fc, ec=ec,
                  lw=1.8, zorder=z)
    right = Polygon([(x1, y0), (x1 + D, y0 - D), (x1 + D, y1 - D), (x1, y1)], closed=True, fc=fc, ec=ec,
                    lw=1.8, zorder=z)
    ax.add_patch(top)
    ax.add_patch(right)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=fc, ec=ec, lw=1.8, zorder=z))
    ax.text(x0 + 18, y0 + 26, title, ha="left", va="center", fontsize=title_size, fontweight="bold",
            color=ec, family=FONT, zorder=z + 1)
    if sub:
        ax.text(x0 + 18, y0 + 56, sub, ha="left", va="center", fontsize=13, color="#4A5568",
                family=FONT, zorder=z + 1, style="italic")


def container(x0, y0, x1, y1, name, image, lines, ec=BLUE, fc=BLUE_FILL, stereo="«container»"):
    node(x0, y0, x1, y1, name, "", ec=ec, fc=fc, z=3, title_size=16)
    ax.text(x0 + 18, y0 + 56, image, ha="left", va="center", fontsize=13.5, color=ORANGE,
            family="DejaVu Sans Mono", zorder=5)
    ax.text(x0 + 18, y0 + 86, lines, ha="left", va="top", fontsize=13.5, color=INK, family=FONT,
            zorder=5, linespacing=1.35)
    ax.text(x1 - 12, y0 + 26, stereo, ha="right", va="center", fontsize=12, style="italic",
            color="#6A7179", family=FONT, zorder=5)


def artifact(x, y, w, name):
    ax.add_patch(FancyBboxPatch((x, y), w, 46, boxstyle="round,pad=0,rounding_size=6", fc="white",
                                ec=BLUE, lw=1.4, zorder=6))
    ax.text(x + 14, y + 23, name, ha="left", va="center", fontsize=13.5, color=INK, family=FONT,
            zorder=7)
    fx, fy = x + w - 30, y + 10  # значок артефакта
    ax.add_patch(Polygon([(fx, fy), (fx + 12, fy), (fx + 18, fy + 6), (fx + 18, fy + 26), (fx, fy + 26)],
                         closed=True, fc="white", ec=BLUE, lw=1.1, zorder=7))


def link(p1, p2, label, label_xy, ha="center", style="-"):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>,head_length=12,head_width=6", lw=2,
                                 color=DEP, zorder=8, shrinkA=0, shrinkB=0,
                                 linestyle="-" if style == "-" else (0, (6, 4))))
    ax.text(label_xy[0], label_xy[1], label, ha=ha, va="center", fontsize=13.5, color=INK,
            family=FONT, zorder=9, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none"))


# Клиент
node(50, 470, 400, 860, "Клиентское устройство", "ПК / ноутбук сотрудника")
artifact(80, 620, 290, "Браузер (Web UI)")
ax.text(80, 720, "Chrome, Firefox, Edge,\nЯндекс Браузер", ha="left", va="top", fontsize=13,
        color="#4A5568", family=FONT, linespacing=1.35)

# Облачный сервер
node(500, 130, 2000, 1260, "Облачный сервер (Linux VM, Docker Engine)",
     "docker compose, внутренняя сеть bma-network", fc="#FBFCFE")

container(560, 490, 890, 870, "Nginx", "nginx:alpine",
          "Reverse proxy, TLS,\nстатика Web UI\n0.5 CPU, 256 MB")
container(1010, 400, 1440, 960, "Приложение", "bma-api:latest",
          "FastAPI + Uvicorn\n1 CPU, 1 GB")
for i, name in enumerate(["REST API (контроллеры)", "Сервис аутентификации", "Сервис импорта",
                          "Сервис KPI", "Сервис отчётов"]):
    artifact(1035, 560 + i * 72, 380, name)

container(1590, 190, 1950, 430, "PostgreSQL", "postgres:16",
          "Продажи, пользователи, аудит\n2 CPU, 2 GB · том pgdata")
container(1590, 580, 1950, 800, "Redis", "redis:7-alpine", "Кэш KPI\n0.5 CPU, 512 MB")
container(1590, 960, 1950, 1200, "MinIO", "minio/minio",
          "Хранилище отчётов (S3)\n0.5 CPU, 512 MB · том miniodata")

# Внешние сервисы
node(2130, 330, 2580, 1110, "Внешние сервисы", "", ec=GREY, fc="#F6F7F9")
container(2160, 430, 2540, 600, "SMTP-сервер", "smtp.company.ru", "Email-уведомления",
          ec=GREY, fc=GREY_FILL, stereo="«external»")
container(2160, 790, 2540, 1010, "Источник данных", "1С / CSV / Excel",
          "Выгрузки продаж\nиз 1С, кассы, CRM", ec=GREY, fc=GREY_FILL,
          stereo="«external»")

# Связи
link((400, 680), (560, 680), "HTTPS :443", (480, 650))
link((890, 680), (1010, 680), "HTTP :8000", (950, 650))
link((1462, 440), (1590, 330), "SQL :5432", (1515, 300))
link((1462, 690), (1590, 690), "Redis :6379", (1525, 660))
link((1462, 930), (1590, 1060), "S3 API :9000", (1480, 1060))
link((1462, 505), (2160, 505), "SMTP :587", (2065, 478))
link((2160, 880), (1462, 880), "HTTPS / SFTP: выгрузки продаж", (1800, 850))

out = Path(__file__).with_name("deployment.png")
fig.savefig(out, dpi=150, facecolor="white")
print("saved", out)
