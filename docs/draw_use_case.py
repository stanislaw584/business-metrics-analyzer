"""Построение Use Case-диаграммы Business Metrics Analyzer (docs/use_case_diagram.png).

Запуск: python docs/draw_use_case.py
"""
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyBboxPatch

W, H = 2000, 1760
FONT = "DejaVu Sans"
INK = "#1E2A3A"
LINE = "#44546A"
UC_FILL, UC_EDGE = "#EEF4FB", "#2F5D8A"
SEC_FILL = "#FFF6EC"
SEC_EDGE = "#C27A2C"

fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")
fig.patch.set_facecolor("white")

CX = 1000  # колонка вариантов использования
use_cases = {
    "notify": ("Уведомления о KPI", 200, False),
    "compare": ("Сравнение с предыдущим периодом", 340, True),
    "dash": ("Просмотр дашборда KPI", 480, False),
    "calc": ("Расчёт KPI", 620, True),
    "report": ("Формирование отчёта", 760, False),
    "export": ("Экспорт отчёта в Excel", 900, False),
    "upload": ("Загрузка данных о продажах", 1180, False),
    "check": ("Проверка формата файла", 1320, True),
    "metrics": ("Настройка метрик (плановые значения)", 1040, False),
    "users": ("Управление пользователями", 1460, False),
    "auth": ("Авторизация", 1600, False),
}
UC_H = 84


def uc_width(text):
    return max(300, len(text) * 12.6 + 90)


# граница системы
ax.add_patch(FancyBboxPatch((560, 120), 880, 1570, boxstyle="round,pad=0,rounding_size=18",
                            fc="#FAFBFD", ec=UC_EDGE, lw=2.2, zorder=1))
ax.text(CX, 150, "Business Metrics Analyzer", ha="center", va="center", fontsize=17,
        fontweight="bold", color=UC_EDGE, family=FONT, zorder=2)
ax.text(W / 2, 50, "Use Case-диаграмма системы Business Metrics Analyzer", ha="center",
        va="center", fontsize=20, fontweight="bold", color=INK, family=FONT)

for key, (text, y, secondary) in use_cases.items():
    w = uc_width(text)
    ax.add_patch(Ellipse((CX, y), w, UC_H, fc=SEC_FILL if secondary else UC_FILL,
                         ec=SEC_EDGE if secondary else UC_EDGE, lw=1.8, zorder=4))
    ax.text(CX, y, text, ha="center", va="center", fontsize=15, color=INK, family=FONT, zorder=5)


def edge_point(key, toward):
    """Точка на границе эллипса в направлении точки toward."""
    text, y, _ = use_cases[key]
    a, b = uc_width(text) / 2, UC_H / 2
    dx, dy = toward[0] - CX, toward[1] - y
    t = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
    return CX + dx * t, y + dy * t


def actor(x, y, name):
    kw = dict(color=UC_EDGE, lw=2.4, zorder=6, solid_capstyle="round")
    ax.add_patch(plt.Circle((x, y - 62), 20, fc="#DCE8F5", ec=UC_EDGE, lw=2.4, zorder=6))
    ax.plot([x, x], [y - 42, y + 18], **kw)
    ax.plot([x - 36, x + 36], [y - 22, y - 22], **kw)
    ax.plot([x, x - 28], [y + 18, y + 62], **kw)
    ax.plot([x, x + 28], [y + 18, y + 62], **kw)
    ax.text(x, y + 98, name, ha="center", va="center", fontsize=16, fontweight="bold",
            color=INK, family=FONT, zorder=6, linespacing=1.2)
    return x, y


def assoc(act, key, side):
    start = (act[0] + (46 if side == "left" else -46), act[1] - 20)
    end = edge_point(key, start)
    ax.plot([start[0], end[0]], [start[1], end[1]], color=LINE, lw=1.7, zorder=3)


def dashed(src, dst, label):
    _, y1, _ = use_cases[src]
    _, y2, _ = use_cases[dst]
    sgn = 1 if y2 > y1 else -1
    p1 = (CX, y1 + sgn * UC_H / 2)
    p2 = (CX, y2 - sgn * UC_H / 2)
    ax.annotate("", xy=p2, xytext=p1, zorder=3,
                arrowprops=dict(arrowstyle="-|>,head_length=0.9,head_width=0.45", color=SEC_EDGE,
                                lw=1.8, linestyle=(0, (6, 4)), shrinkA=0, shrinkB=0))
    ax.text(CX + 18, (p1[1] + p2[1]) / 2, label, ha="left", va="center", fontsize=14,
            color=SEC_EDGE, family=FONT, style="italic", zorder=5)


# акторы
cd = actor(240, 300, "Коммерческий\nдиректор")
ro = actor(240, 700, "Руководитель\nотдела")
mp = actor(240, 1040, "Менеджер\nпо продажам")
an = actor(1760, 860, "Аналитик")
ad = actor(1760, 1400, "Администратор")

for k in ("notify", "dash", "report"):
    assoc(cd, k, "left")
for k in ("dash", "report"):
    assoc(ro, k, "left")
for k in ("dash", "upload"):
    assoc(mp, k, "left")
for k in ("dash", "report", "export", "upload", "metrics"):
    assoc(an, k, "right")
assoc(ad, "users", "right")

dashed("compare", "dash", "«extend»")
dashed("dash", "calc", "«include»")
dashed("report", "calc", "«include»")
dashed("export", "report", "«extend»")
dashed("upload", "check", "«include»")

# примечание к авторизации
nx, ny = 1490, 1580
ax.add_patch(FancyBboxPatch((nx, ny), 400, 80, boxstyle="round,pad=0,rounding_size=8",
                            fc="#FFFBE6", ec="#B9A34A", lw=1.4, zorder=6))
ax.text(nx + 200, ny + 40, "Выполняют все акторы\nперед работой с системой", ha="center",
        va="center", fontsize=13.5, color=INK, family=FONT, zorder=7, linespacing=1.25)
ep = edge_point("auth", (nx, ny + 40))
ax.plot([nx, ep[0]], [ny + 40, ep[1]], color="#B9A34A", lw=1.4,
        linestyle=(0, (4, 3)), zorder=3)

# легенда
lx, ly = 40, 1600
ax.add_patch(Ellipse((lx + 40, ly), 60, 26, fc=UC_FILL, ec=UC_EDGE, lw=1.5))
ax.text(lx + 85, ly, "вариант использования", va="center", fontsize=13, color=INK, family=FONT)
ax.add_patch(Ellipse((lx + 40, ly + 44), 60, 26, fc=SEC_FILL, ec=SEC_EDGE, lw=1.5))
ax.text(lx + 85, ly + 44, "включаемый / расширяющий", va="center", fontsize=13, color=INK,
        family=FONT)

out = Path(__file__).with_name("use_case_diagram.png")
fig.savefig(out, dpi=150, facecolor="white")
print("saved", out)
