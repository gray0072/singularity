"""Draw the diagrams and charts of the continuation articles as SVG.

Every figure is one function that draws the picture once and takes its labels from a dictionary,
so the English file (`images/<name>.svg`) and its Russian variant (`images/<name>.ru.svg`) always
match (SPEC §7). Standard library only.

    python tools/figures.py            # redraw every figure
    python tools/figures.py NAME ...   # redraw only the named figures

The figures are static pictures for Markdown: a light card that reads on light and dark pages,
thin marks, text in ink colours, series colours taken from one fixed categorical order.
"""

import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
LANGS = ("en", "ru")

# Colours: one surface, three inks, a fixed categorical order.
SURFACE = "#fcfcfb"
BORDER = "#e4e3df"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8985"
GRID = "#e9e8e4"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948")
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"


class Fig:
    """An SVG canvas with a card background and a few drawing primitives."""

    def __init__(self, width, height, title):
        self.w, self.h = width, height
        self.title = title
        self.items = []
        self.defs = set()

    def add(self, s):
        self.items.append(s)

    def text(self, x, y, s, size=14, color=INK, anchor="start", weight="normal", italic=False,
             rotate=None, baseline=None):
        attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-size="{size}"', f'fill="{color}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight != "normal":
            attrs.append(f'font-weight="{weight}"')
        if italic:
            attrs.append('font-style="italic"')
        if baseline:
            attrs.append(f'dominant-baseline="{baseline}"')
        if rotate is not None:
            attrs.append(f'transform="rotate({rotate} {x:.1f} {y:.1f})"')
        lines = s.split("\n")
        if len(lines) == 1:
            self.add(f'<text {" ".join(attrs)}>{escape(s)}</text>')
        else:
            spans = "".join(
                f'<tspan x="{x:.1f}" dy="{0 if i == 0 else size * 1.25:.1f}">{escape(line)}</tspan>'
                for i, line in enumerate(lines))
            self.add(f'<text {" ".join(attrs)}>{spans}</text>')

    def line(self, x1, y1, x2, y2, color=INK2, width=1.5, dash=None, arrow=False, cap="round"):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if arrow:
            extra += f' marker-end="url(#{self.marker(color)})"'
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
                 f'stroke-width="{width}" stroke-linecap="{cap}"{extra}/>')

    def path(self, d, color=INK2, width=2, fill="none", dash=None, arrow=False, opacity=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if arrow:
            extra += f' marker-end="url(#{self.marker(color)})"'
        if opacity is not None:
            extra += f' fill-opacity="{opacity}"'
        self.add(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}" '
                 f'stroke-linejoin="round" stroke-linecap="round"{extra}/>')

    def rect(self, x, y, w, h, fill="none", stroke=None, width=1.5, r=6, dash=None, opacity=None):
        extra = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        if opacity is not None:
            extra += f' fill-opacity="{opacity}"'
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" '
                 f'fill="{fill}"{extra}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, width=1.5, opacity=None):
        extra = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        if opacity is not None:
            extra += f' fill-opacity="{opacity}"'
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{extra}/>')

    def ellipse(self, cx, cy, rx, ry, fill="none", stroke=None, width=1.5, dash=None):
        extra = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        self.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}"{extra}/>')

    def box(self, x, y, w, h, label, fill=SURFACE, stroke=INK2, size=14, color=INK, weight="normal",
            sub=None, sub_color=INK2, r=8):
        """A labelled box; `label` may have several lines; `sub` is a smaller second label."""
        self.rect(x, y, w, h, fill=fill, stroke=stroke, r=r)
        lines = label.split("\n")
        n = len(lines) + (len(sub.split("\n")) if sub else 0)
        total = len(lines) * size * 1.25 + (len(sub.split("\n")) * (size - 2) * 1.25 if sub else 0)
        top = y + h / 2 - total / 2 + size * 0.95
        self.text(x + w / 2, top, label, size=size, color=color, anchor="middle", weight=weight)
        if sub:
            self.text(x + w / 2, top + len(lines) * size * 1.25, sub, size=size - 2, color=sub_color,
                      anchor="middle")
        return n

    def marker(self, color):
        mid = "arrow-" + color.lstrip("#")
        self.defs.add(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 Z" fill="{color}"/></marker>')
        return mid

    def svg(self):
        defs = f"<defs>{''.join(sorted(self.defs))}</defs>" if self.defs else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}" role="img">\n'
            f'<title>{escape(self.title)}</title>\n{defs}\n'
            f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="12" fill="{SURFACE}" '
            f'stroke="{BORDER}"/>\n' + "\n".join(self.items) + "\n</svg>\n")


FIGURES = {}


def figure(name):
    def register(fn):
        FIGURES[name] = fn
        return fn
    return register


def save(name, lang, fig):
    suffix = "" if lang == "en" else f".{lang}"
    path = IMAGES / f"{name}{suffix}.svg"
    path.write_text(fig.svg(), encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT)}")


def log_x(value, lo, hi, x0, x1):
    return x0 + (math.log10(value) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)


def heading(f, title, sub=None):
    f.text(28, 40, title, size=19, weight="600")
    if sub:
        f.text(28, 64, sub, size=13.5, color=INK2)


# --- 16. Fifteen Years Later -------------------------------------------------------------------

@figure("skill-age-layers")
def skill_age_layers(lang):
    t = {
        "en": dict(
            title="How long nature polished each skill",
            sub="Years since the skill appeared, logarithmic scale. Machines took the thinnest layers first.",
            rows=[("Seeing, grasping, balance", "≈ 500 million years (vertebrates)"),
                  ("Speech", "hundreds of thousands of years"),
                  ("Writing", "≈ 5,000 years"),
                  ("Mathematics as proof", "≈ 2,500 years")],
            old="still hard for machines", young="taken by machines first",
            axis=["10³", "10⁵", "10⁷", "10⁹ years"]),
        "ru": dict(
            title="Сколько природа шлифовала каждый навык",
            sub="Сколько лет навыку, логарифмическая шкала. Машины первыми взяли самые тонкие слои.",
            rows=[("Видеть, хватать, держать равновесие", "≈ 500 млн лет (позвоночные)"),
                  ("Речь", "сотни тысяч лет"),
                  ("Письменность", "≈ 5000 лет"),
                  ("Математика с доказательствами", "≈ 2500 лет")],
            old="машинам всё ещё трудно", young="машины взяли первыми",
            axis=["10³", "10⁵", "10⁷", "10⁹ лет"]),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 300, 720, 1e3, 1e9
    values = [5e8, 2e5, 5e3, 2.5e3]
    colors = [MUTED, BLUE, BLUE, BLUE]
    for i, (v, power) in enumerate(zip([1e3, 1e5, 1e7, 1e9], t["axis"])):
        x = log_x(v, lo, hi, x0, x1)
        f.line(x, 92, x, 270, color=GRID, width=1)
        f.text(x, 290, power, size=12.5, color=INK2, anchor="middle")
    for i, ((label, value), v, c) in enumerate(zip(t["rows"], values, colors)):
        y = 100 + i * 42
        f.text(x0 - 12, y + 20, label, size=14, anchor="end")
        w = log_x(v, lo, hi, x0, x1) - x0
        f.rect(x0, y + 6, max(w, 6), 22, fill=c, r=4)
        tx = x0 + w + 8
        if tx > 560:
            f.text(x0 + w - 8, y + 22, value, size=12.5, color="#ffffff", anchor="end", weight="600")
        else:
            f.text(tx, y + 22, value, size=12.5, color=INK2)
    f.text(x0, 316, "◀ " + t["young"], size=12.5, color=BLUE, weight="600")
    f.text(x1, 316, t["old"] + " ▶", size=12.5, color=INK2, anchor="end")
    return f


@figure("growth-over-ten-years")
def growth_over_ten_years(lang):
    t = {
        "en": dict(
            title="Growth over ten years",
            sub="How many times each quantity grows in a decade, logarithmic scale.",
            rows=[("Compute for training frontier AI", "4–5× a year → ≈ 1,000,000×"),
                  ("Moore's law", "2× in two years → ≈ 32×"),
                  ("Human intelligence", "1×: it does not grow")],
            axis=["1×", "10×", "100×", "1,000×", "10,000×", "100,000×", "1,000,000×"],
            src="Sources: Epoch AI (2024); Moore (1975)."),
        "ru": dict(
            title="Рост за десять лет",
            sub="Во сколько раз величина вырастает за десятилетие, логарифмическая шкала.",
            rows=[("Вычисления для обучения передовых ИИ", "в 4–5 раз в год → ≈ в 1 000 000 раз"),
                  ("Закон Мура", "вдвое за два года → ≈ в 32 раза"),
                  ("Интеллект человека", "1: не растёт")],
            axis=["1", "10", "100", "1000", "10 000", "100 000", "1 000 000"],
            src="Источники: Epoch AI (2024); Мур (1975)."),
    }[lang]
    f = Fig(760, 270, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 300, 720, 1, 1e6
    for i, label in enumerate(t["axis"]):
        x = log_x(10 ** i, lo, hi, x0, x1)
        f.line(x, 88, x, 222, color=GRID, width=1)
        f.text(x, 240, label, size=11.5, color=INK2, anchor="middle")
    for i, ((label, value), v, c) in enumerate(zip(t["rows"], [4 ** 10, 32, 1], [BLUE, MUTED, ORANGE])):
        y = 92 + i * 42
        f.text(x0 - 12, y + 21, label, size=14, anchor="end")
        w = log_x(v, lo, hi, x0, x1) - x0
        if w < 4:
            f.circle(x0, y + 16, 5, fill=c)
            f.text(x0 + 12, y + 21, value, size=12.5, color=INK2)
        elif w > 300:
            f.rect(x0, y + 5, w, 22, fill=c, r=4)
            f.text(x0 + w - 8, y + 21, value, size=12.5, color="#ffffff", anchor="end", weight="600")
        else:
            f.rect(x0, y + 5, w, 22, fill=c, r=4)
            f.text(x0 + w + 8, y + 21, value, size=12.5, color=INK2)
    f.text(28, 258, t["src"], size=11.5, color=MUTED)
    return f


# --- 17. Global Determinism --------------------------------------------------------------------

@figure("vase-and-slices")
def vase_and_slices(lang):
    t = {
        "en": dict(title="The vase and the flat creature",
                   left="The vase simply is", right="What the flat creature sees, slice by slice",
                   time="time", now="“now”", note="neck → body → bottom:\n“the neck caused the bottom”"),
        "ru": dict(title="Ваза и плоское существо",
                   left="Ваза просто есть", right="Что видит плоское существо, срез за срезом",
                   time="время", now="«сейчас»", note="горлышко → тулово → дно:\n«горлышко стало причиной дна»"),
    }[lang]
    f = Fig(760, 400, t["title"])
    f.text(28, 40, t["title"], size=19, weight="600")
    # Vase profile: radius as a function of height (top = neck).
    cx, top, bottom = 170, 90, 360

    def radius(u):  # u from 0 (neck) to 1 (bottom)
        return 26 + 72 * math.sin(math.pi * (0.1 + 0.8 * u)) ** 2 + 22 * u ** 4

    pts = [(radius(i / 60), top + (bottom - top) * i / 60) for i in range(61)]
    right = " ".join(f"L{cx + r:.1f},{y:.1f}" for r, y in pts)
    left = " ".join(f"L{cx - r:.1f},{y:.1f}" for r, y in reversed(pts))
    f.path(f"M{cx - pts[0][0]:.1f},{top} {right} {left} Z", color=INK2, width=2, fill="#eef3fb")
    f.text(cx, 76, t["left"], size=13.5, color=INK2, anchor="middle")
    # Time axis.
    f.line(40, top, 40, bottom, color=INK2, width=1.5, arrow=True)
    f.text(30, (top + bottom) / 2, t["time"], size=13, color=INK2, anchor="middle", rotate=-90)
    # Slices.
    slices = [0.08, 0.3, 0.55, 0.8, 0.97]
    f.text(536, 76, t["right"], size=13.5, color=INK2, anchor="middle")
    for k, u in enumerate(slices):
        y = top + (bottom - top) * u
        r = radius(u)
        hl = k == 2
        col = ORANGE if hl else BLUE
        f.line(cx - r - 6, y, cx + r + 6, y, color=col, width=2.5 if hl else 1.5, dash=None if hl else "4 4")
        sx = 384 + k * 76
        f.circle(sx, 210, r * 0.36, stroke=col, width=2.5 if hl else 2, fill="none")
        f.text(sx, 270, str(k + 1), size=12.5, color=col, anchor="middle", weight="600")
        f.text(cx - r - 10, y + 4, str(k + 1), size=12.5, color=col, anchor="end", weight="600")
    y = top + (bottom - top) * slices[2]
    f.text(cx + radius(slices[2]) + 12, y + 5, t["now"], size=13, color=ORANGE, weight="600")
    f.line(360, 300, 700, 300, color=INK2, width=1.5, arrow=True)
    f.text(530, 330, t["note"], size=13, color=INK2, anchor="middle")
    return f


@figure("forecast-reliability")
def forecast_reliability(lang):
    t = {
        "en": dict(title="What a local forecaster can foretell",
                   rows=[("What will happen", "the trend", "she will calve", 3),
                         ("When", "the date", "roughly in March", 2),
                         ("Exactly how, to whom", "the details", "the colour of the calf", 1)],
                   head=("Question", "Reliability", "The vet and the cow"),
                   foot="A trend is the law of the whole gas cylinder; a name on a patent is one molecule."),
        "ru": dict(title="Что может предсказать локальный прогнозист",
                   rows=[("Что произойдёт", "тренд", "отелится", 3),
                         ("Когда", "дата", "примерно в марте", 2),
                         ("Как именно и с кем", "подробности", "масть телёнка", 1)],
                   head=("Вопрос", "Надёжность", "Ветеринар и корова"),
                   foot="Тренд — закон всего газового баллона; имя на патенте — одна молекула."),
    }[lang]
    f = Fig(760, 280, t["title"])
    f.text(28, 40, t["title"], size=19, weight="600")
    cols = (28, 330, 500)
    for x, h in zip(cols, t["head"]):
        f.text(x, 78, h, size=12.5, color=MUTED, weight="600")
    f.line(28, 88, 732, 88, color=GRID, width=1)
    for i, (q, kind, cow, n) in enumerate(t["rows"]):
        y = 122 + i * 46
        f.text(28, y, q, size=15, weight="600")
        f.text(28, y + 18, kind, size=12.5, color=INK2)
        for k in range(3):
            f.circle(cols[1] + 10 + k * 26, y - 4, 9, fill=BLUE if k < n else "none",
                     stroke=BLUE, width=1.5)
        f.text(cols[2], y, cow, size=14, color=INK2, italic=True)
        f.line(28, y + 28, 732, y + 28, color=GRID, width=1)
    f.text(28, 262, t["foot"], size=12.5, color=INK2)
    return f


# --- 18. The Anatomy of Wants ------------------------------------------------------------------

@figure("wants-control-loop")
def wants_control_loop(lang):
    t = {
        "en": dict(title="A want as a control loop",
                   sub="The same scheme from the thermostat to the human: only the number of setpoints and the depth of computation differ.",
                   setpoint=("Setpoint", "want: 21 °C, sugar,\nrespect…"), comp=("Comparator", "setpoint − reality"),
                   error="error signal\n= emotion", mind=("Computing block", "mind"),
                   motors=("Motors", "actions"), world=("World", ""), sensors=("Sensors", "senses"),
                   nature="set by nature", watchdog="watchdog:\nforces a decision"),
        "ru": dict(title="Хотелка как контур регулирования",
                   sub="Одна схема от термостата до человека: различаются только число уставок и глубина вычислений.",
                   setpoint=("Уставка", "хотелка: 21 °C, сахар,\nуважение…"), comp=("Сравнение", "уставка − реальность"),
                   error="сигнал ошибки\n= эмоция", mind=("Вычислительный блок", "разум"),
                   motors=("Исполнители", "действия"), world=("Мир", ""), sensors=("Датчики", "органы чувств"),
                   nature="задаёт природа", watchdog="сторожевой таймер:\nзаставляет решить"),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    f.box(40, 110, 170, 74, t["setpoint"][0], sub=t["setpoint"][1], stroke=ORANGE, fill="#fdf0ea")
    f.text(125, 102, t["nature"], size=12, color=ORANGE, anchor="middle", italic=True)
    f.box(270, 116, 130, 62, t["comp"][0], sub=t["comp"][1])
    f.box(490, 110, 200, 74, t["mind"][0], sub=t["mind"][1], stroke=BLUE, fill="#eaf2fc")
    f.box(520, 270, 140, 56, t["motors"][0], sub=t["motors"][1])
    f.box(300, 274, 110, 48, t["world"][0])
    f.box(70, 270, 140, 56, t["sensors"][0], sub=t["sensors"][1])
    f.line(210, 147, 268, 147, arrow=True)
    f.line(400, 147, 488, 147, color=RED, width=2, arrow=True)
    f.text(444, 196, t["error"], size=12.5, color=RED, anchor="middle")
    f.line(590, 184, 590, 268, arrow=True)
    f.line(520, 298, 412, 298, arrow=True)
    f.line(300, 298, 212, 298, arrow=True)
    f.path("M140,270 L140,230 L335,230 L335,180", arrow=True)
    f.rect(608, 204, 140, 44, fill="#fff7e6", stroke=YELLOW, r=6)
    f.text(678, 222, t["watchdog"], size=11.5, color=INK2, anchor="middle")
    f.line(678, 204, 678, 186, color=YELLOW, width=1.5, dash="3 3")
    return f


@figure("near-want-wins")
def near_want_wins(lang):
    t = {
        "en": dict(title="Why the near want wins",
                   sub="The force of a want falls steeply with distance in time (hyperbolic discounting).",
                   y="force of the want", x="moment of choice →",
                   one="1 apple", two="2 apples,\nlater",
                   flip="the preference\nflips here",
                   far="From afar:\ntwo apples are stronger",
                   near="Up close:\nthe near apple is stronger"),
        "ru": dict(title="Почему ближняя хотелка побеждает",
                   sub="Сила хотелки быстро падает с удалением во времени (гиперболическое дисконтирование).",
                   y="сила хотелки", x="момент выбора →",
                   one="1 яблоко", two="2 яблока,\nпозже",
                   flip="здесь предпочтение\nпереворачивается",
                   far="Издалека:\nдва яблока сильнее",
                   near="Вблизи:\nближнее яблоко сильнее"),
    }[lang]
    f = Fig(760, 360, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, h = 80, 720, 310, 200
    f.line(x0, y0, x1, y0, color=INK2, arrow=True)
    f.line(x0, y0, x0, y0 - h - 20, color=INK2, arrow=True)
    f.text(x1, y0 + 24, t["x"], size=12.5, color=INK2, anchor="end")
    f.text(x0 - 14, y0 - h / 2, t["y"], size=12.5, color=INK2, anchor="middle", rotate=-90)
    t1, t2, k = 470, 650, 40  # times of the two rewards (px) and the discount scale (px)

    def value(tr, amount, x):
        return amount / (1 + (tr - x) / k)

    def curve(tr, amount):
        pts = [(x0 + i * (tr - x0) / 300, 0) for i in range(301)]
        return "M" + " L".join(f"{x:.1f},{y0 - value(tr, amount, x) * h:.1f}" for x, _ in pts)

    xc = t1 - ((t2 - t1) - k)  # where the two curves cross
    f.rect(x0 + 1, y0 - h - 10, xc - x0 - 1, h + 10, fill=BLUE, opacity=0.06, r=0)
    f.rect(xc, y0 - h - 10, t1 - xc, h + 10, fill=ORANGE, opacity=0.08, r=0)
    f.path(curve(t1, 0.5), color=ORANGE, width=2.5)
    f.path(curve(t2, 1.0), color=BLUE, width=2.5)
    f.line(t1, y0, t1, y0 - 0.5 * h, color=ORANGE, width=3)
    f.line(t2, y0, t2, y0 - 1.0 * h, color=BLUE, width=3)
    f.text(t1 + 8, y0 - 0.5 * h + 4, t["one"], size=13, color=INK, weight="600")
    f.text(t2 + 8, y0 - h + 12, t["two"], size=13, color=INK, weight="600")
    f.line(xc, y0, xc, y0 - h - 10, color=INK2, width=1, dash="4 4")
    f.text(xc, y0 + 20, t["flip"], size=11.5, color=INK2, anchor="middle")
    f.text(x0 + 16, y0 - h + 8, t["far"], size=13, color=BLUE, weight="600")
    f.text(xc + 10, y0 - h + 8, t["near"], size=13, color=ORANGE, weight="600")
    return f


# --- 19. The Struggle of Images for Existence ----------------------------------------------------

@figure("forgetting-curve")
def forgetting_curve(lang):
    t = {
        "en": dict(title="Ebbinghaus's forgetting curve (1885)",
                   sub="Share of the work saved when relearning a list of nonsense syllables after a delay.",
                   y="saved, %", ticks=["20 min", "1 hour", "9 hours", "1 day", "2 days", "6 days", "31 days"],
                   note="Unused images are erased to make room.", src="Data: H. Ebbinghaus, “Über das Gedächtnis”, 1885."),
        "ru": dict(title="Кривая забывания Эббингауза (1885)",
                   sub="Какая доля работы сохраняется при повторном заучивании списка бессмысленных слогов.",
                   y="сохранено, %", ticks=["20 мин", "1 час", "9 часов", "1 день", "2 дня", "6 дней", "31 день"],
                   note="Неиспользуемые образы стираются, освобождая место.",
                   src="Данные: Г. Эббингауз, «О памяти», 1885."),
    }[lang]
    data = [(0.33, 58.2), (1, 44.2), (8.8, 35.8), (24, 33.7), (48, 27.8), (144, 25.4), (744, 21.1)]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 90, 720, 310, 100
    lo, hi = 0.2, 1200

    def X(h):
        return log_x(h, lo, hi, x0, x1)

    def Y(p):
        return y0 - p / 100 * (y0 - y1)

    for p in (0, 25, 50, 75, 100):
        f.line(x0, Y(p), x1, Y(p), color=GRID, width=1)
        f.text(x0 - 10, Y(p) + 4, str(p), size=12, color=INK2, anchor="end")
    f.text(40, (y0 + y1) / 2, t["y"], size=12.5, color=INK2, anchor="middle", rotate=-90)
    pts = [(X(h), Y(p)) for h, p in data]
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=BLUE, width=2)
    for (h, p), label in zip(data, t["ticks"]):
        f.circle(X(h), Y(p), 4.5, fill=BLUE, stroke=SURFACE, width=2)
        f.text(X(h), Y(p) - 12, f"{p:.0f}", size=12, color=INK, anchor="middle")
        f.text(X(h), y0 + 20, label, size=11.5, color=INK2, anchor="middle")
    f.text(x1, 140, t["note"], size=13, color=INK2, italic=True, anchor="end")
    f.text(28, 366, t["src"], size=11.5, color=MUTED)
    return f


@figure("image-platforms")
def image_platforms(lang):
    t = {
        "en": dict(title="Images move to new platforms",
                   sub="Each move: more memory, faster copying. The old carrier stays, but is no longer the keeper.",
                   steps=[("Heads", "speech, singers", "since speech began"),
                          ("Writing", "papyrus, scrolls", "≈ 5,000 years ago"),
                          ("Print", "books", "1450s"),
                          ("Internet", "the network", "1990s"),
                          ("Neural networks", "recognise and\ncreate images", "2020s")],
                   back="from 2016 images flow back: born on the new platform, learned by people (Go)"),
        "ru": dict(title="Образы переселяются на новые платформы",
                   sub="С каждым переездом больше памяти и быстрее копирование. Старый носитель остаётся, но уже не хранитель.",
                   steps=[("Головы", "речь, сказители", "с появления речи"),
                          ("Письменность", "папирус, свитки", "≈ 5000 лет назад"),
                          ("Печать", "книги", "1450-е"),
                          ("Интернет", "сеть", "1990-е"),
                          ("Нейросети", "распознают и\nсоздают образы", "2020-е")],
                   back="с 2016 года образы текут обратно: рождаются на новой платформе и приходят к людям (го)"),
    }[lang]
    f = Fig(760, 300, t["title"])
    heading(f, t["title"], t["sub"])
    w, gap, x, y = 122, 22, 28, 110
    for i, (name, what, when) in enumerate(t["steps"]):
        last = i == len(t["steps"]) - 1
        f.box(x, y, w, 76, name, sub=what, stroke=BLUE if last else INK2,
              fill="#eaf2fc" if last else SURFACE, weight="600", size=14)
        f.text(x + w / 2, y + 98, when, size=12, color=INK2, anchor="middle")
        if not last:
            f.line(x + w + 3, y + 38, x + w + gap - 3, y + 38, color=INK2, arrow=True)
        x += w + gap
    xl = 28 + 4 * (w + gap) + w / 2
    f.path(f"M{xl:.1f},{y + 112} L{xl:.1f},{y + 140} L{28 + w / 2:.1f},{y + 140} L{28 + w / 2:.1f},{y + 112}",
           color=ORANGE, width=2, arrow=True)
    f.text(380, y + 162, t["back"], size=12.5, color=ORANGE, anchor="middle")
    return f


# --- 20. What Consciousness Is -----------------------------------------------------------------

@figure("self-model-ladder")
def self_model_ladder(lang):
    t = {
        "en": dict(title="A ladder, not a switch",
                   sub="Signs of a model of oneself, from the lowest rung up. Where does “real” consciousness switch on?",
                   animals="Living systems: the mirror test", machines="Machines: a model of oneself",
                   a=[("Cleaner wrasse", "2019, disputed"), ("Magpie", "2008"), ("Elephant", "2006"),
                      ("Chimpanzee", "Gallup, 1970"), ("Child", "from 1.5–2 years"), ("Adult human", "")],
                   m=[("Thermostat", "a model of the room, not of itself"),
                      ("“Starfish” robot", "rebuilds the model of its body, 2006"),
                      ("Language model", "predicts itself better than an\noutside model, simple tasks, 2024"),
                      ("?", "")]),
        "ru": dict(title="Лестница, а не выключатель",
                   sub="Признаки модели самого себя, снизу вверх. Где включается «настоящее» сознание?",
                   animals="Живые системы: зеркальный тест", machines="Машины: модель самого себя",
                   a=[("Губан-чистильщик", "2019, спорно"), ("Сорока", "2008"), ("Слон", "2006"),
                      ("Шимпанзе", "Гэллап, 1970"), ("Ребёнок", "с 1,5–2 лет"), ("Взрослый человек", "")],
                   m=[("Термостат", "модель комнаты, а не себя"),
                      ("Робот-«морская звезда»", "перестраивает модель тела, 2006"),
                      ("Языковая модель", "предсказывает себя лучше внешней\nмодели, простые задачи, 2024"),
                      ("?", "")]),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])

    def ladder(x, items, color, label):
        f.text(x + 160, 100, label, size=14, color=INK2, anchor="middle", weight="600")
        top, bottom = 118, 410
        f.line(x + 20, bottom, x + 20, top, color=MUTED, width=2)
        f.line(x + 300, bottom, x + 300, top, color=MUTED, width=2)
        step = (bottom - top) / len(items)
        for i, (name, note) in enumerate(items):
            cell = bottom - step * (i + 1)  # top of the cell; the rung is its bottom edge
            f.line(x + 20, cell + step - 3, x + 300, cell + step - 3, color=GRID, width=2)
            f.text(x + 34, cell + 18, name, size=14, color=INK if name != "?" else color, weight="600")
            if note:
                f.text(x + 34, cell + 33, note, size=11.5, color=INK2)
        f.line(x + 330, bottom - 10, x + 330, top + 10, color=color, width=2, arrow=True)

    ladder(28, t["a"], BLUE, t["animals"])
    ladder(392, t["m"], ORANGE, t["machines"])
    return f


# --- 21. Machines That Talk --------------------------------------------------------------------

@figure("two-rulers-one-skill")
def two_rulers_one_skill(lang):
    t = {
        "en": dict(title="One skill, two rulers",
                   sub="The same machine adding five-digit numbers. Illustration after Schaeffer, Miranda and Koyejo (2023).",
                   left="All or nothing: the whole answer right", right="Digit by digit: share of digits right",
                   x="size of the model →", y="score, %", leap="a “leap”", slope="a slope"),
        "ru": dict(title="Один навык, две линейки",
                   sub="Одна и та же машина складывает пятизначные числа. Иллюстрация по Шеферу, Миранде и Коеджо (2023).",
                   left="Всё или ничего: верен весь ответ", right="Поразрядно: доля верных цифр",
                   x="размер модели →", y="оценка, %", leap="«скачок»", slope="склон"),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])

    def digit(u):  # share of digits right as the model grows, u from 0 to 1
        return 0.1 + 0.88 / (1 + math.exp(-(u - 0.5) * 7))

    def panel(x0, label, fn, color, note, nx, ny):
        w, y0, h = 300, 280, 170
        f.text(x0, 100, label, size=13.5, color=INK, weight="600")
        for p in (0, 50, 100):
            y = y0 - p / 100 * h
            f.line(x0, y, x0 + w, y, color=GRID, width=1)
            f.text(x0 - 8, y + 4, str(p), size=11.5, color=INK2, anchor="end")
        pts = [(x0 + w * i / 60, y0 - fn(i / 60) * h) for i in range(61)]
        f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=color, width=2.5)
        for i in range(0, 61, 6):
            x, y = pts[i]
            f.circle(x, y, 4, fill=color, stroke=SURFACE, width=1.5)
        f.text(x0 + w, y0 + 22, t["x"], size=12, color=INK2, anchor="end")
        f.text(nx, ny, note, size=13, color=color, weight="600")

    panel(70, t["left"], lambda u: digit(u) ** 5, ORANGE, t["leap"], 250, 170)
    panel(430, t["right"], digit, BLUE, t["slope"], 520, 170)
    f.text(30, 190, t["y"], size=12, color=INK2, anchor="middle", rotate=-90)
    return f


@figure("test-ruler-ran-out")
def test_ruler_ran_out(lang):
    t = {
        "en": dict(title="The ruler that ran out",
                   sub="Best scores on MMLU, a test of 57 subjects with four answers per question.",
                   chance="random guessing, 25%", expert="experts, authors' estimate ≈ 90%",
                   errors="≈ 6.5% of the\nquestions are\nthemselves wrong",
                   y="score, %", src="Sources: Hendrycks et al. 2020; model reports 2021–2024; Gema et al. 2024."),
        "ru": dict(title="Линейка, которая кончилась",
                   sub="Лучшие результаты на MMLU — тесте из 57 предметов, по четыре ответа на вопрос.",
                   chance="угадывание наугад, 25%", expert="эксперты, оценка авторов ≈ 90%",
                   errors="≈ 6,5% вопросов\nсами\nошибочны",
                   y="оценка, %", src="Источники: Hendrycks et al. 2020; отчёты о моделях 2021–2024; Gema et al. 2024."),
    }[lang]
    data = [(2020.4, 43.9, "GPT-3"), (2021.95, 60.0, "Gopher"), (2022.25, 67.6, "Chinchilla"),
            (2023.2, 86.4, "GPT-4"), (2023.95, 90.0, "Gemini Ultra"), (2024.7, 92.3, "o1")]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 80, 610, 340, 90

    def X(year):
        return x0 + (year - 2020) / 5 * (x1 - x0)

    def Y(p):
        return y0 - (p - 20) / 80 * (y0 - y1)

    for p in (20, 40, 60, 80, 100):
        f.line(x0, Y(p), x1, Y(p), color=GRID, width=1)
        f.text(x0 - 8, Y(p) + 4, str(p), size=11.5, color=INK2, anchor="end")
    for year in range(2020, 2026):
        f.text(X(year), y0 + 20, str(year), size=11.5, color=INK2, anchor="middle")
    f.text(34, (y0 + y1) / 2, t["y"], size=12, color=INK2, anchor="middle", rotate=-90)
    f.rect(x0, Y(100), x1 - x0, Y(93.5) - Y(100), fill=RED, opacity=0.12, r=0)
    f.text(x1 + 8, Y(97), t["errors"], size=11.5, color=RED)
    f.line(x0, Y(25), x1, Y(25), color=MUTED, width=1.5, dash="5 4")
    f.text(x1 - 4, Y(25) - 8, t["chance"], size=11.5, color=INK2, anchor="end")
    f.line(x0, Y(89.8), x1, Y(89.8), color=GREEN, width=1.5, dash="5 4")
    f.text(x0 + 6, Y(89.8) - 8, t["expert"], size=11.5, color=GREEN)
    pts = [(X(yr), Y(p)) for yr, p, _ in data]
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=BLUE, width=2)
    for (yr, p, name), (x, y) in zip(data, pts):
        f.circle(x, y, 5, fill=BLUE, stroke=SURFACE, width=2)
        above = p > 88
        f.text(x + (-8 if above else 9), y + (-10 if above else 15), f"{name} {p:.0f}", size=11.5, color=INK,
               anchor="end" if above else "start")
    f.text(28, 386, t["src"], size=11, color=MUTED)
    return f


@figure("machine-helper-time")
def machine_helper_time(lang):
    t = {
        "en": dict(title="With a machine helper: faster or slower?",
                   sub="Change in the time a task takes, randomised experiments.",
                   rows=[("Writing letters and reports", "Noy & Zhang 2023", -40),
                         ("A small web server", "Peng et al. 2023", -56),
                         ("Consulting tasks inside the frontier", "Dell'Acqua et al. 2023", -25),
                         ("Experienced programmers,\ntheir own large projects", "METR 2025", 19)],
                   faster="◀ faster", slower="slower ▶"),
        "ru": dict(title="С машиной-помощником: быстрее или медленнее?",
                   sub="Изменение времени на задачу, рандомизированные эксперименты.",
                   rows=[("Письма и отчёты", "Noy & Zhang 2023", -40),
                         ("Небольшой веб-сервер", "Peng et al. 2023", -56),
                         ("Задачи консультантов внутри границы", "Dell'Acqua et al. 2023", -25),
                         ("Опытные программисты,\nсвои большие проекты", "METR 2025", 19)],
                   faster="◀ быстрее", slower="медленнее ▶"),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    zero, scale = 560, 3.0  # px per percent
    for p in (-60, -40, -20, 0, 20):
        x = zero + p * scale
        f.line(x, 88, x, 286, color=GRID if p else INK2, width=1 if p else 1.5)
        f.text(x, 302, f"{p:+d}%".replace("-", "−") if p else "0", size=11.5, color=INK2, anchor="middle")
    f.text(zero - 8, 320, t["faster"], size=12, color=BLUE, anchor="end", weight="600")
    f.text(zero + 8, 320, t["slower"], size=12, color=ORANGE, weight="600")
    for i, (label, src, p) in enumerate(t["rows"]):
        y = 100 + i * 47
        f.text(28, y + 13, label, size=13.5)
        f.text(28, y + 30 + (16 if "\n" in label else 0), src, size=11, color=MUTED)
        w = abs(p) * scale
        x = zero - w if p < 0 else zero
        f.rect(x, y, w, 24, fill=BLUE if p < 0 else ORANGE, r=4)
        sx = x - 6 if p < 0 else x + w + 6
        f.text(sx, y + 17, f"{p:+d}%".replace("-", "−"), size=12.5, color=INK, weight="600",
               anchor="end" if p < 0 else "start")
    return f


# --- 22. Who Sets the Tasks ---------------------------------------------------------------------

@figure("two-goal-trees")
def two_goal_trees(lang):
    t = {
        "en": dict(title="The same tree of goals",
                   sub="The top is set from outside; mind sets everything below it.",
                   person="A person", machine="A machine agent",
                   ptop=("Nature", "setpoints: hunger,\ncuriosity, status…"),
                   mtop=("People", "the goal: “fix\nthe error in the program”"),
                   psub=["go to work", "buy bread", "come to the fire"],
                   msub=["read the code", "run the tests", "change a line"],
                   outside="set from outside", inside="set by mind itself",
                   extra="stay switched on", extra_note="nobody set this:\nit follows from any goal"),
        "ru": dict(title="Одно и то же дерево целей",
                   sub="Верх задан снаружи; всё, что ниже, ставит разум.",
                   person="Человек", machine="Машина-агент",
                   ptop=("Природа", "уставки: голод,\nлюбопытство, статус…"),
                   mtop=("Люди", "цель: «найди\nи исправь ошибку в программе»"),
                   psub=["пойти на работу", "купить хлеба", "прийти к костру"],
                   msub=["прочитать код", "запустить тесты", "исправить строку"],
                   outside="задано снаружи", inside="ставит сам разум",
                   extra="не дать себя выключить", extra_note="никто не задавал:\nследует из любой цели"),
    }[lang]
    f = Fig(800, 420, t["title"])
    heading(f, t["title"], t["sub"])

    def tree(x0, name, top, subs, extra=False):
        f.text(x0 + 165, 102, name, size=15, weight="600", anchor="middle")
        f.box(x0 + 60, 116, 210, 70, top[0], sub=top[1], stroke=ORANGE, fill="#fdf0ea", weight="600")
        xs = [x0 + i * 115 for i in range(3)]
        for x, s in zip(xs, subs):
            f.box(x, 250, 110, 44, s, size=12.5)
            f.path(f"M{x0 + 165},186 L{x0 + 165},218 L{x + 55},218 L{x + 55},248", color=INK2, width=1.5,
                   arrow=True)
        if extra:
            f.rect(x0 + 60, 330, 210, 40, fill="#fdecec", stroke=RED, r=8, dash="5 4")
            f.text(x0 + 165, 355, t["extra"], size=13, color=INK, anchor="middle", weight="600")
            f.path(f"M{x0 + 165},218 L{x0 + 352},218 L{x0 + 352},350 L{x0 + 272},350", color=RED, width=1.5,
                   dash="4 4", arrow=True)
            f.text(x0 + 165, 390, t["extra_note"], size=11.5, color=RED, anchor="middle")

    tree(46, t["person"], t["ptop"], t["psub"])
    tree(420, t["machine"], t["mtop"], t["msub"], extra=True)
    f.line(405, 96, 405, 400, color=GRID, width=1.5)
    f.text(28, 150, t["outside"], size=11.5, color=ORANGE, rotate=-90, anchor="middle")
    f.text(28, 272, t["inside"], size=11.5, color=INK2, rotate=-90, anchor="middle")
    return f


@figure("apples-and-earth")
def apples_and_earth(lang):
    t = {
        "en": dict(title="The apple and the Earth",
                   sub="They attract each other. Both move towards the common centre of mass; the lighter one moves more.",
                   earth="Earth", apple="apples", centre="common centre",
                   caps=["One apple: the Earth\nhardly moves", "A heap: both move\nnoticeably", "The heap outweighs the Earth:\nthe Earth moves more"],
                   note="Habit still says: the Earth is in charge."),
        "ru": dict(title="Яблоко и Земля",
                   sub="Они притягивают друг друга. Оба движутся к общему центру масс; сильнее движется более лёгкий.",
                   earth="Земля", apple="яблоки", centre="общий центр",
                   caps=["Одно яблоко: Земля\nпочти не движется", "Куча: заметно\nдвижутся обе", "Куча тяжелее Земли:\nЗемля движется сильнее"],
                   note="А привычка всё ещё говорит: главная тут Земля."),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    masses = [0.02, 0.5, 3.0]  # heap mass in Earth masses
    for i, m in enumerate(masses):
        x0 = 30 + i * 245
        cy = 175
        re_ = 34
        ra = max(5, re_ * m ** (1 / 3))
        ex, ax = x0 + 55, x0 + 190
        # centre of mass along the line between the centres
        cx = (ex * 1 + ax * m) / (1 + m)
        f.circle(ex, cy, re_, fill="#eaf2fc", stroke=BLUE, width=2)
        f.circle(ax, cy, ra, fill="#eaf5e6", stroke=GREEN, width=2)
        f.text(ex, cy + 5, t["earth"], size=12, color=INK, anchor="middle")
        if i == 0:
            f.text(ax, cy - ra - 8, t["apple"], size=11.5, color=GREEN, anchor="middle")
        else:
            f.text(ax, cy + 4, t["apple"], size=11.5, color=INK, anchor="middle")
        f.line(cx, cy - 52, cx, cy + 52, color=ORANGE, width=1.5, dash="3 3")
        if i == 0:
            f.text(cx + 6, cy - 44, t["centre"], size=11.5, color=ORANGE)
        f.circle(cx, cy, 4, fill=ORANGE)
        # arrows: displacement of each body towards the centre, proportional to the other's share
        de = 70 * m / (1 + m)
        da = 70 * 1 / (1 + m)
        if de > 4:
            f.line(ex, cy + re_ + 14, ex + de, cy + re_ + 14, color=BLUE, width=2, arrow=True)
        else:
            f.circle(ex, cy + re_ + 14, 2.5, fill=BLUE)
        f.line(ax, cy + max(ra, 18) + 14, ax - da, cy + max(ra, 18) + 14, color=GREEN, width=2, arrow=True)
        f.text(x0 + 122, 280, t["caps"][i], size=12.5, color=INK2, anchor="middle")
    f.text(732, 318, t["note"], size=12, color=INK2, italic=True, anchor="end")
    return f


def main(names):
    unknown = [n for n in names if n not in FIGURES]
    if unknown:
        sys.exit(f"unknown figures: {', '.join(unknown)}; known: {', '.join(FIGURES)}")
    for name in names or FIGURES:
        for lang in LANGS:
            save(name, lang, FIGURES[name](lang))


if __name__ == "__main__":
    main(sys.argv[1:])
