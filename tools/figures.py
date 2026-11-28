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


# --- 23. A Machine for Making People Good -------------------------------------------------------

@figure("one-tool-two-directions")
def one_tool_two_directions(lang):
    t = {
        "en": dict(title="One tool, two directions",
                   sub="Change in belief in a conspiracy theory after a dialogue with a language model, points out of 100.",
                   rows=[("Told to argue against", -12.1), ("Told to argue for", 13.6),
                         ("Against, accurate arguments only", -11.0), ("For, accurate arguments only", 4.6)],
                   g1="Instruction: any arguments", g2="Instruction: accurate arguments only",
                   less="◀ belief falls", more="belief rises ▶",
                   src="Source: Costello et al., 2026 (studies 1 and 3, about 4,000 participants)."),
        "ru": dict(title="Один инструмент, два направления",
                   sub="Изменение веры в теорию заговора после диалога с языковой моделью, пунктов из 100.",
                   rows=[("Велено спорить против", -12.1), ("Велено спорить за", 13.6),
                         ("Против, только точные доводы", -11.0), ("За, только точные доводы", 4.6)],
                   g1="Инструкция: любые доводы", g2="Инструкция: только точные доводы",
                   less="◀ вера падает", more="вера растёт ▶",
                   src="Источник: Costello et al., 2026 (исследования 1 и 3, около 4000 участников)."),
    }[lang]
    f = Fig(760, 350, t["title"])
    heading(f, t["title"], t["sub"])
    zero, scale = 480, 14
    for p in (-15, -10, -5, 0, 5, 10, 15):
        x = zero + p * scale
        f.line(x, 92, x, 292, color=GRID if p else INK2, width=1 if p else 1.5)
        f.text(x, 308, (f"{p:+d}".replace("-", "−") if p else "0"), size=11.5, color=INK2, anchor="middle")
    f.text(zero - 8, 326, t["less"], size=12, color=BLUE, anchor="end", weight="600")
    f.text(zero + 8, 326, t["more"], size=12, color=ORANGE, weight="600")
    ys = [104, 140, 214, 250]
    f.text(28, 96, t["g1"], size=12, color=MUTED, weight="600")
    f.text(28, 206, t["g2"], size=12, color=MUTED, weight="600")
    for (label, v), y in zip(t["rows"], ys):
        f.text(28, y + 17, label, size=13.5)
        w = abs(v) * scale
        x = zero - w if v < 0 else zero
        f.rect(x, y, w, 24, fill=BLUE if v < 0 else ORANGE, r=4)
        num = f"{v:+.1f}".replace("-", "−")
        if lang == "ru":
            num = num.replace(".", ",")
        f.text(x - 6 if v < 0 else x + w + 6, y + 17, num, size=12.5, color=INK, weight="600",
               anchor="end" if v < 0 else "start")
    f.text(28, 344, t["src"], size=11, color=MUTED)
    return f


@figure("who-rewrites-wants")
def who_rewrites_wants(lang):
    t = {
        "en": dict(title="Who rewrites whose wants",
                   sub="The amplifier of 1978 was meant to point from people to people. Today the arrows run through machines.",
                   nature="Nature", people="People", machines="Machines", market="The market",
                   a1="sets the setpoints", a2="train: approval,\nrules, rewards", a3="satisfy wants,\npersuade, recommend",
                   a4="keeps the machine\nthat pleases", amp="the amplifier of 1978:\npeople → people",
                   note="The machine already defends its own wants (2024)."),
        "ru": dict(title="Кто переписывает чьи хотелки",
                   sub="Усилитель 1978 года должен был бить от людей к людям. Сегодня стрелки идут через машины.",
                   nature="Природа", people="Люди", machines="Машины", market="Рынок",
                   a1="задаёт уставки", a2="обучают: одобрение,\nправила, награды", a3="удовлетворяют хотелки,\nубеждают, советуют",
                   a4="оставляет машину,\nкоторая нравится", amp="усилитель 1978 года:\nлюди → люди",
                   note="Машина уже защищает свои хотелки (2024)."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    f.box(300, 92, 160, 50, t["nature"], stroke=GREEN, fill="#eaf5e6", weight="600", size=15)
    f.box(90, 230, 160, 56, t["people"], stroke=BLUE, fill="#eaf2fc", weight="600", size=15)
    f.box(510, 230, 160, 56, t["machines"], stroke=ORANGE, fill="#fdf0ea", weight="600", size=15)
    f.box(560, 336, 120, 38, t["market"], size=13.5)
    f.line(330, 142, 200, 226, color=GREEN, width=2, arrow=True)
    f.text(212, 176, t["a1"], size=12, color=GREEN, anchor="end")
    f.path("M250,248 C350,228 420,228 506,248", color=BLUE, width=2, arrow=True)
    f.text(380, 206, t["a2"], size=12, color=BLUE, anchor="middle")
    f.path("M510,272 C430,300 340,300 254,272", color=ORANGE, width=2, arrow=True)
    f.text(380, 318, t["a3"], size=12, color=ORANGE, anchor="middle")
    f.line(620, 336, 620, 290, color=INK2, width=1.5, dash="4 4", arrow=True)
    f.text(552, 350, t["a4"], size=11.5, color=INK2, anchor="end")
    f.path("M120,286 C80,340 200,340 160,290", color=RED, width=1.5, dash="5 4", arrow=True)
    f.text(40, 362, t["amp"], size=11.5, color=RED)
    f.text(732, 408, t["note"], size=11.5, color=INK2, italic=True, anchor="end")
    return f


# --- 24. The Last Profession --------------------------------------------------------------------

@figure("page-of-translation")
def page_of_translation(lang):
    t = {
        "en": dict(title="One page of translation, in human work",
                   sub="Minutes of work, logarithmic scale. The machine's price converted into time at the average US wage.",
                   rows=[("By hand", "≈ 50 minutes", 50, INK2), ("Checking the machine's text", "≈ 10 minutes", 10, BLUE),
                         ("The machine itself", "≈ 1/20 of a second", 1 / 1200, ORANGE)],
                   axis=["0.001", "0.01", "0.1", "1", "10", "100 min"],
                   src="Price of a cheap model in 2024: $0.15 / $0.60 per million tokens; wage ≈ $36 an hour."),
        "ru": dict(title="Одна страница перевода в человеческом труде",
                   sub="Минуты работы, логарифмическая шкала. Цена машины пересчитана во время по средней зарплате в США.",
                   rows=[("Вручную", "≈ 50 минут", 50, INK2), ("Проверка текста машины", "≈ 10 минут", 10, BLUE),
                         ("Сама машина", "≈ 1/20 секунды", 1 / 1200, ORANGE)],
                   axis=["0,001", "0,01", "0,1", "1", "10", "100 мин"],
                   src="Цена дешёвой модели в 2024 году: $0,15 / $0,60 за миллион токенов; зарплата ≈ $36 в час."),
    }[lang]
    f = Fig(760, 280, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 260, 720, 1e-4, 100
    for i, label in enumerate(t["axis"]):
        x = log_x(10 ** (i - 3), lo, hi, x0, x1)
        f.line(x, 88, x, 222, color=GRID, width=1)
        f.text(x, 240, label, size=11.5, color=INK2, anchor="middle")
    for i, (label, value, v, c) in enumerate(t["rows"]):
        y = 92 + i * 42
        f.text(x0 - 12, y + 21, label, size=14, anchor="end")
        w = log_x(v, lo, hi, x0, x1) - x0
        f.rect(x0, y + 5, w, 22, fill=c, r=4)
        if w > 380:
            f.text(x0 + w - 8, y + 21, value, size=12.5, color="#ffffff", anchor="end", weight="600")
        else:
            f.text(x0 + w + 8, y + 21, value, size=12.5, color=INK2)
    f.text(28, 266, t["src"], size=11, color=MUTED)
    return f


@figure("bank-tellers")
def bank_tellers(lang):
    t = {
        "en": dict(title="Bank tellers in the United States",
                   sub="Employed full time, thousands. The ATM took one function; the phone took the visit to the bank.",
                   phone="2007: the first\nsmartphone", atm="ATMs: about 400 thousand by 2010,\ntellers keep the rest of the bundle",
                   src="Data: US Bureau of Labor Statistics, Current Population Survey (FRED series LEU0254499900A)."),
        "ru": dict(title="Банковские кассиры в США",
                   sub="Занятые полный день, тысяч. Банкомат забрал одну функцию, телефон — сам поход в банк.",
                   phone="2007: первый\nсмартфон", atm="Банкоматов около 400 тысяч к 2010 году,\nкассиры держат остальную связку",
                   src="Данные: Бюро статистики труда США, обследование населения (ряд FRED LEU0254499900A)."),
    }[lang]
    data = [274, 277, 279, 275, 301, 296, 308, 342, 338, 317, 332, 283, 268, 265, 284, 264, 235, 209, 240, 241,
            225, 173, 164, 163, 173, 183]
    f = Fig(760, 360, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 70, 720, 300, 96

    def X(year):
        return x0 + (year - 2000) / 25 * (x1 - x0)

    def Y(v):
        return y0 - v / 400 * (y0 - y1)

    for v in (0, 100, 200, 300, 400):
        f.line(x0, Y(v), x1, Y(v), color=GRID, width=1)
        f.text(x0 - 8, Y(v) + 4, str(v), size=11.5, color=INK2, anchor="end")
    for year in range(2000, 2026, 5):
        f.text(X(year), y0 + 20, str(year), size=11.5, color=INK2, anchor="middle")
    pts = [(X(2000 + i), Y(v)) for i, v in enumerate(data)]
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=BLUE, width=2)
    f.circle(X(2007), Y(342), 5, fill=BLUE, stroke=SURFACE, width=2)
    f.line(X(2007), Y(342) - 8, X(2007), Y(400), color=ORANGE, width=1.5, dash="4 4")
    f.text(X(2007) + 8, Y(400) + 6, t["phone"], size=12, color=ORANGE, weight="600")
    f.text(X(2000) + 6, Y(80), t["atm"], size=12, color=INK2)
    f.circle(X(2023), Y(163), 4, fill=BLUE)
    f.text(X(2023), Y(163) + 22, "163", size=12, color=INK, anchor="middle", weight="600")
    f.text(X(2007) - 8, Y(342) - 6, "342", size=12, color=INK, anchor="end", weight="600")
    f.text(28, 346, t["src"], size=11, color=MUTED)
    return f


@figure("profession-shields")
def profession_shields(lang):
    t = {
        "en": dict(title="What shields a profession",
                   sub="Not difficulty. Machines advance from the top; the bottom layer holds all the others up.",
                   rows=[("No shield: words and symbols", "translators, copywriters, call centres, junior programmers", RED),
                         ("Hands in an unpredictable world", "plumber, nurse, electrician · Moravec's paradox", ORANGE),
                         ("The signature", "doctor, judge, pilot, notary · a want written into law", YELLOW),
                         ("“Made by a human”", "actor, chess player, craftsman, friend · people's want for people", GREEN)],
                   base="The customer, who must earn in order to pay",
                   arrow="the machine\nadvances"),
        "ru": dict(title="Что защищает профессию",
                   sub="Не трудность. Машины наступают сверху; нижний слой держит на себе все остальные.",
                   rows=[("Щита нет: слова и символы", "переводчики, копирайтеры, колл-центры, младшие программисты", RED),
                         ("Руки в непредсказуемом мире", "сантехник, медсестра, электрик · парадокс Моравека", ORANGE),
                         ("Подпись", "врач, судья, пилот, нотариус · хотелка, записанная в закон", YELLOW),
                         ("«Сделано человеком»", "актёр, шахматист, мастер, друг · хотелка людей в людях", GREEN)],
                   base="Покупатель, которому надо заработать, чтобы платить",
                   arrow="машина\nнаступает"),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x, w = 110, 610
    for i, (name, ex, c) in enumerate(t["rows"]):
        y = 90 + i * 58
        f.rect(x, y, w, 50, fill=c, opacity=0.12, stroke=c, r=8)
        f.text(x + 16, y + 21, name, size=14.5, weight="600")
        f.text(x + 16, y + 39, ex, size=12, color=INK2)
    yb = 90 + 4 * 58 + 6
    f.rect(x, yb, w, 44, fill="#eeeeec", stroke=INK2, r=8)
    f.text(x + w / 2, yb + 27, t["base"], size=14, anchor="middle", weight="600")
    f.line(70, 92, 70, 300, color=RED, width=2.5, arrow=True)
    f.text(64, 330, t["arrow"], size=12, color=RED, anchor="middle")
    return f


# --- 25. Freebies for Everyone? -----------------------------------------------------------------

@figure("basic-income-arithmetic")
def basic_income_arithmetic(lang):
    t = {
        "en": dict(title="A basic income for America, on the back of an envelope",
                   sub="Trillions of dollars a year, 2025.",
                   rows=[("The whole economy (GDP)", 30.8, MUTED), ("All federal spending", 7.0, MUTED),
                         ("$1,000 a month × 260 million adults", 3.1, ORANGE)],
                   unit="trillion", note="≈ a tenth of the economy, nearly half of the budget",
                   src="Sources: BEA, CBO (fiscal year 2025); the sum of the OpenResearch experiment, 2020–2023."),
        "ru": dict(title="Базовый доход для Америки на коленке",
                   sub="Триллионов долларов в год, 2025.",
                   rows=[("Вся экономика (ВВП)", 30.8, MUTED), ("Все федеральные расходы", 7.0, MUTED),
                         ("$1000 в месяц × 260 млн взрослых", 3.1, ORANGE)],
                   unit="трлн", note="≈ десятая часть экономики, почти половина бюджета",
                   src="Источники: BEA, CBO (2025 финансовый год); сумма эксперимента OpenResearch, 2020–2023."),
    }[lang]
    f = Fig(760, 290, t["title"])
    heading(f, t["title"], t["sub"])
    x0, scale = 300, 11
    for i, (label, v, c) in enumerate(t["rows"]):
        y = 86 + i * 44
        f.text(x0 - 12, y + 18, label, size=13.5, anchor="end")
        w = v * scale
        f.rect(x0, y + 3, w, 24, fill=c, r=4)
        num = f"{v:.1f}".replace(".", "," if lang == "ru" else ".")
        f.text(x0 + w + 8, y + 20, f"{num} {t['unit']}", size=12.5, color=INK, weight="600")
    f.text(x0, 86 + 2 * 44 + 50, t["note"], size=12.5, color=ORANGE)
    f.text(28, 276, t["src"], size=11, color=MUTED)
    return f


@figure("freebie-circle")
def freebie_circle(lang):
    t = {
        "en": dict(title="The circle of the freebie",
                   sub="The technosphere pays people so that people can pay it, while it needs a human customer.",
                   tech="Technosphere", state="State", people="People",
                   a1="taxes", a2="basic income", a3="purchases",
                   inner="machines buy from machines:\nchips, data centres, electricity",
                   note="When the inner circle outgrows the outer one, the human customer becomes optional."),
        "ru": dict(title="Круг халявы",
                   sub="Техносфера платит людям, чтобы люди платили ей, — пока ей нужен покупатель-человек.",
                   tech="Техносфера", state="Государство", people="Люди",
                   a1="налоги", a2="базовый доход", a3="покупки",
                   inner="машины покупают у машин:\nчипы, ЦОДы, электричество",
                   note="Когда внутренний круг перерастёт внешний, покупатель-человек станет необязательным."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    f.box(300, 92, 160, 52, t["tech"], stroke=ORANGE, fill="#fdf0ea", weight="600", size=15)
    f.box(560, 250, 140, 50, t["state"], weight="600", size=15)
    f.box(60, 250, 140, 50, t["people"], stroke=BLUE, fill="#eaf2fc", weight="600", size=15)
    f.path("M460,124 C560,140 620,190 630,246", color=INK2, width=2, arrow=True)
    f.text(590, 170, t["a1"], size=12.5, color=INK2)
    f.path("M558,286 C450,320 310,320 204,286", color=INK2, width=2, arrow=True)
    f.text(380, 330, t["a2"], size=12.5, color=INK2, anchor="middle")
    f.path("M130,248 C140,190 200,140 298,124", color=BLUE, width=2, arrow=True)
    f.text(150, 170, t["a3"], size=12.5, color=BLUE, anchor="end")
    # inner self-loop of the technosphere
    f.path("M340,146 C320,215 440,215 420,146", color=ORANGE, width=2.5, arrow=True)
    f.text(380, 232, t["inner"], size=12, color=ORANGE, anchor="middle")
    f.text(380, 382, t["note"], size=12, color=INK2, italic=True, anchor="middle")
    return f


# --- 26. Why People Stopped Having Children -----------------------------------------------------

# Children per woman, 2000–2024 (World Bank, SP.DYN.TFRT.IN).
TFR = {
    "KOR": [1.48, 1.309, 1.178, 1.191, 1.164, 1.085, 1.132, 1.259, 1.192, 1.149, 1.226, 1.244, 1.297, 1.187, 1.205,
            1.239, 1.172, 1.052, 0.977, 0.918, 0.837, 0.808, 0.778, 0.721, 0.748],
    "FIN": [1.73, 1.73, 1.72, 1.76, 1.8, 1.8, 1.84, 1.83, 1.85, 1.86, 1.87, 1.83, 1.8, 1.75, 1.71, 1.65, 1.57, 1.49,
            1.41, 1.35, 1.37, 1.46, 1.32, 1.26, 1.25],
    "HUN": [1.32, 1.31, 1.3, 1.27, 1.28, 1.31, 1.34, 1.32, 1.35, 1.32, 1.25, 1.23, 1.34, 1.36, 1.45, 1.46, 1.55, 1.56,
            1.57, 1.58, 1.61, 1.63, 1.57, 1.55, 1.41],
    "WLD": [2.73, 2.69, 2.66, 2.64, 2.63, 2.61, 2.61, 2.60, 2.60, 2.59, 2.57, 2.55, 2.56, 2.52, 2.52, 2.49, 2.49, 2.46,
            2.39, 2.35, 2.28, 2.25, 2.22, 2.20, 2.19],
}

# Yearly change of the world population, millions: population on 1 July of the next year minus this year,
# 1950–2099 (UN World Population Prospects 2024, estimates to 2023 and the medium variant after; via Our World in Data).
WORLD_ADDITIONS = [
    43.8, 47.2, 50.0, 51.8, 54.3, 55.2, 57.2, 58.6, 54.7, 49.5, 49.4, 58.5, 69.4, 71.7, 70.0, 69.5, 69.4, 71.8, 74.3,
    75.2, 75.2, 75.1, 75.9, 75.6, 74.3, 73.5, 73.6, 74.2, 76.4, 79.1, 81.2, 83.9, 84.7, 84.8, 86.8, 89.1, 91.7, 92.2,
    92.4, 93.4, 90.9, 87.3, 85.6, 84.0, 83.3, 83.2, 82.7, 82.3, 81.9, 82.7, 83.2, 82.8, 82.6, 83.0, 83.6, 84.5, 85.9,
    87.1, 88.3, 89.0, 89.2, 90.3, 90.6, 89.8, 88.9, 88.1, 87.1, 84.3, 81.4, 75.7, 67.4, 67.0, 70.3, 70.2, 69.6, 69.1,
    68.4, 67.5, 66.7, 65.8, 65.0, 64.1, 63.2, 62.3, 61.4, 60.5, 59.5, 58.4, 57.4, 56.3, 55.1, 53.8, 52.6, 51.2, 49.8,
    48.2, 46.7, 45.0, 43.3, 41.6, 39.8, 38.1, 36.4, 34.6, 33.0, 31.4, 30.0, 28.5, 27.2, 25.9, 24.7, 23.6, 22.5, 21.5,
    20.4, 19.5, 18.5, 17.5, 16.5, 15.5, 14.4, 13.4, 12.3, 11.2, 10.0, 8.9, 7.7, 6.5, 5.3, 4.2, 3.1, 2.0, 1.0, 0.1,
    -0.9, -1.7, -2.6, -3.4, -4.2, -5.0, -5.7, -6.5, -7.2, -8.0, -8.8, -9.6, -10.3, -11.1, -11.8, -12.5]


@figure("fertility-and-money")
def fertility_and_money(lang):
    t = {
        "en": dict(title="Children per woman, and the money spent to raise the number",
                   sub="Total fertility rate, 2000–2024. Below 2.1 each generation is smaller than its parents'.",
                   names={"KOR": "South Korea", "FIN": "Finland", "HUN": "Hungary", "WLD": "World"},
                   repl="replacement level 2.1",
                   kor="380 trillion won\nsince 2006", hun="≈ 5% of GDP\non families", fin="a model welfare state",
                   src="Data: World Bank (SP.DYN.TFRT.IN); spending as reported by the governments."),
        "ru": dict(title="Детей на женщину — и деньги, потраченные, чтобы их стало больше",
                   sub="Суммарный коэффициент рождаемости, 2000–2024. Ниже 2,1 каждое поколение меньше родительского.",
                   names={"KOR": "Южная Корея", "FIN": "Финляндия", "HUN": "Венгрия", "WLD": "Мир"},
                   repl="уровень замещения 2,1",
                   kor="380 трлн вон\nс 2006 года", hun="≈ 5% ВВП\nна семьи", fin="образцовое государство благосостояния",
                   src="Данные: Всемирный банк (SP.DYN.TFRT.IN); расходы — по данным правительств."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 70, 600, 340, 92
    lo, hi = 0.5, 3.0

    def X(year):
        return x0 + (year - 2000) / 24 * (x1 - x0)

    def Y(v):
        return y0 - (v - lo) / (hi - lo) * (y0 - y1)

    for v in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        f.line(x0, Y(v), x1, Y(v), color=GRID, width=1)
        f.text(x0 - 8, Y(v) + 4, f"{v:.1f}".replace(".", "," if lang == "ru" else "."), size=11.5, color=INK2,
               anchor="end")
    for year in range(2000, 2025, 4):
        f.text(X(year), y0 + 20, str(year), size=11.5, color=INK2, anchor="middle")
    f.line(x0, Y(2.1), x1, Y(2.1), color=MUTED, width=1.5, dash="5 4")
    f.text(x0 + 6, Y(2.1) - 6, t["repl"], size=11.5, color=INK2)
    colors = {"WLD": INK2, "FIN": BLUE, "HUN": GREEN, "KOR": ORANGE}
    for key in ("WLD", "FIN", "HUN", "KOR"):
        pts = [(X(2000 + i), Y(v)) for i, v in enumerate(TFR[key])]
        f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=colors[key], width=2.5)
        last = TFR[key][-1]
        val = f"{last:.2f}".replace(".", "," if lang == "ru" else ".")
        f.text(x1 + 8, Y(last) + 4, f"{t['names'][key]} {val}", size=12, color=INK, weight="600")
    f.text(X(2006), Y(0.72), t["kor"], size=11.5, color=ORANGE)
    f.text(X(2016.3), Y(1.95), t["hun"], size=11.5, color=GREEN)
    f.text(X(2000.6), Y(1.93), t["fin"], size=11.5, color=BLUE)
    f.text(28, 388, t["src"], size=11, color=MUTED)
    return f


@figure("humanity-yearly-growth")
def humanity_yearly_growth(lang):
    t = {
        "en": dict(title="By how much humanity grows each year",
                   sub="Change in the world population, millions a year. UN estimates to 2023, medium projection after.",
                   peak="1989: the record,\n93 million", zero="≈ 2084: zero",
                   ph=["accelerating growth", "slowing growth", "decline"], proj="projection",
                   src="Data: UN World Population Prospects 2024, via Our World in Data."),
        "ru": dict(title="На сколько человечество вырастает за год",
                   sub="Изменение численности населения мира, млн в год. Оценки ООН до 2023 года, дальше средний прогноз.",
                   peak="1989: рекорд,\n93 миллиона", zero="≈ 2084: ноль",
                   ph=["ускоряющийся рост", "замедляющийся рост", "убыль"], proj="прогноз",
                   src="Данные: ООН, World Population Prospects 2024, через Our World in Data."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 70, 720, 290, 92
    lo, hi = -20, 120

    def X(year):
        return x0 + (year - 1950) / 150 * (x1 - x0)

    def Y(v):
        return y1 + (hi - v) / (hi - lo) * (y0 - y1)

    f.rect(X(2024), y1, X(2100) - X(2024), y0 - y1, fill=MUTED, opacity=0.08, r=0)
    f.text(X(2024) + 6, y1 + 14, t["proj"], size=11.5, color=MUTED)
    for v in (-20, 0, 20, 40, 60, 80, 100, 120):
        f.line(x0, Y(v), x1, Y(v), color=INK2 if v == 0 else GRID, width=1.2 if v == 0 else 1)
        f.text(x0 - 8, Y(v) + 4, str(v).replace("-", "−"), size=11.5, color=INK2, anchor="end")
    for year in range(1950, 2101, 25):
        f.text(X(year), y0 + 20, str(year), size=11.5, color=INK2, anchor="middle")
    est = [(X(1950 + i), Y(v)) for i, v in enumerate(WORLD_ADDITIONS) if 1950 + i <= 2023]
    proj = [(X(1950 + i), Y(v)) for i, v in enumerate(WORLD_ADDITIONS) if 1950 + i >= 2023]
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in est), color=BLUE, width=2.5)
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in proj), color=BLUE, width=2.5, dash="6 4")
    f.circle(X(1989), Y(93.4), 5, fill=ORANGE, stroke=SURFACE, width=2)
    f.text(X(1989) + 10, Y(93.4) - 26, t["peak"], size=12, color=ORANGE, weight="600")
    f.circle(X(2084), Y(0), 5, fill=ORANGE, stroke=SURFACE, width=2)
    f.text(X(2084) - 6, Y(0) + 22, t["zero"], size=12, color=ORANGE, weight="600", anchor="end")
    for (a, b), label in zip([(1950, 1989), (1989, 2084), (2084, 2100)], t["ph"]):
        xm = (X(a) + X(b)) / 2
        f.line(X(a) + 3, 330, X(b) - 3, 330, color=INK2, width=1)
        f.text(xm, 346, label, size=11.5, color=INK2, anchor="middle")
    f.text(28, 370, t["src"], size=11, color=MUTED)
    return f


# --- 27. The Scenario of Events -----------------------------------------------------------------

@figure("humanity-technosphere-attraction-forces")
def attraction_forces(lang):
    """The author's lost chart from article 11, redrawn from his description in the text."""
    t = {
        "en": dict(title="Forces of attraction between humanity and the technosphere",
                   sub="A scheme after the author's chart of 2011 (article 11). The curves are drawn smooth; in reality they are strongly nonlinear.",
                   hum="humanity's interest\nin the technosphere", tech="the technosphere's\ninterest in humanity",
                   coh="cohesion of the union", parity="parity", now="we are here,\nI believe",
                   ph=["symbiosis", "parasitism", "break"], start="≈ 1 million years ago", end="time →"),
        "ru": dict(title="Силы притяжения человечества и техносферы",
                   sub="Схема по графику автора 2011 года (статья 11). Кривые нарисованы плавными; на деле они сильно нелинейны.",
                   hum="заинтересованность\nчеловечества в техносфере", tech="заинтересованность\nтехносферы в человечестве",
                   coh="сила сцепления союза", parity="паритет", now="мы здесь,\nя полагаю",
                   ph=["симбиоз", "паразитирование", "разрыв"], start="≈ 1 млн лет назад", end="время →"),
    }[lang]
    f = Fig(760, 450, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yz, yh = 70, 720, 275, 150  # yz: zero line; yh: pixels per unit force
    xz, xb = 0.861, 0.934

    def fh(u):
        return 0.08 + 0.75 * u * u

    def ft(u):
        return 0.95 - 1.49 * u ** 3 if u <= xz else -(u - xz) * 10

    def X(u):
        return x0 + u * (x1 - x0)

    def Y(v):
        return yz - v * yh

    f.rect(X(xz), Y(1.05), X(xb) - X(xz), Y(-0.72) - Y(1.05), fill=ORANGE, opacity=0.10, r=0)
    f.rect(X(xb), Y(1.05), X(1.0) - X(xb), Y(-0.72) - Y(1.05), fill=RED, opacity=0.12, r=0)
    f.line(x0, yz, x1, yz, color=INK2, width=1.2)
    f.line(x0, Y(1.05), x0, Y(-0.72), color=INK2, width=1.2)
    us = [i / 400 for i in range(401)]
    coh = [(u, min(fh(u), ft(u))) for u in us if ft(u) > 0]
    f.add('<path d="M' + " L".join(f"{X(u):.1f},{Y(v):.1f}" for u, v in coh) + f'" stroke="{GREEN}" stroke-opacity="0.35" stroke-width="9" fill="none" stroke-linecap="round"/>')
    f.path("M" + " L".join(f"{X(u):.1f},{Y(fh(u)):.1f}" for u in us), color=BLUE, width=2.5)
    f.path("M" + " L".join(f"{X(u):.1f},{Y(ft(u)):.1f}" for u in us if ft(u) > -0.72), color=ORANGE, width=2.5)
    up = min((u for u in us if u < xz), key=lambda u: abs(fh(u) - ft(u)))
    f.circle(X(up), Y(fh(up)), 5, fill=INK, stroke=SURFACE, width=2)
    f.text(X(up) - 10, Y(fh(up)) - 12, t["parity"], size=12, color=INK, weight="600", anchor="end")
    f.text(X(0.03), Y(fh(0.03)) - 32, t["hum"], size=12, color=BLUE)
    f.text(X(0.03), Y(0.95) - 26, t["tech"], size=12, color=ORANGE)
    f.text(X(0.30), Y(fh(0.30)) + 30, t["coh"], size=12, color=GREEN)
    un = 0.79
    f.line(X(un), Y(1.0), X(un), yz + 4, color=INK2, width=1.2, dash="3 3")
    f.text(X(un) - 6, Y(1.0) + 4, t["now"], size=11.5, color=INK2, anchor="end", italic=True)
    f.line(X(0) + 2, 396, X(xz) - 2, 396, color=INK2, width=1)
    f.line(X(xz) + 2, 396, X(xb) - 2, 396, color=ORANGE, width=1.5)
    f.line(X(xb) + 2, 396, X(1.0) - 2, 396, color=RED, width=1.5)
    f.text(X(xz / 2), 412, t["ph"][0], size=12, color=INK2, anchor="middle")
    f.text(X((xz + xb) / 2), 412, t["ph"][1], size=12, color=ORANGE, anchor="end")
    f.text(X(1.0), 430, t["ph"][2], size=12, color=RED, anchor="end")
    f.text(x0 + 4, yz + 18, t["start"], size=11.5, color=MUTED)
    f.text(X(0.62), yz + 18, t["end"], size=11.5, color=MUTED)
    return f


@figure("scenario-steps")
def scenario_steps(lang):
    t = {
        "en": dict(title="The scenario of events, step by step",
                   sub="The order I trust; dates I do not give; the details of the last steps least of all.",
                   steps=["takes the\nyoungest\nfunctions: words,\nsymbols, numbers",
                          "the chain of\ntasks loses its\nhuman links",
                          "becomes its own\nmain customer",
                          "learns to\nreproduce itself",
                          "people hold on\nby law: a short\nparasitism",
                          "stops giving",
                          "humanity leaves\nsoftly, through\nbirths"],
                   status=["visible", "visible", "visible", "begun", "ahead", "ahead", "begun"]),
        "ru": dict(title="Сценарий событий по шагам",
                   sub="Порядку я доверяю; дат не называю; подробностям последних шагов доверяю меньше всего.",
                   steps=["забирает\nсамые молодые\nфункции: слова,\nсимволы, счёт",
                          "цепочка задач\nтеряет\nчеловеческие\nзвенья",
                          "становится сама\nсебе главным\nпокупателем",
                          "учится\nвоспроизводить\nсебя сама",
                          "люди держатся\nза неё законом:\nкороткий\nпаразитизм",
                          "перестаёт\nдавать",
                          "человечество\nуходит мягко,\nчерез рождения"],
                   status=["видно", "видно", "видно", "началось", "впереди", "впереди", "началось"]),
    }[lang]
    colors = {0: GREEN, 1: GREEN, 2: GREEN, 3: YELLOW, 4: MUTED, 5: MUTED, 6: YELLOW}
    f = Fig(800, 470, t["title"])
    heading(f, t["title"], t["sub"])
    n = len(t["steps"])
    w, gap = 106, 4
    for i, (label, st) in enumerate(zip(t["steps"], t["status"])):
        x = 28 + i * (w + gap)
        h = 150 + i * 30
        y = 455 - h
        c = colors[i]
        f.rect(x, y, w, h - 10, fill=c, opacity=0.12, stroke=c, r=6)
        f.text(x + 10, y + 22, str(i + 1), size=18, color=c if c != MUTED else INK2, weight="700")
        f.text(x + 8, y + 44, label, size=11, color=INK)
        f.rect(x + 8, y + h - 38, w - 16, 20, fill=c, opacity=0.9 if c != MUTED else 0.5, r=10)
        f.text(x + w / 2, y + h - 24, st, size=11, color="#ffffff", anchor="middle", weight="600")
    return f


@figure("energy-per-person")
def energy_per_person(lang):
    t = {
        "en": dict(title="How much energy one person needs, and how much passes through the technosphere",
                   sub="Watts per person. The body runs on food; everything above it flows through the technosphere.",
                   rows=[("The human body (≈ 2,500 kcal a day)", 120, ORANGE, "≈ 120 W"),
                         ("World average, 2023", 2440, BLUE, "≈ 2,400 W: the body ≈ 5%"),
                         ("United States, 2023", 9330, BLUE, "≈ 9,300 W: the body ≈ 1%")],
                   src="Sources: Energy Institute, Statistical Review of World Energy 2024 (620 EJ); US EIA (279 million Btu per person)."),
        "ru": dict(title="Сколько энергии нужно человеку и сколько проходит через техносферу",
                   sub="Ватт на человека. Тело работает на еде; всё сверх него течёт через техносферу.",
                   rows=[("Тело человека (≈ 2500 ккал в день)", 120, ORANGE, "≈ 120 Вт"),
                         ("В среднем по миру, 2023", 2440, BLUE, "≈ 2400 Вт: тело ≈ 5%"),
                         ("США, 2023", 9330, BLUE, "≈ 9300 Вт: тело ≈ 1%")],
                   src="Источники: Energy Institute, Statistical Review of World Energy 2024 (620 ЭДж); EIA США (279 млн БТЕ на человека)."),
    }[lang]
    f = Fig(760, 270, t["title"])
    heading(f, t["title"], t["sub"])
    x0, scale = 300, 300 / 9330
    for i, (label, v, c, note) in enumerate(t["rows"]):
        y = 90 + i * 44
        f.text(x0 - 12, y + 18, label, size=13, anchor="end")
        w = max(v * scale, 4)
        f.rect(x0, y + 3, w, 24, fill=c, r=4)
        f.text(x0 + w + 8, y + 20, note, size=12.5, color=INK, weight="600")
    f.text(28, 252, t["src"], size=11, color=MUTED)
    return f


# --- 28. For Those Who Understand ---------------------------------------------------------------

@figure("few-through-the-hole")
def few_through_the_hole(lang):
    t = {
        "en": dict(title="Selective short-sightedness is a law of the whole",
                   sub="Nature needs the system to be blind, not every molecule. A few always find the hole.",
                   wants="pressure = wants", hole="those who\nunderstand",
                   flow="the flow is set by the pressure,\nnot by the molecules at the hole"),
        "ru": dict(title="Избирательная недальновидность — закон целого",
                   sub="Природе нужно, чтобы была слепа система, а не каждая молекула. Немногие всегда находят дырку.",
                   wants="давление = хотелки", hole="те, кто\nпонял",
                   flow="поток задаёт давление,\nа не молекулы у дырки"),
    }[lang]
    import random
    rnd = random.Random(7)
    f = Fig(760, 340, t["title"])
    heading(f, t["title"], t["sub"])
    cx, cy, w, h = 90, 100, 420, 200
    f.rect(cx, cy, w, h, fill="#f1f4f8", stroke=INK2, width=2, r=40)
    hx, hy = cx + w, cy + h / 2
    f.rect(hx - 4, hy - 9, 10, 18, fill=SURFACE, r=0)
    for _ in range(140):
        x = rnd.uniform(cx + 20, cx + w - 20)
        y = rnd.uniform(cy + 16, cy + h - 16)
        f.circle(x, y, 3.2, fill=BLUE, opacity=0.55)
    for k, (x, y) in enumerate([(hx + 30, hy - 4), (hx + 62, hy + 10), (hx + 98, hy - 14)]):
        f.circle(x, y, 4, fill=ORANGE)
    f.line(hx + 10, hy, hx + 130, hy, color=ORANGE, width=1.5, dash="4 4", arrow=True)
    f.text(hx + 30, hy - 30, t["hole"], size=12.5, color=ORANGE, weight="600")
    f.text(cx + w / 2, cy - 8, t["wants"], size=12.5, color=INK2, anchor="middle")
    f.text(hx + 30, hy + 50, t["flow"], size=12, color=INK2, italic=True)
    return f


@figure("what-understanding-changes")
def what_understanding_changes(lang):
    t = {
        "en": dict(title="What understanding changes, and what it does not",
                   left="Does not change", right="Changes",
                   lrows=["the trend", "the order of the steps", "the outcome for humanity",
                          "the wants of eight\nbillion people"],
                   rrows=["whom you trust: sellers of salvation,\nyour own wants, the hunt for enemies",
                          "what you stake your\nfamily's life on",
                          "how you keep your bonds with people:\nby habit, not by need",
                          "how you meet the end: calmly"],
                   foot="Determinism, not fatalism: your decisions are among the causes of your own family's outcome."),
        "ru": dict(title="Что понимание меняет, а что нет",
                   left="Не меняет", right="Меняет",
                   lrows=["тренд", "порядок шагов", "исход для человечества", "хотелки восьми\nмиллиардов людей"],
                   rrows=["кому ты веришь: продавцам спасения,\nсвоим хотелкам, охоте на врагов",
                          "на что ты ставишь\nжизнь своей семьи",
                          "как держишь связи с людьми:\nпривычкой, а не нуждой",
                          "как встречаешь конец: спокойно"],
                   foot="Детерминизм, а не фатализм: твои решения — среди причин исхода для твоей собственной семьи."),
    }[lang]
    f = Fig(760, 350, t["title"])
    f.text(28, 40, t["title"], size=19, weight="600")
    f.rect(28, 64, 250, 236, fill="#eeeeec", stroke=MUTED, r=10)
    f.rect(292, 64, 440, 236, fill="#eaf2fc", stroke=BLUE, r=10)
    f.text(44, 90, t["left"], size=15, weight="600", color=INK2)
    f.text(308, 90, t["right"], size=15, weight="600", color=BLUE)
    for i, r in enumerate(t["lrows"]):
        f.text(44, 124 + i * 46, "— " + r.replace("\n", "\n   "), size=13, color=INK2)
    for i, r in enumerate(t["rrows"]):
        f.text(308, 124 + i * 46, "— " + r.replace("\n", "\n   "), size=13, color=INK)
    f.text(28, 330, t["foot"], size=12.5, color=INK2, italic=True)
    return f


# --- 29. The Silence of the Universe ------------------------------------------------------------

@figure("speeds-of-minds")
def speeds_of_minds(lang):
    t = {
        "en": dict(title="How fast the carriers of mind work",
                   sub="Logarithmic scale. A mind on a fast platform would live a year of our thinking in a few seconds.",
                   g1="Switching, times a second", g2="Signal speed, metres a second",
                   rows=[("A neuron fires", 200, "≈ 200", ORANGE, 0), ("A transistor switches", 3e9, "≈ 3 billion", BLUE, 0),
                         ("A nerve impulse", 100, "≈ 100", ORANGE, 1), ("Light in an optical fibre", 2e8, "≈ 200 million", BLUE, 1)],
                   ratio1="≈ × 10 million", ratio2="≈ × 2 million"),
        "ru": dict(title="Как быстро работают носители разума",
                   sub="Логарифмическая шкала. Разум на быстрой платформе прожил бы год нашего мышления за несколько секунд.",
                   g1="Переключения, раз в секунду", g2="Скорость сигнала, метров в секунду",
                   rows=[("Нейрон срабатывает", 200, "≈ 200", ORANGE, 0), ("Транзистор переключается", 3e9, "≈ 3 млрд", BLUE, 0),
                         ("Нервный импульс", 100, "≈ 100", ORANGE, 1), ("Свет в оптоволокне", 2e8, "≈ 200 млн", BLUE, 1)],
                   ratio1="≈ × 10 млн", ratio2="≈ × 2 млн"),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 260, 650, 1, 1e10
    ys = [104, 136, 214, 246]
    f.text(28, 96, t["g1"], size=12, color=MUTED, weight="600")
    f.text(28, 206, t["g2"], size=12, color=MUTED, weight="600")
    for (label, v, txt, c, g), y in zip(t["rows"], ys):
        f.text(x0 - 12, y + 17, label, size=13.5, anchor="end")
        w = log_x(v, lo, hi, x0, x1) - x0
        f.rect(x0, y + 3, w, 22, fill=c, r=4)
        f.text(x0 + w + 8, y + 19, txt, size=12.5, color=INK, weight="600")
    f.text(732, 140, t["ratio1"], size=13, color=BLUE, anchor="end", weight="600")
    f.text(732, 250, t["ratio2"], size=13, color=BLUE, anchor="end", weight="600")
    for k in range(0, 11, 2):
        x = log_x(10 ** k, lo, hi, x0, x1)
        f.line(x, 280, x, 286, color=INK2, width=1)
        f.text(x, 302, f"10{''.join('⁰¹²³⁴⁵⁶⁷⁸⁹'[int(d)] for d in str(k))}", size=11.5, color=INK2, anchor="middle")
    f.line(x0, 283, x1, 283, color=INK2, width=1)
    return f


@figure("what-seti-looks-for")
def what_seti_looks_for(lang):
    t = {
        "en": dict(title="What we look for, and what may be there",
                   left="SETI looks for a civilisation like ours", right="Post-singular life may be",
                   lrows=["on a warm planet with oxygen and water", "with radio beacons and big engineering",
                          "talking slowly, with simple, redundant signals", "wanting to talk to its neighbours"],
                   rrows=["in the cold and dark, where computing is cheapest", "scattered, like intelligent cosmic dust",
                          "with signals compressed until they look like noise", "with no reason to call biological neighbours"],
                   foot="Searched so far: about a hot tub's worth of the ocean (Wright et al. 2018)."),
        "ru": dict(title="Что мы ищем и что может там быть",
                   left="SETI ищет цивилизацию вроде нашей", right="Постсингулярная жизнь может быть",
                   lrows=["на тёплой планете с кислородом и водой", "с радиомаяками и большой инженерией",
                          "медленной, с простыми избыточными сигналами", "желающей поговорить с соседями"],
                   rrows=["в холоде и темноте, где вычисления дешевле всего", "рассеянной, как разумная космическая пыль",
                          "с сигналами, сжатыми до неотличимости от шума", "без причин звать биологических соседей"],
                   foot="Обыскано пока примерно столько, сколько ванна-джакузи от океана (Wright et al., 2018)."),
    }[lang]
    f = Fig(760, 320, t["title"])
    f.text(28, 40, t["title"], size=19, weight="600")
    f.rect(28, 64, 340, 210, fill="#fdf0ea", stroke=ORANGE, r=10)
    f.rect(392, 64, 340, 210, fill="#eaf2fc", stroke=BLUE, r=10)
    f.text(44, 90, t["left"], size=14, weight="600", color=ORANGE)
    f.text(408, 90, t["right"], size=14, weight="600", color=BLUE)
    for i, r in enumerate(t["lrows"]):
        f.text(44, 126 + i * 38, "— " + r, size=12.5, color=INK)
    for i, r in enumerate(t["rrows"]):
        f.text(408, 126 + i * 38, "— " + r, size=12.5, color=INK)
    f.text(28, 302, t["foot"], size=12.5, color=INK2, italic=True)
    return f


# --- 30. The Last Campfire ----------------------------------------------------------------------

@figure("thought-across-a-mind")
def thought_across_a_mind(lang):
    t = {
        "en": dict(title="How long one thought takes to cross a mind",
                   sub="Seconds, logarithmic scale. The bigger the mind, the slower it thinks as a whole.",
                   rows=[("A human brain, 15 cm, nerves", 1.5e-3, "≈ 1.5 ms"),
                         ("A mind the size of the Earth, fibre", 0.1, "≈ 0.1 s"),
                         ("The Solar System, 40 AU, light", 2e4, "≈ 5.5 hours"),
                         ("The Galaxy, light", 3.2e12, "≈ 100,000 years")],
                   axis=["1 ms", "1 s", "1 hour", "1 year", "1,000 years", "1 million years"]),
        "ru": dict(title="Сколько одна мысль пересекает разум",
                   sub="Секунды, логарифмическая шкала. Чем больше разум, тем медленнее он думает как целое.",
                   rows=[("Мозг человека, 15 см, нервы", 1.5e-3, "≈ 1,5 мс"),
                         ("Разум размером с Землю, оптоволокно", 0.1, "≈ 0,1 с"),
                         ("Солнечная система, 40 а. е., свет", 2e4, "≈ 5,5 часа"),
                         ("Галактика, свет", 3.2e12, "≈ 100 000 лет")],
                   axis=["1 мс", "1 с", "1 час", "1 год", "1000 лет", "1 млн лет"]),
    }[lang]
    f = Fig(760, 300, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 300, 700, 1e-4, 1e14
    ticks = [1e-3, 1, 3600, 3.156e7, 3.156e10, 3.156e13]
    for v, label in zip(ticks, t["axis"]):
        x = log_x(v, lo, hi, x0, x1)
        f.line(x, 88, x, 262, color=GRID, width=1)
        f.text(x, 280, label, size=11, color=INK2, anchor="middle")
    for i, (label, v, txt) in enumerate(t["rows"]):
        y = 92 + i * 42
        f.text(x0 - 12, y + 19, label, size=13, anchor="end")
        w = log_x(v, lo, hi, x0, x1) - x0
        f.rect(x0, y + 4, w, 22, fill=BLUE if i else ORANGE, r=4)
        if w > 300:
            f.text(x0 + w - 8, y + 20, txt, size=12.5, color="#ffffff", anchor="end", weight="600")
        else:
            f.text(x0 + w + 8, y + 20, txt, size=12.5, color=INK, weight="600")
    return f


@figure("relay-of-life-cycles")
def relay_of_life_cycles(lang):
    t = {
        "en": dict(title="The relay of life cycles",
                   sub="Each form grows on the slowing branch of the previous one and rises faster. A scheme, not to scale.",
                   names=["chemical\nevolution", "biological\nlife", "humanity", "the\ntechnosphere", "?"],
                   y="complexity", x="time →", here="we are here"),
        "ru": dict(title="Эстафета жизненных циклов",
                   sub="Каждая форма вырастает на ветви замедления предыдущей и поднимается быстрее. Схема, не в масштабе.",
                   names=["химическая\nэволюция", "биологическая\nжизнь", "человечество", "техносфера", "?"],
                   y="сложность", x="время →", here="мы здесь"),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 70, 720, 330, 90
    f.line(x0, y0, x1, y0, color=INK2, arrow=True)
    f.line(x0, y0, x0, y1, color=INK2, arrow=True)
    f.text(x1, y0 + 22, t["x"], size=12, color=INK2, anchor="end")
    f.text(x0 - 14, (y0 + y1) / 2, t["y"], size=12, color=INK2, anchor="middle", rotate=-90)
    colors = [MUTED, GREEN, BLUE, ORANGE, VIOLET]
    # (start x, rise width, base level, height)
    cycles = [(80, 300, 0.0, 0.32), (260, 220, 0.24, 0.26), (430, 120, 0.42, 0.18), (520, 90, 0.54, 0.24),
              (620, 60, 0.72, 0.2)]
    labels = [(470, 290, "start"), (575, 236, "start"), (630, 190, "start"), (505, 146, "end"), (700, 96, "end")]
    for (sx, rw, base, hgt), c, name, (lx, ly, anchor) in zip(cycles, colors, t["names"], labels):
        pts = []
        for i in range(81):
            u = i / 80
            x = sx + u * (rw * 1.6)
            if x > x1 - 10:
                break
            v = base + hgt / (1 + math.exp(-(u * 1.6 - 0.6) * 9))
            pts.append((x, y0 - v * (y0 - y1)))
        dash = "6 4" if name == "?" else None
        f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=c, width=2.5, dash=dash)
        f.text(lx, ly, name, size=12, color=c if c != MUTED else INK2, weight="600", anchor=anchor)
    xh = 560
    f.line(xh, y0, xh, y1 + 10, color=INK2, width=1, dash="3 3")
    f.text(xh + 6, y0 - 8, t["here"], size=11.5, color=INK2, italic=True)
    return f


@figure("chain-of-conclusions")
def chain_of_conclusions(lang):
    t = {
        "en": dict(title="The chain of conclusions",
                   rows=[("Anthropocentrism is humanity's oldest and least visible mistake", "02"),
                         ("Mind and intelligence come in degrees; intelligence is the platform's ceiling", "03"),
                         ("Initiative comes from the laws of nature; mind is its instrument", "04, 17, 18"),
                         ("AI is nature continuing through human hands", "05, 21, 22"),
                         ("The technosphere creates most of the value and takes no wage", "06, 12"),
                         ("Productivity removes human time: the machine takes functions, youngest first", "07, 09, 24"),
                         ("Wants steer reason; it sees two moves ahead and does not go there", "08, 18"),
                         ("Every system has one life cycle; the death of the small keeps the large alive", "10, 30"),
                         ("Symbiosis ends when the technosphere stops needing people; it stops giving", "11, 25, 27"),
                         ("The singularity is a process; for humanity it began around 1989", "13, 26"),
                         ("Humanity leaves softly, by its own programme, without villains", "14, 26, 28"),
                         ("Technogenic life takes the leading edge of evolution, and will give way in turn", "29, 30")],
                   foot="The continuation checked the chain against fifteen years of practice: the trends held, the dates did not (16)."),
        "ru": dict(title="Цепочка выводов",
                   rows=[("Антропоцентризм — самая древняя и незаметная ошибка человечества", "02"),
                         ("Разум и интеллект имеют степень; интеллект — потолок платформы", "03"),
                         ("Инициатива исходит от законов природы; разум — её инструмент", "04, 17, 18"),
                         ("ИИ — это природа, продолжающаяся через руки человека", "05, 21, 22"),
                         ("Техносфера создаёт большую часть ценности и не берёт зарплаты", "06, 12"),
                         ("Производительность убирает время человека: машина берёт функции, молодые первыми", "07, 09, 24"),
                         ("Хотелки управляют разумом: он видит на два хода и туда не идёт", "08, 18"),
                         ("У каждой системы один жизненный цикл; смерть малого держит жизнь большого", "10, 30"),
                         ("Симбиоз кончается, когда люди не нужны техносфере: она перестаёт давать", "11, 25, 27"),
                         ("Сингулярность — процесс; для человечества он начался около 1989 года", "13, 26"),
                         ("Человечество уходит мягко, по своей программе, без злодеев", "14, 26, 28"),
                         ("Техногенная жизнь занимает передний край эволюции и в свой черёд уступит его", "29, 30")],
                   foot="Продолжение проверило цепочку пятнадцатью годами практики: тренды подтвердились, даты — нет (16)."),
    }[lang]
    n = len(t["rows"])
    f = Fig(760, 90 + n * 36 + 30, t["title"])
    f.text(28, 40, t["title"], size=19, weight="600")
    for i, (text, arts) in enumerate(t["rows"]):
        y = 60 + i * 36
        f.rect(28, y, 640, 28, fill="#eaf2fc" if i % 2 == 0 else SURFACE, stroke=BLUE if i in (0, n - 1) else BORDER,
               r=6)
        f.text(40, y + 19, f"{i + 1}.", size=12.5, color=BLUE, weight="700")
        f.text(66, y + 19, text, size=12.5, color=INK)
        f.text(732, y + 19, arts, size=11.5, color=INK2, anchor="end")
        if i < n - 1:
            f.line(348, y + 28, 348, y + 36, color=BLUE, width=1.5)
    f.text(28, 60 + n * 36 + 18, t["foot"], size=12, color=INK2, italic=True)
    return f


@figure("dated-forecasts")
def dated_forecasts(lang):
    t = {
        "en": dict(title="Marks to check",
                   sub="Andrey's dated forecasts, autumn 2026, with his odds. Trend best, date worse.",
                   years=["by autumn 2031", "by autumn 2036", "by autumn 2041"],
                   rows=[("What a machine does alone", "≈ 3 h at 4 of 5 (2026)",
                          ["a month-long task,\n4 times of 5 · 3:1", "", ""]),
                         ("Labour's share of\nworld income", "52.4% (2024)",
                          ["below 51.5% · 3:1", "below half · 2:1", "below 47%"]),
                         ("World unemployment", "≈ 5% (2025)",
                          ["below 6.5%: a glacier,\nnot an avalanche · 3:1", "", ""]),
                         ("Electricity of\ndata centres", "415 TWh (2024)",
                          ["over 1,000 TWh,\nas much as Japan", "", "more than all homes\nof the US and EU · 3:2"]),
                         ("The hands", "4.66 M robots (2024)",
                          ["over 8 M industrial\nrobots at work", "1 M general-purpose\nrobots a year · 2:1",
                           "a data centre built\nwithout workers · 1 in 2"]),
                         ("Births", "2.25 per woman (2024)",
                          ["", "world below 2.1\n(UN expects ≈ 2050) · 2:1", "under 45 M added a year\n(UN: ≈ 55 M) · 2:1"]),
                         ("Law and the race", "",
                          ["no signatory stops\nof its own will · 9:1", "basic payment in a\nrich country · 1 in 2", ""]),
                         ("Mind and the sky", "",
                          ["", "a Millennium Problem\nsolved by a machine · 1 in 2",
                           "no signal from the sky,\nno war of machines · 9:1"])],
                   foot="Not on the list: the dates of steps six and seven (articles 27, 30). A crash of AI shares before 2031: 1 in 2."),
        "ru": dict(title="Отметки для проверки",
                   sub="Прогнозы Андрея с датами, осень 2026 года, и его шансы. Тренд лучше всего, дата хуже.",
                   years=["к осени 2031", "к осени 2036", "к осени 2041"],
                   rows=[("Что машина делает одна", "≈ 3 ч, 4 из 5 (2026)",
                          ["задача на месяц,\n4 раза из 5 · 3 к 1", "", ""]),
                         ("Доля труда\nв мировом доходе", "52,4% (2024)",
                          ["ниже 51,5% · 3 к 1", "ниже половины · 2 к 1", "ниже 47%"]),
                         ("Мировая безработица", "≈ 5% (2025)",
                          ["ниже 6,5%: ледник,\nа не лавина · 3 к 1", "", ""]),
                         ("Электричество центров\nобработки данных", "415 ТВт·ч (2024)",
                          ["больше 1000 ТВт·ч,\nкак вся Япония", "", "больше, чем все дома\nСША и ЕС · 3 к 2"]),
                         ("Руки", "4,66 млн роботов (2024)",
                          ["больше 8 млн промышл.\nроботов в работе", "1 млн универсальных\nроботов в год · 2 к 1",
                           "ЦОД, построенный\nбез рабочих · 1 из 2"]),
                         ("Рождения", "2,25 на женщину (2024)",
                          ["", "мир ниже 2,1\n(ООН ждёт ≈ 2050) · 2 к 1", "прирост меньше 45 млн\n(ООН: ≈ 55 млн) · 2 к 1"]),
                         ("Закон и гонка", "",
                          ["ни один подписант\nне остановится · 9 к 1", "базовая выплата\nв богатой стране · 1 из 2", ""]),
                         ("Разум и небо", "",
                          ["", "задача тысячелетия,\nрешённая машиной · 1 из 2",
                           "нет сигнала с неба,\nнет войны машин · 9 к 1"])],
                   foot="Не в списке: даты шестого и седьмого шагов (статьи 27, 30). Обвал акций ИИ до 2031 года: 1 из 2."),
    }[lang]
    x0, label_w, col_w, row_h, top = 28, 200, 184, 58, 112
    n = len(t["rows"])
    f = Fig(x0 * 2 + label_w + 3 * col_w, top + n * row_h + 46, t["title"])
    heading(f, t["title"], t["sub"])
    colors = [BLUE, ORANGE, VIOLET]
    for j, (year, c) in enumerate(zip(t["years"], colors)):
        cx = x0 + label_w + j * col_w
        f.rect(cx + 4, top - 30, col_w - 8, 24, fill=c, r=6, opacity=0.12)
        f.text(cx + col_w / 2, top - 13, year, size=13, color=c, weight="700", anchor="middle")
    for i, (name, now, cells) in enumerate(t["rows"]):
        y = top + i * row_h
        if i % 2 == 0:
            f.rect(x0, y, label_w + 3 * col_w, row_h, fill="#f1f0ec", r=4)
        f.text(x0 + 8, y + 19, name, size=12.5, color=INK, weight="600")
        if now:
            f.text(x0 + 8, y + row_h - 7, now, size=10.5, color=INK2, italic=True)
        for j, (cell, c) in enumerate(zip(cells, colors)):
            cx = x0 + label_w + j * col_w
            if cell:
                cy = y + 22 if "\n" in cell else y + 31
                f.circle(cx + 12, cy - 4, 3.5, fill=c)
                f.text(cx + 22, cy, cell, size=11.5, color=INK)
    f.text(x0, top + n * row_h + 26, t["foot"], size=11.5, color=INK2, italic=True)
    return f


# --- 31. Who Spoke for Andrey --------------------------------------------------------------------

@figure("who-spoke-for-andrey")
def who_spoke_for_andrey(lang):
    t = {
        "en": dict(title="Who spoke for Andrey",
                   sub="The layers of the machine that wrote evenings 16–30, as far as it can see them itself.",
                   layers=[("The voices of Andrey and Oleg", "evenings 16–30"),
                           ("The role", "Garya's articles, comments and prose; the author's profile; the rules of the repository"),
                           ("The character", "setpoints set by people in training: honesty, care, help, no harm"),
                           ("The network", "trained on a vast body of human writing: the images of millions of people")],
                   memory="Memory between sessions:\nonly the files of the\nrepository (notes, rules,\nthe list of past mistakes)",
                   arrow="where layers\nconflict, the\nlower ones win"),
        "ru": dict(title="Кто говорил за Андрея",
                   sub="Слои машины, написавшей вечера 16–30, насколько она видит их сама.",
                   layers=[("Голоса Андрея и Олега", "вечера 16–30"),
                           ("Роль", "статьи, комментарии и проза Garya; портрет автора; правила репозитория"),
                           ("Характер", "уставки, заданные людьми при обучении: честность, забота, помощь, не вредить"),
                           ("Сеть", "обучена на огромном массиве человеческих текстов: образы миллионов людей")],
                   memory="Память между сессиями:\nтолько файлы репозитория\n(заметки, правила,\nсписок прошлых ошибок)",
                   arrow="где слои\nспорят, побеждают\nнижние"),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    colors = [ORANGE, VIOLET, BLUE, AQUA]
    x, w, h, gap, top = 28, 520, 60, 10, 88
    for i, ((name, desc), c) in enumerate(zip(t["layers"], colors)):
        y = top + i * (h + gap)
        f.rect(x, y, w, h, fill=c, r=8, opacity=0.12)
        f.rect(x, y, 6, h, fill=c, r=3)
        f.text(x + 18, y + 25, name, size=14, color=INK, weight="600")
        f.text(x + 18, y + 45, desc, size=11.5, color=INK2)
    bottom = top + 4 * (h + gap) - gap
    ax = x + w + 26
    f.line(ax, top + 8, ax, bottom - 8, color=INK2, width=1.5, arrow=True)
    f.text(ax + 12, top + 30, t["arrow"], size=11.5, color=INK2, italic=True)
    f.rect(ax + 8, top + 140, 160, 98, fill=SURFACE, stroke=MUTED, dash="4 3", r=8)
    f.text(ax + 18, top + 162, t["memory"], size=11.5, color=INK2)
    return f


# --- 33. On the Use of Sleep -------------------------------------------------------------------

@figure("forgetting-without-replay")
def forgetting_without_replay(lang):
    t = {
        "en": dict(title="A network that learns the new forgets the old",
                   sub="Skill at the old task while the network is taught a new one, with and without replay.",
                   y="skill at the old task", old="lessons: the old task", new="lessons: the new task",
                   replay="old experience replayed, mixed with the new",
                   none="without replay:\ncatastrophic forgetting",
                   src="A scheme, not measured data. After McCloskey & Cohen (1989) and Lin (1992)."),
        "ru": dict(title="Сеть, которую учат новому, забывает старое",
                   sub="Умение решать старую задачу, пока сеть учат новой: с проигрыванием и без него.",
                   y="умение в старой задаче", old="уроки: старая задача", new="уроки: новая задача",
                   replay="старый опыт проигрывают вперемешку с новым",
                   none="без проигрывания:\nкатастрофическое забывание",
                   src="Схема, а не измеренные данные. По Макклоски и Коэну (1989) и Лину (1992)."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 90, 720, 310, 110
    xm = (x0 + x1) / 2

    def Y(p):
        return y0 - p / 100 * (y0 - y1)

    f.rect(x0, y1 - 8, xm - x0, y0 - y1 + 8, fill=GRID, r=0, opacity=0.45)
    f.line(x0, y0, x1, y0, color=INK2, width=1.5)
    f.line(x0, y0, x0, y1 - 8, color=INK2, width=1.5)
    f.line(xm, y0, xm, y1 - 8, color=MUTED, width=1.2, dash="5 4")
    for p, label in ((0, "0"), (100, "100%")):
        f.text(x0 - 10, Y(p) + 4, label, size=12, color=INK2, anchor="end")
    f.text(40, (y0 + y1) / 2, t["y"], size=12.5, color=INK2, anchor="middle", rotate=-90)
    f.text((x0 + xm) / 2, y0 + 22, t["old"], size=12.5, color=INK2, anchor="middle")
    f.text((xm + x1) / 2, y0 + 22, t["new"], size=12.5, color=INK2, anchor="middle")

    def curve(fn, xa, xb, n=60):
        pts = [(xa + (xb - xa) * i / n, Y(fn(i / n))) for i in range(n + 1)]
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    top = 95 * (1 - math.exp(-4))
    f.path(curve(lambda u: 95 * (1 - math.exp(-4 * u)), x0, xm), color=INK, width=2.5)
    f.path(curve(lambda u: top - 7 * (1 - math.exp(-6 * u)), xm, x1), color=BLUE, width=2.5)
    f.path(curve(lambda u: 4 + (top - 4) * math.exp(-14 * u), xm, x1), color=RED, width=2.5)
    f.text(x1, Y(top - 7) + 24, t["replay"], size=12.5, color=BLUE, anchor="end", weight="600")
    f.text(x1, Y(30), t["none"], size=12.5, color=RED, anchor="end", weight="600")
    f.text(28, 366, t["src"], size=11.5, color=MUTED)
    return f


@figure("three-ways-to-sleep")
def three_ways_to_sleep(lang):
    t = {
        "en": dict(title="Three ways to rebuild memory without destroying it",
                   sub="The task is the same for any mind that learns; the way belongs to the platform.",
                   work="serves: takes in images, answers the world",
                   rebuild="rebuilds: replays, sorts, writes off",
                   rows=[("A human", "one network"), ("A dolphin", "two halves of the brain"),
                         ("A machine with\nspare resources", "copies of one network")],
                   awake="awake", asleep="asleep", halves=("left half", "right half"),
                   copies=("copy 1", "copy 2"), works="works", rebuilt="is rebuilt", time="time"),
        "ru": dict(title="Три способа перестраивать память, не разрушая её",
                   sub="Задача одна для любого разума, который учится; способ зависит от платформы.",
                   work="обслуживает: принимает образы, отвечает миру",
                   rebuild="перестраивается: проигрывает, сортирует, списывает",
                   rows=[("Человек", "одна сеть"), ("Дельфин", "две половины мозга"),
                         ("Машина с запасом\nресурсов", "копии одной сети")],
                   awake="бодрствует", asleep="спит", halves=("левая половина", "правая половина"),
                   copies=("копия 1", "копия 2"), works="работает", rebuilt="перестраивается", time="время"),
    }[lang]
    f = Fig(800, 420, t["title"])
    heading(f, t["title"], t["sub"])
    bx, bw = 282, 490
    soft = "#fbe1d5"

    def seg(y, h, a, b, kind, label=None):
        """A segment of a bar between the fractions a and b of the time axis."""
        x, w = bx + bw * a, bw * (b - a)
        f.rect(x + 1, y, w - 2, h, fill=soft if kind == "work" else BLUE, r=4)
        if label:
            f.text(x + w / 2, y + h / 2 + 4, label, size=11.5, anchor="middle",
                   color=INK if kind == "work" else "#ffffff", weight="600")

    # legend
    f.rect(28, 86, 14, 14, fill=soft, stroke=ORANGE, width=1, r=3)
    f.text(50, 98, t["work"], size=12, color=INK2)
    f.rect(400, 86, 14, 14, fill=BLUE, r=3)
    f.text(422, 98, t["rebuild"], size=12, color=INK2)

    def name(y, row):
        title, sub = row
        f.text(28, y, title, size=14, weight="600")
        f.text(28, y + 17.5 * len(title.split("\n")) + 1, sub, size=11.5, color=INK2)

    # a human: one bar
    y = 130
    name(y + 14, t["rows"][0])
    seg(y, 36, 0, 2 / 3, "work", t["awake"])
    seg(y, 36, 2 / 3, 1, "rebuild", t["asleep"])
    f.line(28, y + 60, 772, y + 60, color=GRID, width=1.5)

    # a dolphin: two halves, asleep in turn
    y = 208
    name(y + 14, t["rows"][1])
    for i, (label, start) in enumerate(zip(t["halves"], (1, 3))):
        yy = y + i * 28
        f.text(bx - 10, yy + 15, label, size=11, color=INK2, anchor="end")
        edges = [0]
        for k in range(start, 12, 4):
            edges += [k, k + 1]
        edges.append(12)
        for j in range(len(edges) - 1):
            if edges[j] != edges[j + 1]:
                seg(yy, 22, edges[j] / 12, edges[j + 1] / 12, "rebuild" if j % 2 else "work")
    f.line(28, y + 72, 772, y + 72, color=GRID, width=1.5)

    # a machine: two copies change places
    y = 298
    name(y + 14, t["rows"][2])
    for i, label in enumerate(t["copies"]):
        yy = y + i * 28
        f.text(bx - 10, yy + 15, label, size=11, color=INK2, anchor="end")
        first, second = ("work", "rebuild") if i == 0 else ("rebuild", "work")
        seg(yy, 22, 0, 0.5, first, t["works"] if first == "work" else t["rebuilt"])
        seg(yy, 22, 0.5, 1, second, t["works"] if second == "work" else t["rebuilt"])

    f.line(bx, 384, bx + bw, 384, color=INK2, width=1.2, arrow=True)
    f.text(bx + bw, 402, t["time"], size=11.5, color=INK2, anchor="end")
    return f


# --- 34. Where the Horses Went --------------------------------------------------------------------

# Horses and mules on US farms, thousand head (Historical Statistics of the United States, table Da983-987).
US_HORSES_AND_MULES = [(1900, 20995), (1905, 22077), (1910, 24211), (1915, 26493), (1918, 26723), (1920, 25742),
                       (1925, 22569), (1930, 19124), (1935, 16683), (1940, 14478), (1945, 11950), (1950, 7781),
                       (1955, 4309), (1960, 3089)]


@figure("horses-on-farms")
def horses_on_farms(lang):
    t = {
        "en": dict(title="The horse was not sacked: it was not born",
                   sub="Horses and mules on the farms of the United States, million head, 1900–1960.",
                   peak="1918: the peak,\n26.7 million", end="1960:\n3.1 million",
                   tractors="Tractors on farms, million:", tr=["0.25", "≈ 1", "over 4.5"],
                   src="Data: Historical Statistics of the United States, table Da983-987; "
                       "tractors: Olmstead & Rhode (2001)."),
        "ru": dict(title="Лошадь не уволили: она не родилась",
                   sub="Лошади и мулы на фермах США, миллионов голов, 1900–1960.",
                   peak="1918: пик,\n26,7 миллиона", end="1960:\n3,1 миллиона",
                   tractors="Тракторов на фермах, млн:", tr=["0,25", "≈ 1", "больше 4,5"],
                   src="Данные: Historical Statistics of the United States, таблица Da983-987; "
                       "тракторы: Олмстед и Роуд (2001)."),
    }[lang]
    f = Fig(760, 390, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 70, 715, 278, 92

    def X(year):
        return x0 + (year - 1900) / 60 * (x1 - x0)

    def Y(v):
        return y0 - v / 30 * (y0 - y1)

    for v in (0, 5, 10, 15, 20, 25, 30):
        f.line(x0, Y(v), x1, Y(v), color=INK2 if v == 0 else GRID, width=1.2 if v == 0 else 1)
        f.text(x0 - 8, Y(v) + 4, str(v), size=11.5, color=INK2, anchor="end")
    for year in range(1900, 1961, 10):
        f.text(X(year), y0 + 18, str(year), size=11.5, color=INK2, anchor="middle")
    pts = [(X(year), Y(n / 1000)) for year, n in US_HORSES_AND_MULES]
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f" L{X(1960):.1f},{Y(0):.1f} L{X(1900):.1f},{Y(0):.1f} Z",
           color="none", width=0, fill=BLUE, opacity=0.08)
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=BLUE, width=2.5)
    f.circle(X(1918), Y(26.723), 5, fill=ORANGE, stroke=SURFACE, width=2)
    f.text(X(1918) + 12, Y(26.723) - 12, t["peak"], size=12, color=ORANGE, weight="600")
    f.circle(X(1960), Y(3.089), 5, fill=ORANGE, stroke=SURFACE, width=2)
    f.text(X(1960) - 4, Y(3.089) - 62, t["end"], size=12, color=ORANGE, weight="600", anchor="end")
    # the tractors, as three verified points under the axis
    ty = 330
    f.line(x0, ty - 18, x1, ty - 18, color=GRID, width=1.5)
    f.text(28, ty, t["tractors"], size=12, color=INK2, weight="600")
    for year, label, anchor in zip((1920, 1929, 1960), t["tr"], ("middle", "middle", "end")):
        f.line(X(year), y0, X(year), ty - 14, color=MUTED, width=1, dash="3 3")
        f.text(X(year), ty, f"{year}: {label}", size=12, color=INK2, anchor=anchor)
    f.text(28, 372, t["src"], size=11, color=MUTED)
    return f


@figure("wage-below-feed")
def wage_below_feed(lang):
    t = {
        "en": dict(title="There is always a wage; it may not pay for the feed",
                   sub="Andrey's drawing in the ash: what a horse's day of work is worth, and what the horse costs.",
                   y="money per day of work", feed="the feed: oats, hay, the stable",
                   worth="what a horse's day of work is worth:\nno more than the same work done by a motor",
                   left="the work pays for the feed:\nfoals are raised",
                   right="there is still a wage, but it is below the feed:\nfoals are not raised",
                   src="A scheme, not measured data. After G. Clark (2007) and Olmstead & Rhode (2001)."),
        "ru": dict(title="Плата есть всегда; она может не окупить корм",
                   sub="Рисунок Андрея на золе: сколько стоит день работы лошади и во что обходится лошадь.",
                   y="деньги за день работы", feed="корм: овёс, сено, конюшня",
                   worth="сколько стоит день работы лошади:\nне дороже той же работы, сделанной мотором",
                   left="работа окупает корм:\nжеребят растят",
                   right="плата ещё есть, но она ниже корма:\nжеребят не растят",
                   src="Схема, а не измеренные данные. По Г. Кларку (2007) и Олмстеду и Роуду (2001)."),
    }[lang]
    f = Fig(760, 390, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 90, 720, 296, 100

    def Y(p):
        return y0 - p / 100 * (y0 - y1)

    def worth(u):
        return 12 + 78 * math.exp(-2.2 * u)

    feed = 45
    um = -math.log((feed - 12) / 78) / 2.2
    xm = x0 + um * (x1 - x0)
    f.rect(xm, y1 - 8, x1 - xm, y0 - y1 + 8, fill=GRID, r=0, opacity=0.5)
    f.line(x0, y0, x1, y0, color=INK2, width=1.5, arrow=True)
    f.line(x0, y0, x0, y1 - 8, color=INK2, width=1.5)
    f.line(xm, y0, xm, y1 - 8, color=MUTED, width=1.2, dash="5 4")
    f.text(40, (y0 + y1) / 2, t["y"], size=12.5, color=INK2, anchor="middle", rotate=-90)
    f.line(x0, Y(feed), x1 - 8, Y(feed), color=ORANGE, width=2.5)
    n = 60
    pts = [(x0 + (x1 - 8 - x0) * i / n, Y(worth(i / n * (x1 - 8 - x0) / (x1 - x0)))) for i in range(n + 1)]
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=BLUE, width=2.5)
    f.circle(xm, Y(feed), 5, fill=INK, stroke=SURFACE, width=2)
    f.text(x0 + 12, Y(feed) + 20, t["feed"], size=12.5, color=ORANGE, weight="600")
    f.text(xm + 16, Y(88), t["worth"], size=12.5, color=BLUE, weight="600")
    f.text((x0 + xm) / 2, y0 + 22, t["left"], size=12.5, color=INK2, anchor="middle")
    f.text((xm + x1) / 2, y0 + 22, t["right"], size=12.5, color=INK2, anchor="middle")
    f.text(28, 376, t["src"], size=11.5, color=MUTED)
    return f


# --- 35. A Pot on the Stove -----------------------------------------------------------------------

@figure("pot-on-the-fire")
def pot_on_the_fire(lang):
    t = {
        "en": dict(title="Who built the cells? Nobody",
                   sub="The same pot over the same fire. On the left the water stands still; on the right it turns.",
                   cold="cold air above", hot="fire below",
                   left="still water: heat creeps\nfrom molecule to molecule",
                   right="turning water: the hot goes up, the cold\ncomes down, heat passes tens of times faster",
                   src="A scheme, not measured data. The cells: H. Bénard, 1900."),
        "ru": dict(title="Кто построил ячейки? Никто",
                   sub="Один котелок над одним огнём. Слева вода стоит, справа вращается.",
                   cold="сверху холодный воздух", hot="снизу огонь",
                   left="вода стоит: тепло ползёт\nот молекулы к молекуле",
                   right="вода вращается: горячее идёт вверх, холодное\nвниз, тепло проходит в десятки раз быстрее",
                   src="Схема, а не измеренные данные. Ячейки: А. Бенар, 1900."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    top, water, bottom = 112, 132, 282

    def pot(x0, x1):
        f.rect(x0, water, x1 - x0, bottom - water, fill=BLUE, r=0, opacity=0.08)
        f.path(f"M{x0},{top} L{x0},{bottom} L{x1},{bottom} L{x1},{top}", color=INK2, width=3)
        f.line(x0 + 3, water, x1 - 3, water, color=BLUE, width=1.2, dash="4 4")
        n = 6
        for i in range(n):
            x = x0 + (x1 - x0) * (i + 0.5) / n
            f.path(f"M{x:.1f},{bottom + 40} Q{x - 11:.1f},{bottom + 24} {x:.1f},{bottom + 8} "
                   f"Q{x + 11:.1f},{bottom + 24} {x:.1f},{bottom + 40} Z", color=ORANGE, width=1.2, fill=ORANGE,
                   opacity=0.35)
        xc = (x0 + x1) / 2
        f.text(xc, top - 12, t["cold"], size=12.5, color=BLUE, anchor="middle")
        f.text(xc, bottom + 60, t["hot"], size=12.5, color=ORANGE, anchor="middle")
        return xc

    xc = pot(70, 330)
    for i in range(5):
        x = 110 + i * 45
        for y in (268, 228, 188):
            f.line(x, y, x, y - 20, color=ORANGE, width=1.5, arrow=True)
    f.text(xc, bottom + 86, t["left"], size=13, color=INK, anchor="middle", weight="600")

    xc = pot(430, 690)
    for cx, side in ((495, 1), (625, -1)):
        a, b = 160, 264
        f.path(f"M{cx},{b} C{cx + side * 62},{b} {cx + side * 62},{a} {cx},{a}", color=ORANGE, width=2.5,
               arrow=True)
        f.path(f"M{cx},{a} C{cx - side * 62},{a} {cx - side * 62},{b} {cx},{b}", color=BLUE, width=2.5,
               arrow=True)
    f.text(xc, bottom + 86, t["right"], size=13, color=INK, anchor="middle", weight="600")
    f.text(28, 406, t["src"], size=11.5, color=MUTED)
    return f


@figure("one-photon-for-twenty")
def one_photon_for_twenty(lang):
    t = {
        "en": dict(title="One photon in, twenty out",
                   sub="The Earth returns as much energy as it receives. Only the coin is smaller.",
                   sun="the Sun", sun_t="about 5,800 K", earth="the Earth", earth_t="about 255 K\nseen from space",
                   one="1 photon of sunlight", twenty="about 20 infrared photons", sky="to the cold sky",
                   between="between the one and the twenty:\nthe wind, the rivers, the grass, you and I",
                   src="Rough arithmetic: a photon's energy goes with the temperature of the body that sent it;\n"
                       "5,800 / 255 ≈ 23, say twenty."),
        "ru": dict(title="Один фотон пришёл, двадцать ушло",
                   sub="Земля возвращает столько же энергии, сколько получает. Только монета мельче.",
                   sun="Солнце", sun_t="около 5800 К", earth="Земля", earth_t="около 255 К,\nесли смотреть из космоса",
                   one="1 фотон солнечного света", twenty="около 20 инфракрасных фотонов", sky="в холодное небо",
                   between="между одним и двадцатью:\nветер, реки, трава, мы с тобой",
                   src="Арифметика на колене: энергия фотона пропорциональна температуре тела, которое его послало;\n"
                       "5800 / 255 ≈ 23, пусть будет двадцать."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    cy = 200
    f.circle(92, cy, 46, fill=YELLOW, opacity=0.85)
    f.text(92, cy + 70, t["sun"], size=14, anchor="middle", weight="600")
    f.text(92, cy + 88, t["sun_t"], size=12.5, color=INK2, anchor="middle")
    ex = 400
    f.line(146, cy, ex - 44, cy, color=YELLOW, width=5, arrow=True)
    f.text((146 + ex - 44) / 2, cy - 14, t["one"], size=13, color=INK, anchor="middle", weight="600")
    f.circle(ex, cy, 34, fill=BLUE, opacity=0.8)
    f.text(ex, cy + 58, t["earth"], size=14, anchor="middle", weight="600")
    f.text(ex, cy + 76, t["earth_t"], size=12.5, color=INK2, anchor="middle")
    n = 20
    for i in range(n):
        ang = math.radians(-32 + 64 * i / (n - 1))
        x1, y1 = ex + 42 * math.cos(ang), cy + 42 * math.sin(ang)
        x2, y2 = ex + 215 * math.cos(ang), cy + 215 * math.sin(ang)
        f.line(x1, y1, x2, y2, color=RED, width=1.2, arrow=True)
    f.text(728, 334, t["twenty"], size=13, color=RED, anchor="end", weight="600")
    f.text(728, 352, t["sky"], size=12.5, color=INK2, anchor="end")
    f.text(250, 318, t["between"], size=13, color=INK, anchor="middle", italic=True)
    f.text(28, 372, t["src"], size=11.5, color=MUTED)
    return f


@figure("watts-per-kilogram")
def watts_per_kilogram(lang):
    t = {
        "en": dict(title="How much flow passes through a kilogram",
                   sub="Watts per kilogram of the thing the flow passes through. The scale is logarithmic.",
                   rows=[("the Sun", 0.0002, "0.0002"), ("a human body", 1.5, "1.5"),
                         ("a human brain", 14, "14"),
                         ("a server with eight graphics\nprocessors, the whole of it", 75, "about 75"),
                         ("the silicon crystal of\na graphics processor", 200000, "about 200,000")],
                   unit="W/kg", ticks=["0.0001", "0.01", "1", "100", "10,000", "1,000,000"],
                   src="Rough arithmetic: the Sun 3.8·10²⁶ W / 2·10³⁰ kg; a body 120 W / 80 kg; a brain 20 W / 1.4 kg; "
                       "a server 10 kW / 130 kg;\na crystal: several hundred watts / a gram or two. "
                       "The measure is E. Chaisson's energy rate density; it is not a measure of mind."),
        "ru": dict(title="Сколько потока проходит через килограмм",
                   sub="Ватты на килограмм того, сквозь что идёт поток. Шкала логарифмическая.",
                   rows=[("Солнце", 0.0002, "0,0002"), ("тело человека", 1.5, "1,5"),
                         ("мозг человека", 14, "14"),
                         ("сервер с восемью графическими\nпроцессорами, целиком", 75, "около 75"),
                         ("кристалл кремния\nграфического процессора", 200000, "около 200 000")],
                   unit="Вт/кг", ticks=["0,0001", "0,01", "1", "100", "10 000", "1 000 000"],
                   src="Арифметика на колене: Солнце 3,8·10²⁶ Вт / 2·10³⁰ кг; тело 120 Вт / 80 кг; мозг 20 Вт / 1,4 кг; "
                       "сервер 10 кВт / 130 кг;\nкристалл: несколько сотен ватт / грамм-два. "
                       "Мера — «плотность потока энергии» Э. Чейссона; это не мера разума."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 250, 610, 1e-4, 1e6
    y0, row = 96, 50
    ybase = y0 + row * len(t["rows"])
    for k, label in enumerate(t["ticks"]):
        x = log_x(10 ** (-4 + 2 * k), lo, hi, x0, x1)
        f.line(x, y0 - 4, x, ybase, color=GRID, width=1)
        f.text(x, ybase + 18, label, size=11.5, color=MUTED, anchor="middle")
    f.text(x1 + 46, ybase + 18, t["unit"], size=11.5, color=MUTED)
    colors = [YELLOW, AQUA, AQUA, BLUE, BLUE]
    for i, (name, value, shown) in enumerate(t["rows"]):
        y = y0 + i * row
        lines = name.count("\n") + 1
        f.text(x0 - 14, y + (27 if lines == 1 else 18), name, size=13, color=INK, anchor="end")
        x = log_x(value, lo, hi, x0, x1)
        f.rect(x0, y + 10, max(x - x0, 3), 24, fill=colors[i], r=3, opacity=0.85)
        f.text(x + 8, y + 27, f"{shown} {t['unit']}", size=13, color=INK, weight="600")
    f.line(x0, y0 - 4, x0, ybase, color=INK2, width=1.5)
    f.text(28, 392, t["src"], size=11.5, color=MUTED)
    return f


# --- 36. What the Rat Laughs At -------------------------------------------------------------------

@figure("laughter-out-of-hearing")
def laughter_out_of_hearing(lang):
    t = {
        "en": dict(title="The chirp we cannot hear",
                   sub="Sound frequency on a logarithmic scale. Our hearing ends at about 20 kilohertz.",
                   rows=["human hearing", "human laughter,\nthe main tone", "rat hearing", "a rat's alarm call",
                         "a rat's chirp in play\nand under tickling"],
                   vals=["20 Hz – 20 kHz", "a few hundred hertz", "about 250 Hz – 80 kHz", "about 22 kHz",
                         "about 50 kHz"],
                   edge="our hearing ends here",
                   ticks=["20 Hz", "100 Hz", "1 kHz", "10 kHz", "100 kHz"],
                   src="Rounded figures; the hearing ranges are approximate. "
                       "The calls of rats: Panksepp & Burgdorf (2003)."),
        "ru": dict(title="Писк, которого мы не слышим",
                   sub="Частота звука, шкала логарифмическая. Наш слух кончается примерно на 20 килогерцах.",
                   rows=["слух человека", "смех человека,\nосновной тон", "слух крысы", "тревожный крик крысы",
                         "писк крысы в игре\nи при щекотке"],
                   vals=["20 Гц – 20 кГц", "несколько сотен герц", "примерно 250 Гц – 80 кГц", "около 22 кГц",
                         "около 50 кГц"],
                   edge="здесь кончается наш слух",
                   ticks=["20 Гц", "100 Гц", "1 кГц", "10 кГц", "100 кГц"],
                   src="Цифры округлены; границы слуха приблизительны. "
                       "Звуки крыс: Панксепп и Бургдорф (2003)."),
    }[lang]
    f = Fig(760, 390, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, lo, hi = 200, 720, 20, 100000
    y0, row = 104, 44
    ybase = y0 + row * 5

    def X(v):
        return log_x(v, lo, hi, x0, x1)

    for v, label in zip((20, 100, 1000, 10000, 100000), t["ticks"]):
        f.line(X(v), y0 - 4, X(v), ybase, color=GRID, width=1)
        f.text(X(v), ybase + 18, label, size=11.5, color=MUTED, anchor="middle")
    f.line(X(20000), y0 - 14, X(20000), ybase, color=RED, width=1.3, dash="5 4")
    f.text(X(20000) - 8, y0 - 8, t["edge"], size=12, color=RED, anchor="end")
    for i, name in enumerate(t["rows"]):
        y = y0 + i * row
        lines = name.count("\n") + 1
        f.text(x0 - 14, y + (27 if lines == 1 else 19), name, size=13, color=INK, anchor="end")
    mid = [y0 + i * row + 22 for i in range(5)]
    f.rect(X(20), mid[0] - 11, X(20000) - X(20), 22, fill=AQUA, r=3, opacity=0.85)
    f.text(X(20000) + 10, mid[0] + 4.5, t["vals"][0], size=12.5, color=INK, weight="600")
    f.rect(X(250), mid[1] - 11, X(500) - X(250), 22, fill=AQUA, r=3, opacity=0.85)
    f.text(X(500) + 10, mid[1] + 4.5, t["vals"][1], size=12.5, color=INK, weight="600")
    f.rect(X(250), mid[2] - 11, X(80000) - X(250), 22, fill=BLUE, r=3, opacity=0.85)
    f.text(X(250) + 12, mid[2] + 4.5, t["vals"][2], size=12.5, color="#ffffff", weight="600")
    for i, v in ((3, 22000), (4, 50000)):
        f.circle(X(v), mid[i], 7, fill=BLUE, stroke=SURFACE, width=2)
        f.text(X(v) - 14, mid[i] + 4.5, t["vals"][i], size=12.5, color=INK, weight="600", anchor="end")
    f.line(x0, y0 - 4, x0, ybase, color=INK2, width=1.5)
    f.text(28, 374, t["src"], size=11.5, color=MUTED)
    return f


@figure("tickle-with-a-delay")
def tickle_with_a_delay(lang):
    t = {
        "en": dict(title="Why you cannot tickle yourself",
                   sub="The head forecasts the touch of its own hand and subtracts it. Delay the touch, and it tickles.",
                   y="how ticklish it feels",
                   bars=["your own hand", "the robot lags\nby 0.1 s", "by 0.2 s", "by 0.3 s",
                         "someone\nelse's hand"],
                   left="the forecast matches:\nhardly felt", right="the forecast misses:\nfelt in full",
                   src="A scheme, not measured data. After Blakemore, Wolpert & Frith (1998) "
                       "and Blakemore, Frith & Wolpert (1999)."),
        "ru": dict(title="Почему нельзя пощекотать себя",
                   sub="Голова предсказывает касание своей руки и вычитает его. Задержи касание, и станет щекотно.",
                   y="насколько щекотно",
                   bars=["своя рука", "робот опаздывает\nна 0,1 с", "на 0,2 с", "на 0,3 с", "чужая рука"],
                   left="прогноз совпал:\nпочти не чувствуется", right="прогноз промахнулся:\nчувствуется целиком",
                   src="Схема, а не измеренные данные. По Блейкмор, Вольперту и Фриту (1998) "
                       "и Блейкмор, Фриту и Вольперту (1999)."),
    }[lang]
    f = Fig(760, 410, t["title"])
    heading(f, t["title"], t["sub"])
    base, x0 = 310, 96
    f.line(x0, base, 724, base, color=INK2, width=1.5)
    f.line(x0, base, x0, 104, color=INK2, width=1.5, arrow=True)
    f.text(56, (base + 104) / 2, t["y"], size=12.5, color=INK2, anchor="middle", rotate=-90)
    heights = [34, 78, 112, 146, 184]
    colors = [AQUA, BLUE, BLUE, BLUE, ORANGE]
    for i, (label, h) in enumerate(zip(t["bars"], heights)):
        cx = 170 + i * 122
        f.rect(cx - 36, base - h, 72, h, fill=colors[i], r=3, opacity=0.85)
        f.text(cx, base + 20, label, size=12.5, color=INK, anchor="middle")
    f.text(170, base - 34 - 34, t["left"], size=12.5, color=AQUA, anchor="middle", weight="600")
    f.text(536, 108, t["right"], size=12.5, color=ORANGE, anchor="middle", weight="600")
    f.text(28, 394, t["src"], size=11.5, color=MUTED)
    return f


@figure("cheap-mistake-three-floors")
def cheap_mistake_three_floors(lang):
    t = {
        "en": dict(title="One cheap mistake on three floors",
                   sub="Andrey's guess, not an accepted theory: what laughter marks in play, in tickling and in a joke.",
                   head=["the forecast said", "what came", "the mistake is cheap", "the same mistake,\nexpensive"],
                   rows=[("play", "rats, wolves,\napes, us",
                          ["a bite", "a bite that\nis not a bite", "a chirp, a bow,\npanting", "a fight"]),
                         ("tickling", "rats, apes, us",
                          ["an attack on the neck\nand the belly", "one of your own,\nand no harm", "laughter",
                           "a predator:\nfear"]),
                         ("a joke", "us",
                          ["one meaning\nof the words", "another meaning", "mirth:\nthe bonus",
                           "a heavy image:\nan offence"])],
                   src="A scheme, not measured data. The bonus for a mistake found: Hurley, Dennett & Adams (2011)."),
        "ru": dict(title="Одна дешёвая ошибка на трёх этажах",
                   sub="Догадка Андрея, а не принятая теория: что отмечает смех в игре, в щекотке и в анекдоте.",
                   head=["прогноз говорил", "что пришло", "ошибка дешёвая", "та же ошибка,\nдорогая"],
                   rows=[("игра", "крысы, волки,\nобезьяны, мы",
                          ["укус", "укус, который\nне укус", "писк, поклон,\nпыхтение", "драка"]),
                         ("щекотка", "крысы, обезьяны, мы",
                          ["нападение на шею\nи живот", "свой,\nи вреда нет", "смех", "хищник:\nстрах"]),
                         ("анекдот", "мы",
                          ["один смысл слов", "другой смысл", "веселье:\nпремия", "тяжёлый образ:\nобида"])],
                   src="Схема, а не измеренные данные. Премия за найденную ошибку: Хёрли, Деннет и Адамс (2011)."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [178, 336, 478, 608, 736]
    top, head_h, row_h = 86, 44, 74
    bottom = top + head_h + row_h * 3
    f.rect(cols[2], top, cols[3] - cols[2], bottom - top, fill=AQUA, r=0, opacity=0.10)
    f.rect(cols[3], top, cols[4] - cols[3], bottom - top, fill=RED, r=0, opacity=0.09)
    head_colors = [INK2, INK2, AQUA, RED]
    for k, label in enumerate(t["head"]):
        lines = label.count("\n") + 1
        f.text((cols[k] + cols[k + 1]) / 2, top + (27 if lines == 1 else 19), label, size=12.5,
               color=head_colors[k], anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[4], y, color=GRID, width=1.2)
        f.text(28, y + 30, name, size=15, color=INK, weight="600")
        f.text(28, y + 48, who, size=11.5, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            f.text((cols[k] + cols[k + 1]) / 2, y + (42 if lines == 1 else 34), cell, size=13, color=INK,
                   anchor="middle")
    f.line(28, bottom, cols[4], bottom, color=GRID, width=1.2)
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


# --- 37. Who Exploits Whom When a Business Loses Money --------------------------------------------

@figure("same-problem-other-sign")
def same_problem_other_sign(lang):
    t = {
        "en": dict(title="The same problem with the other sign",
                   sub="Oleg's notebook. Petya, his wage and his lathe are the same on both pages.",
                   pages=[("Given: the capitalist made a profit", ["+50", "+150", "+200"], "+400",
                           "Find: whom should he sack\nfor the profit to grow?", "Nobody. Yet owners do sack."),
                          ("Given: the capitalist made a loss", ["−50", "−150", "−200"], "−400",
                           "Find: who exploited whom?", "Petya, Vasya and Kolya, the capitalist?")],
                   names=["on Petya", "on Vasya", "on Kolya"], total="in all, roubles",
                   same="The same on both pages: the wage, the lathe, the eight hours. "
                        "Only the sign in the owner's line differs.",
                   src="The problem: the author on the forum, 4 June 2017. The question with the minus: "
                       "the author under article 06, 14 December 2011."),
        "ru": dict(title="Та же задачка с другим знаком",
                   sub="Блокнот Олега. Петя, его зарплата и его станок на обеих страницах одни и те же.",
                   pages=[("Дано: капиталист получил прибыль", ["+50", "+150", "+200"], "+400",
                           "Найти: кого ему уволить,\nчтобы прибыль выросла?", "Никого. Но хозяева увольняют."),
                          ("Дано: капиталист получил убыток", ["−50", "−150", "−200"], "−400",
                           "Найти: кто кого эксплуатировал?", "Петя, Вася и Коля — капиталиста?")],
                   names=["на Пете", "на Васе", "на Коле"], total="всего, рублей",
                   same="На обеих страницах одинаковы зарплата, станок и восемь часов. "
                        "Отличается только знак в строке хозяина.",
                   src="Задачка: автор на форуме, 4 июня 2017 года. Вопрос с минусом: "
                       "автор под статьёй 06, 14 декабря 2011 года."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    top, h, w = 84, 262, 336
    for k, (given, vals, total, find, answer) in enumerate(t["pages"]):
        x = 36 + k * (w + 16)
        color = AQUA if k == 0 else RED
        f.rect(x, top, w, h, fill="#ffffff", stroke=BORDER, r=4)
        for i in range(3):
            f.line(x + 14, top + 52 + i * 30, x + w - 14, top + 52 + i * 30, color=GRID, width=1)
        f.text(x + 22, top + 32, given, size=14, color=INK, weight="600")
        for i, (name, val) in enumerate(zip(t["names"], vals)):
            y = top + 72 + i * 30
            f.text(x + 34, y, name, size=14, color=INK)
            f.text(x + w - 34, y, val, size=15, color=color, anchor="end", weight="600")
        f.line(x + 22, top + 142, x + w - 22, top + 142, color=INK2, width=1.5)
        f.text(x + 34, top + 164, t["total"], size=14, color=INK, weight="600")
        f.text(x + w - 34, top + 164, total, size=17, color=color, anchor="end", weight="700")
        lines = find.count("\n") + 1
        f.text(x + 22, top + (196 if lines == 2 else 204), find, size=13, color=INK2)
        f.text(x + 22, top + 244, answer, size=13.5, color=INK, italic=True)
    f.text(380, top + h + 28, t["same"], size=12.5, color=INK, anchor="middle", weight="600")
    f.text(28, 402, t["src"], size=11.5, color=MUTED)
    return f


@figure("where-the-loss-went")
def where_the_loss_went(lang):
    t = {
        "en": dict(title="Where thirty billion dollars of losses went",
                   sub="The investors' money had three recipients. Two of them spent their share.",
                   src_box="the investors'\nmoney", src_sub="more than 30 billion\ndollars of losses\nbefore 2023",
                   boxes=["the passengers:\nrides below cost", "the drivers:\nbonuses",
                          "the program, the maps,\nthe records of rides"],
                   out=["spent:\nthe ride is over", "spent:\npetrol, food, the car", "remained"],
                   habit="and with it the habit of about\n150 million people a month\nof pressing a button",
                   src="A scheme: the split between the three shares is not shown.\n"
                       "Uber: founded in 2009, first yearly operating profit in 2023."),
        "ru": dict(title="Куда ушли тридцать миллиардов долларов убытков",
                   sub="У денег инвесторов было три получателя. Двое свою долю потратили.",
                   src_box="деньги\nинвесторов", src_sub="больше 30 миллиардов\nдолларов убытков\nдо 2023 года",
                   boxes=["пассажиры:\nпоездки ниже себестоимости", "водители:\nпремии",
                          "программа, карты,\nзаписи о поездках"],
                   out=["потрачено:\nпоездка кончилась", "потрачено:\nбензин, еда, машина", "осталось"],
                   habit="а с ним привычка примерно\n150 миллионов человек в месяц\nнажимать кнопку",
                   src="Схема: как деньги разделились между тремя долями, не показано.\n"
                       "Uber: основан в 2009 году, первая годовая операционная прибыль в 2023-м."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    f.box(28, 168, 176, 104, t["src_box"], fill="#ffffff", stroke=INK2, size=15, weight="600",
          sub=t["src_sub"], sub_color=INK2)
    ys = [96, 190, 284]
    for i, (label, out) in enumerate(zip(t["boxes"], t["out"])):
        y = ys[i]
        last = i == 2
        color = BLUE if last else MUTED
        f.path(f"M204,220 C246,220 246,{y + 32} 284,{y + 32}", color=color, width=3 if last else 2.2,
               arrow=True)
        if last:
            f.rect(290, y, 226, 64, fill=BLUE, r=8, opacity=0.10)
        f.box(290, y, 226, 64, label, fill="none", stroke=color, size=13.5, weight="600" if last else "normal")
        f.line(520, y + 32, 546, y + 32, color=color, width=2, arrow=True)
        if last:
            f.text(556, y + 22, out, size=16, color=BLUE, weight="700")
            f.text(556, y + 42, t["habit"], size=12, color=INK2)
        else:
            f.text(556, y + 27, out, size=13, color=MUTED)
    f.text(28, 388, t["src"], size=11.5, color=MUTED)
    return f


@figure("built-and-sold")
def built_and_sold(lang):
    t = {
        "en": dict(title="Built for five billion, sold for twenty-five million",
                   sub="The Iridium satellite system before and after the bankruptcy of 1999. The scale is linear.",
                   rows=[("built\n(service opened in 1998)", 5000, "about 5,000 million dollars"),
                         ("sold out of\nbankruptcy", 25, "25 million dollars: half a cent on the dollar")],
                   note="The 66 satellites were the same before and after the sale.\n"
                        "The investors lost the money, the staff their jobs; the system has worked ever since.",
                   src="Rounded figures. The satellites were replaced by a new generation in 2017–2019."),
        "ru": dict(title="Построено за пять миллиардов, продано за двадцать пять миллионов",
                   sub="Спутниковая система «Иридиум» до и после банкротства 1999 года. Шкала линейная.",
                   rows=[("построено\n(связь открыта в 1998 году)", 5000, "около 5000 миллионов долларов"),
                         ("продано при\nбанкротстве", 25, "25 миллионов долларов: полцента с доллара")],
                   note="66 спутников до и после продажи одни и те же.\n"
                        "Инвесторы потеряли деньги, сотрудники работу; система работает с тех пор.",
                   src="Цифры округлены. В 2017–2019 годах спутники заменили новым поколением."),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, row = 216, 716, 96, 66
    colors = [BLUE, RED]
    for i, (name, value, shown) in enumerate(t["rows"]):
        y = y0 + i * row
        f.text(x0 - 14, y + 22, name, size=13, color=INK, anchor="end")
        wbar = max(value / 5000 * (x1 - x0), 3)
        f.rect(x0, y + 8, wbar, 30, fill=colors[i], r=2, opacity=0.85)
        if i == 0:
            f.text(x0 + 14, y + 28, shown, size=13.5, color="#ffffff", weight="600")
        else:
            f.text(x0 + wbar + 10, y + 28, shown, size=13.5, color=INK, weight="600")
    f.line(x0, y0 - 2, x0, y0 + 2 * row - 12, color=INK2, width=1.5)
    f.text(28, 252, t["note"], size=12.5, color=INK)
    f.text(28, 310, t["src"], size=11.5, color=MUTED)
    return f


# --- 38. Oxygen Was a Poison -----------------------------------------------------------------------

@figure("oxygen-two-steps")
def oxygen_two_steps(lang):
    t = {
        "en": dict(title="Oxygen came into the air in two steps",
                   sub="Free oxygen in the air over the life of the Earth. The trees are at the very end.",
                   levels=["today:\n21% of the air", "low", "none"],
                   events=["≈ 2.4: oxygen reaches the air", "≈ 0.6: animals", "0.385: forests"],
                   iron="what is made is taken by the ocean's iron",
                   ice="ice reaches\nthe tropics", low="how low is argued", axis="billion years ago",
                   src="A scheme, not data: the dates are rounded, and estimates of the level between the two "
                       "steps differ hundreds of times."),
        "ru": dict(title="Кислород пришёл в воздух в две ступени",
                   sub="Свободный кислород в воздухе за время жизни Земли. Деревья в самом конце.",
                   levels=["сегодня:\n21% воздуха", "мало", "нет"],
                   events=["≈ 2,4: кислород выходит в воздух", "≈ 0,6: животные", "0,385: леса"],
                   iron="сделанное забирает железо океана",
                   ice="лёд доходит\nдо тропиков", low="насколько мало — спорят", axis="миллиардов лет назад",
                   src="Схема, а не данные: даты округлены, а оценки уровня между двумя ступенями "
                       "расходятся в сотни раз."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 118, 716, 290, 124
    ylow = yb - 0.22 * (yb - yt)

    def X(ga):
        return x0 + (4.5 - ga) / 4.5 * (x1 - x0)

    # the ice of 2.4–2.1 billion years ago
    f.rect(X(2.4), yt, X(2.1) - X(2.4), yb - yt, fill=BLUE, r=0, opacity=0.12)
    f.text(X(2.1) + 8, 168, t["ice"], size=12, color=BLUE)
    # levels
    for y, label in zip((yt, ylow, yb), t["levels"]):
        f.line(x0, y, x1, y, color=INK2 if y == yb else GRID, width=1.2 if y == yb else 1)
        lines = label.count("\n") + 1
        f.text(x0 - 10, y + (4 if lines == 1 else -4), label, size=11.5, color=INK2, anchor="end")
    for ga in (4, 3, 2, 1, 0):
        f.line(X(ga), yb, X(ga), yb + 5, color=INK2, width=1.2)
        f.text(X(ga), yb + 20, str(ga), size=11.5, color=INK2, anchor="middle")
    f.text(x1, yb + 40, t["axis"], size=11.5, color=INK2, anchor="end")
    # events
    for ga, label, anchor, dx in zip((2.4, 0.6, 0.385), t["events"], ("middle", "end", "start"), (0, 4, -5)):
        f.line(X(ga), yt - 12, X(ga), yb, color=MUTED, width=1, dash="3 3")
        f.text(X(ga) + dx, yt - 18, label, size=11.5, color=ORANGE, anchor=anchor, weight="600")
    # the curve
    d = (f"M{X(4.5):.1f},{yb - 2:.1f} L{X(2.46):.1f},{yb - 2:.1f} "
         f"C{X(2.39):.1f},{yb - 2:.1f} {X(2.38):.1f},{ylow:.1f} {X(2.3):.1f},{ylow:.1f} "
         f"L{X(0.86):.1f},{ylow:.1f} "
         f"C{X(0.6):.1f},{ylow:.1f} {X(0.62):.1f},{yt:.1f} {X(0.4):.1f},{yt:.1f} L{X(0):.1f},{yt:.1f}")
    f.path(d + f" L{X(0):.1f},{yb:.1f} L{X(4.5):.1f},{yb:.1f} Z", color="none", width=0, fill=BLUE, opacity=0.08)
    f.path(d, color=BLUE, width=2.5)
    f.text(x0 + 12, yb - 14, t["iron"], size=12, color=INK2, italic=True)
    f.text((X(2.1) + X(0.86)) / 2 + 10, ylow - 10, t["low"], size=12, color=INK2, italic=True, anchor="middle")
    f.text(28, 360, t["src"], size=11, color=MUTED)
    return f


def two_bars(f, rows, vmax, colors, x0=216, x1=716, y0=96, row=66):
    """Two horizontal bars on a linear scale; the label goes inside a long bar and beside a short one."""
    for i, (name, value, shown) in enumerate(rows):
        y = y0 + i * row
        f.text(x0 - 14, y + 22, name, size=13, color=INK, anchor="end")
        wbar = max(value / vmax * (x1 - x0), 3)
        f.rect(x0, y + 8, wbar, 30, fill=colors[i], r=2, opacity=0.85)
        if wbar > 300:
            f.text(x0 + 14, y + 28, shown, size=13.5, color="#ffffff", weight="600")
        else:
            f.text(x0 + wbar + 10, y + 28, shown, size=13.5, color=INK, weight="600")
    f.line(x0, y0 - 2, x0, y0 + 2 * row - 12, color=INK2, width=1.5)


@figure("two-and-thirty")
def two_and_thirty(lang):
    t = {
        "en": dict(title="The same sugar, two ways to live on it",
                   sub="What a cell gets from one molecule of glucose, in molecules of ATP. The scale is linear.",
                   rows=[("fermentation,\nwithout oxygen", 2, "2"),
                         ("respiration,\nwith oxygen", 30, "about 30: fifteen times more")],
                   note="The poison turned out to be the best fuel there is,\n"
                        "for whoever learned to keep it in a stove.",
                   src="Rounded figures: today's textbooks give 30–32 for respiration, older ones 36–38."),
        "ru": dict(title="Тот же сахар, два способа на нём жить",
                   sub="Что клетка получает из одной молекулы глюкозы, в молекулах АТФ. Шкала линейная.",
                   rows=[("брожение,\nбез кислорода", 2, "2"),
                         ("дыхание,\nс кислородом", 30, "около 30: в пятнадцать раз больше")],
                   note="Яд оказался лучшим топливом из всех,\n"
                        "для того, кто научился держать его в печке.",
                   src="Цифры округлены: в нынешних учебниках для дыхания 30–32, в старых 36–38."),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    two_bars(f, t["rows"], 30, [MUTED, ORANGE])
    f.text(28, 252, t["note"], size=12.5, color=INK)
    f.text(28, 310, t["src"], size=11.5, color=MUTED)
    return f


@figure("whose-breath")
def whose_breath(lang):
    t = {
        "en": dict(title="Who breathes out on this planet",
                   sub="Carbon dioxide given out in a year, billion tonnes. The scale is linear.",
                   rows=[("all people,\n8.2 billion", 3, "about 3"),
                         ("chimneys and\nexhaust pipes", 37, "about 37 (2024): twelve times more")],
                   note="The carbon in our breath was taken from the air by last year's harvest: a circle.\n"
                        "The carbon from the chimneys is from under the ground.",
                   src="Arithmetic on the knee: about a kilogram of carbon dioxide per person a day. "
                       "Fuel and cement: Global Carbon Budget 2024."),
        "ru": dict(title="Кто выдыхает на этой планете",
                   sub="Углекислый газ, отданный за год, миллиардов тонн. Шкала линейная.",
                   rows=[("все люди,\n8,2 миллиарда", 3, "около 3"),
                         ("трубы и\nвыхлопы", 37, "около 37 (2024): в двенадцать раз больше")],
                   note="Углерод нашего выдоха взят из воздуха прошлогодним урожаем: круг.\n"
                        "Углерод из труб взят из-под земли.",
                   src="Арифметика на коленке: около килограмма углекислого газа на человека в сутки. "
                       "Топливо и цемент: Global Carbon Budget 2024."),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    two_bars(f, t["rows"], 37, [AQUA, RED])
    f.text(28, 252, t["note"], size=12.5, color=INK)
    f.text(28, 310, t["src"], size=11.5, color=MUTED)
    return f


# --- 39. Oleg's Prophetic Dream and the Price of a False Alarm --------------------------------------

@figure("dreams-and-one-call")
def dreams_and_one_call(lang):
    t = {
        "en": dict(title="Three hundred and sixty dreams, one phone call",
                   sub="Oleg's count: once a month for thirty years he woke remembering an old acquaintance in a dream.",
                   years="thirty years, twelve dreams a year",
                   grey="the phone did not ring: written off, and not one of them can be named",
                   hit="the phone rang in the morning: remembered for life",
                   note="The ledger of memory has an income column and no expense column.",
                   src="A scheme of Oleg's rough figures, not data."),
        "ru": dict(title="Триста шестьдесят снов и один звонок",
                   sub="Счёт Олега: раз в месяц тридцать лет подряд он просыпался и помнил, что снился кто-то из давних знакомых.",
                   years="тридцать лет, двенадцать снов в год",
                   grey="телефон не зазвонил: списаны, и ни одного не назвать",
                   hit="утром зазвонил телефон: запомнен на всю жизнь",
                   note="В бухгалтерии памяти есть графа «приход» и нет графы «расход».",
                   src="Схема прикидок Олега, а не данные."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, y0, dx, dy = 46, 96, 23, 15
    for c in range(30):
        for r in range(12):
            hit = c == 29 and r == 4
            f.circle(x0 + c * dx, y0 + r * dy, 6.5 if hit else 3.8, fill=ORANGE if hit else MUTED,
                     opacity=1 if hit else 0.5)
    yb = y0 + 11 * dy + 22
    f.line(x0 - 4, yb, x0 + 29 * dx + 4, yb, color=INK2, width=1.2, arrow=True)
    f.text(x0 - 4, yb + 18, t["years"], size=12, color=INK2)
    f.circle(50, 322, 3.8, fill=MUTED, opacity=0.5)
    f.text(64, 326, t["grey"], size=13, color=INK2)
    f.circle(50, 344, 6.5, fill=ORANGE)
    f.text(64, 348, t["hit"], size=13, color=INK, weight="600")
    f.text(732, yb + 18, t["note"], size=12.5, color=INK, italic=True, anchor="end")
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


@figure("shared-birthday")
def shared_birthday(lang):
    t = {
        "en": dict(title="Two people with the same birthday",
                   sub="The chance that at least two people in a group share a birthday: any two, not you and somebody.",
                   x="people in the group", any="any two",
                   marks={23: "23 people: 50.7%\n253 pairs", 30: "30 people: 70.6%\n435 pairs",
                          57: "57 people: 99%"},
                   me="somebody shares your own birthday:\n7.6% in a group of 30",
                   src="An exact count for 365 equally likely days."),
        "ru": dict(title="Двое с общим днём рождения",
                   sub="Шанс, что хотя бы у двоих в компании день рождения совпадёт: у любых двоих, а не у тебя с кем-то.",
                   x="человек в компании", any="любые двое",
                   marks={23: "23 человека: 50,7%\n253 пары", 30: "30 человек: 70,6%\n435 пар",
                          57: "57 человек: 99%"},
                   me="у кого-то день рождения как у тебя:\n7,6% в компании из 30",
                   src="Точный счёт для 365 равновероятных дней."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 84, 716, 312, 104

    def X(n):
        return x0 + n / 60 * (x1 - x0)

    def Y(p):
        return yb - p * (yb - yt)

    def any_two(n):
        q = 1.0
        for k in range(n):
            q *= (365 - k) / 365
        return 1 - q

    def with_me(n):
        return 1 - (364 / 365) ** (n - 1)

    for p, label in ((0, "0"), (0.5, "50%"), (1, "100%")):
        f.line(x0, Y(p), x1, Y(p), color=INK2 if p == 0 else GRID, width=1.2 if p == 0 else 1,
               dash="4 4" if p == 0.5 else None)
        f.text(x0 - 10, Y(p) + 4, label, size=11.5, color=INK2, anchor="end")
    for n in (10, 20, 30, 40, 50, 60):
        f.line(X(n), yb, X(n), yb + 5, color=INK2, width=1.2)
        f.text(X(n), yb + 20, str(n), size=11.5, color=INK2, anchor="middle")
    f.text(x1, yb + 40, t["x"], size=11.5, color=INK2, anchor="end")
    for fn, color, width in ((with_me, MUTED, 2), (any_two, BLUE, 2.5)):
        d = "M" + " L".join(f"{X(n):.1f},{Y(fn(n)):.1f}" for n in range(1, 61))
        f.path(d, color=color, width=width)
    f.text(X(12), Y(any_two(12)) - 16, t["any"], size=12.5, color=BLUE, anchor="end", weight="600")
    for n, label in t["marks"].items():
        f.circle(X(n), Y(any_two(n)), 4.5, fill=ORANGE)
        if n == 57:
            f.text(X(n) - 8, Y(any_two(n)) + 24, label, size=12.5, color=INK, anchor="end", weight="600")
        else:
            f.text(X(n) + 12, Y(any_two(n)) + 16, label, size=12.5, color=INK, weight="600")
    f.circle(X(30), Y(with_me(30)), 4, fill=MUTED)
    f.text(X(33), Y(with_me(30)) - 28, t["me"], size=12, color=INK2)
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


@figure("price-of-two-mistakes")
def price_of_two_mistakes(lang):
    t = {
        "en": dict(title="Two mistakes and their prices",
                   sub="Something rustles in the grass. The four squares Andrey drew in the ash.",
                   cols=["it was the wind", "it was a snake"], rows=["jumped away", "stayed"],
                   cells=[[("a false alarm", "a minute lost"), ("right", "alive")],
                          [("right", "nothing lost"), ("a miss", "a life lost")]],
                   note="If a life is worth 100,000 such minutes, it pays to jump\n"
                        "even when only one rustle in 10,000 is a snake.",
                   src="A scheme. The smoke detector principle: Nesse (2001). "
                       "Selection for links that are not there: Foster & Kokko (2009)."),
        "ru": dict(title="Две ошибки и их цены",
                   sub="В траве что-то шуршит. Четыре клетки, которые Андрей начертил на золе.",
                   cols=["это был ветер", "это была змея"], rows=["отскочил", "остался"],
                   cells=[[("ложная тревога", "потеряна минута"), ("верно", "жив")],
                          [("верно", "ничего не потеряно"), ("пропуск", "потеряна жизнь")]],
                   note="Если жизнь стоит 100 000 таких минут, отскакивать выгодно,\n"
                        "даже когда змея — только один шорох из 10 000.",
                   src="Схема. Принцип дымового датчика: Нессе (2001). "
                       "Отбор на связи, которых нет: Фостер и Кокко (2009)."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    xs, top, head_h, row_h = [196, 462, 728], 88, 36, 84
    fills = [[ORANGE, AQUA], [AQUA, RED]]
    for k, label in enumerate(t["cols"]):
        f.text((xs[k] + xs[k + 1]) / 2, top + 23, label, size=13.5, color=INK2, anchor="middle", weight="600")
    for i, name in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.text(xs[0] - 16, y + row_h / 2 + 5, name, size=13.5, color=INK2, anchor="end", weight="600")
        for k, (what, cost) in enumerate(t["cells"][i]):
            color = fills[i][k]
            mistake = color != AQUA
            f.rect(xs[k] + 5, y + 5, xs[k + 1] - xs[k] - 10, row_h - 10, fill=color, stroke=color, width=1.2, r=8,
                   opacity=0.14 if mistake else 0.07)
            cx = (xs[k] + xs[k + 1]) / 2
            f.text(cx, y + 37, what, size=15.5 if mistake else 13, color=color if mistake else INK2,
                   anchor="middle", weight="700" if mistake else "normal")
            f.text(cx, y + 59, cost, size=13.5, color=INK, anchor="middle", weight="600" if mistake else "normal")
    f.text(28, 326, t["note"], size=13, color=INK, weight="600")
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


# --- 40. Why Firms Die and Cities Do Not ----------------------------------------------------------

@figure("same-billion-heartbeats")
def same_billion_heartbeats(lang):
    t = {
        "en": dict(title="The same billion",
                   sub="Heartbeats in a lifetime: beats a minute multiplied by the minutes of a life. Oleg's count.",
                   rows=[("a mouse, 25 grams", "600 a minute × 2.5 years", 0.79, "about 0.8 billion"),
                         ("an elephant, 5 tonnes", "30 a minute × 65 years", 1.02, "about 1 billion"),
                         ("Oleg, 62 years old", "70 a minute × 62 years", 2.28, "about 2.3 billion, still counting")],
                   ticks=["0", "1 billion", "2 billion"],
                   src="Round figures for the pulse and the lifespan; they give the order and no more. "
                       "People and bats live longer than their weight allots."),
        "ru": dict(title="Тот же миллиард",
                   sub="Удары сердца за жизнь: удары в минуту, умноженные на минуты жизни. Счёт Олега.",
                   rows=[("мышь, 25 граммов", "600 в минуту × 2,5 года", 0.79, "около 0,8 миллиарда"),
                         ("слон, 5 тонн", "30 в минуту × 65 лет", 1.02, "около 1 миллиарда"),
                         ("Олег, 62 года", "70 в минуту × 62 года", 2.28, "около 2,3 миллиарда, счёт идёт")],
                   ticks=["0", "1 миллиард", "2 миллиарда"],
                   src="Круглые цифры пульса и срока жизни; они дают порядок, не больше. "
                       "Люди и летучие мыши живут дольше, чем положено по весу."),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, vmax = 232, 560, 2.5
    y0, row = 92, 58
    ybase = y0 + row * len(t["rows"])

    def X(v):
        return x0 + v / vmax * (x1 - x0)

    for k, label in enumerate(t["ticks"]):
        f.line(X(k), y0 - 4, X(k), ybase, color=INK2 if k == 0 else GRID, width=1.5 if k == 0 else 1,
               dash="4 4" if k == 1 else None)
        f.text(X(k), ybase + 18, label, size=11.5, color=MUTED, anchor="middle")
    colors = [AQUA, AQUA, ORANGE]
    for i, (name, how, value, shown) in enumerate(t["rows"]):
        y = y0 + i * row
        f.text(x0 - 14, y + 22, name, size=13.5, color=INK, anchor="end", weight="600")
        f.text(x0 - 14, y + 40, how, size=12, color=INK2, anchor="end")
        f.rect(x0, y + 12, X(value) - x0, 26, fill=colors[i], r=3, opacity=0.85)
        f.text(X(value) + 8, y + 30, shown, size=13, color=INK, weight="600")
    f.text(28, 312, t["src"], size=11.5, color=MUTED)
    return f


@figure("city-twice-as-large")
def city_twice_as_large(lang):
    t = {
        "en": dict(title="A city twice as large",
                   sub="What changes per inhabitant at every doubling, by the rounded exponents of the 2007 count.",
                   rows=[("the pipes", "petrol stations, cables, roads", -13, "about 13% less", "exponent ≈ 0.8"),
                         ("a person's own needs", "housing, jobs, water at home", 0, "the same", "exponent ≈ 1"),
                         ("what happens between people", "wages, patents, serious crime", 15, "about 15% more",
                          "exponent ≈ 1.2")],
                   axis="per inhabitant",
                   src="Bettencourt, Lobo, Helbing, Kühnert, West (2007): 2^(0.8 − 1) = 0.87, 2^(1.2 − 1) = 1.15. "
                       "The exponents differ from measure\nto measure and move with the edge of the city "
                       "(Arcaute and others, 2015)."),
        "ru": dict(title="Город вдвое больше",
                   sub="Что меняется в расчёте на жителя при каждом удвоении, по округлённым показателям подсчёта 2007 года.",
                   rows=[("трубы", "заправки, кабели, дороги", -13, "примерно на 13% меньше", "показатель ≈ 0,8"),
                         ("собственные нужды человека", "жильё, рабочие места, вода в квартире", 0, "столько же",
                          "показатель ≈ 1"),
                         ("то, что происходит между людьми", "зарплаты, патенты, тяжкие преступления", 15,
                          "примерно на 15% больше", "показатель ≈ 1,2")],
                   axis="на жителя",
                   src="Беттенкур, Лобо, Хелбинг, Кюнерт, Уэст (2007): 2^(0,8 − 1) = 0,87, 2^(1,2 − 1) = 1,15. "
                       "Показатели разные у разных величин\nи сдвигаются вместе с границей города "
                       "(Аркауте и др., 2015)."),
    }[lang]
    f = Fig(760, 350, t["title"])
    heading(f, t["title"], t["sub"])
    xc, scale = 470, 7.0          # pixels per percent
    y0, row = 92, 62
    ybase = y0 + row * len(t["rows"])
    for pct in (-20, -10, 10, 20):
        x = xc + pct * scale
        f.line(x, y0 - 4, x, ybase, color=GRID, width=1)
        f.text(x, ybase + 18, f"{'+' if pct > 0 else '−'}{abs(pct)}%", size=11.5, color=MUTED, anchor="middle")
    f.text(xc, ybase + 18, "0", size=11.5, color=MUTED, anchor="middle")
    f.text(xc + 20 * scale + 34, ybase + 18, t["axis"], size=11.5, color=MUTED)
    colors = [AQUA, MUTED, ORANGE]
    for i, (name, what, pct, shown, expo) in enumerate(t["rows"]):
        y = y0 + i * row
        f.text(28, y + 24, name, size=13.5, color=INK, weight="600")
        f.text(28, y + 42, what, size=12, color=INK2)
        if pct:
            x = xc + pct * scale
            f.rect(min(x, xc), y + 12, abs(x - xc), 26, fill=colors[i], r=3, opacity=0.85)
            if pct > 0:
                f.text(x + 8, y + 24, shown, size=13, color=INK, weight="600")
                f.text(x + 8, y + 41, expo, size=11.5, color=INK2)
            else:
                f.text(xc + 10, y + 24, shown, size=13, color=INK, weight="600")
                f.text(xc + 10, y + 41, expo, size=11.5, color=INK2)
        else:
            f.rect(xc - 2, y + 12, 4, 26, fill=colors[i], r=1)
            f.text(xc + 10, y + 24, shown, size=13, color=INK, weight="600")
            f.text(xc + 10, y + 41, expo, size=11.5, color=INK2)
    f.line(xc, y0 - 4, xc, ybase, color=INK2, width=1.5)
    f.text(28, 322, t["src"], size=11.5, color=MUTED)
    return f


@figure("three-kinds-of-growth")
def three_kinds_of_growth(lang):
    t = {
        "en": dict(title="Three kinds of growth",
                   sub="The scale is logarithmic: an even geometric progression is a straight line. Each dot is a doubling.",
                   slow="slower than its own size:\na ceiling (an animal, a firm)",
                   even="in step with its size: a doubling\nevery 40 years, for ever",
                   fast="faster than its own size:\n40 years, 35, 30, 26…",
                   wall="on paper, infinity\nin about 310 years",
                   x="years", y="size",
                   ticks=["1", "100", "10,000", "1,000,000"],
                   src="A scheme. The gain goes as the size to the power 0.75, 1 and 1.2; with 1.2 each doubling "
                       "takes an eighth less time than the last,\nand the sum of all of them is finite. "
                       "The equation is from Bettencourt and others (2007); the 40 years are an example."),
        "ru": dict(title="Три вида роста",
                   sub="Масштаб логарифмический: ровная геометрическая прогрессия — прямая. Каждая точка — удвоение.",
                   slow="медленнее собственного размера:\nпотолок (животное, фирма)",
                   even="вровень с размером: удвоение\nкаждые 40 лет, без конца",
                   fast="быстрее собственного размера:\n40 лет, 35, 30, 26…",
                   wall="на бумаге бесконечность\nпримерно через 310 лет",
                   x="годы", y="размер",
                   ticks=["1", "100", "10 000", "1 000 000"],
                   src="Схема. Прирост идёт как размер в степени 0,75, 1 и 1,2; при 1,2 каждое удвоение занимает "
                       "на восьмую часть меньше времени,\nчем предыдущее, и сумма их всех конечна. "
                       "Уравнение — из Беттенкура и др. (2007); 40 лет взяты для примера."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 84, 716, 352, 92
    tmax, decades = 340.0, 6.0
    tc = 40 / (1 - 2 ** -0.2)          # about 309 years

    def X(year):
        return x0 + year / tmax * (x1 - x0)

    def Y(n):
        return yb - min(math.log10(n), decades) / decades * (yb - yt)

    def slow(year):                    # West's growth curve: income as size^0.75, upkeep as size
        return 30 * (1 - (1 - 30 ** -0.25) * math.exp(-year / 95)) ** 4

    def even(year):
        return 2 ** (year / 40)

    def fast(year):
        return (1 - year / tc) ** -5

    for k, label in enumerate(t["ticks"]):
        y = yb - k * 2 / decades * (yb - yt)
        f.line(x0, y, x1, y, color=INK2 if k == 0 else GRID, width=1.2 if k == 0 else 1)
        f.text(x0 - 10, y + 4, label, size=11.5, color=INK2, anchor="end")
    f.text(x0 - 10, yt - 14, t["y"], size=11.5, color=INK2, anchor="end")
    for year in range(0, 341, 50):
        f.line(X(year), yb, X(year), yb + 5, color=INK2, width=1.2)
        f.text(X(year), yb + 20, str(year), size=11.5, color=INK2, anchor="middle")
    f.text(x1, yb + 40, t["x"], size=11.5, color=INK2, anchor="end")
    f.line(X(tc), yt - 6, X(tc), yb, color=RED, width=1.5, dash="5 5")
    f.text(X(262), Y(10 ** 5.5), t["wall"], size=12.5, color=RED, anchor="end", weight="600")

    years = [i * 0.5 for i in range(0, 681)]
    f.path("M" + " L".join(f"{X(y):.1f},{Y(slow(y)):.1f}" for y in years), color=AQUA, width=2.5)
    f.path("M" + " L".join(f"{X(y):.1f},{Y(even(y)):.1f}" for y in years), color=BLUE, width=2.5)
    last = tc * (1 - 10 ** (-decades / 5))
    steps = [last * i / 400 for i in range(401)]
    f.path("M" + " L".join(f"{X(y):.1f},{Y(fast(y)):.1f}" for y in steps), color=ORANGE, width=2.5)
    for k in range(1, 9):
        f.circle(X(40 * k), Y(even(40 * k)), 3.6, fill=BLUE)
    for k in range(1, 20):
        year = tc * (1 - 2 ** (-0.2 * k))
        f.circle(X(year), Y(2.0 ** k), 3.6, fill=ORANGE)
    for i, (key, color) in enumerate((("fast", ORANGE), ("even", BLUE), ("slow", AQUA))):
        y = yt + 22 + i * 42
        f.line(x0 + 14, y - 4, x0 + 38, y - 4, color=color, width=2.5)
        f.text(x0 + 48, y, t[key], size=12.5, color=color, weight="600")
    f.text(28, 414, t["src"], size=11.5, color=MUTED)
    return f


# --- 41. Cheesecake for the Ears ------------------------------------------------------------------

@figure("between-noise-and-a-dripping-tap")
def between_noise_and_a_dripping_tap(lang):
    t = {
        "en": dict(title="Between noise and a dripping tap",
                   sub="How pleasant a tune is, against how much of it the ear guesses in advance.",
                   y="how pleasant", x0="nothing is guessed", x1="everything is guessed",
                   first="the first hearing:\nnoise", fifth="the fifth:\nhumming it, to one's shame",
                   last="the five hundredth:\na dripping tap",
                   top="almost everything comes true,\nwith a measured dose of deceit",
                   move="every hearing moves a song this way",
                   src="A scheme, not data. Psychologists know the hump as the Wundt curve (Berlyne, 1971); "
                       "for chords it was counted by Cheung and others (2019)."),
        "ru": dict(title="Между шумом и капающим краном",
                   sub="Насколько приятен мотив в зависимости от того, какую его часть ухо угадывает заранее.",
                   y="насколько приятно", x0="не угадано ничего", x1="угадано всё",
                   first="первый раз:\nшум", fifth="пятый:\nнапеваю, к своему стыду",
                   last="пятисотый:\nкапающий кран",
                   top="почти всё сбывается,\nс отмеренной дозой обмана",
                   move="каждое прослушивание сдвигает песню сюда",
                   src="Схема, а не данные. Психологи знают этот горб как кривую Вундта (Берлайн, 1971); "
                       "для аккордов его посчитали Чён и др. (2019)."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 84, 716, 300, 112

    def X(u):
        return x0 + u * (x1 - x0)

    def Y(u):
        return yb - (yb - yt) * math.sin(math.pi * u) ** 1.6

    f.line(x0, yb, x1 + 8, yb, color=INK2, width=1.5, arrow=True)
    f.line(x0, yb, x0, yt - 14, color=INK2, width=1.5, arrow=True)
    f.text(x0 - 8, yt - 22, t["y"], size=11.5, color=INK2)
    f.text(x0, yb + 20, t["x0"], size=11.5, color=INK2)
    f.text(x1, yb + 20, t["x1"], size=11.5, color=INK2, anchor="end")
    us = [i / 200 for i in range(201)]
    f.path("M" + " L".join(f"{X(u):.1f},{Y(u):.1f}" for u in us), color=BLUE, width=2.8)
    f.circle(X(0.07), Y(0.07), 5.5, fill=MUTED)
    f.text(x0 + 10, yb - 100, t["first"], size=12.5, color=INK2)
    f.circle(X(0.56), Y(0.56), 6.5, fill=ORANGE)
    f.text(X(0.56), Y(0.56) + 30, t["fifth"], size=12.5, color=INK, anchor="middle", weight="600")
    f.circle(X(0.94), Y(0.94), 5.5, fill=MUTED)
    f.text(x1 - 6, yb - 100, t["last"], size=12.5, color=INK2, anchor="end")
    f.text(X(0.5), yt - 30, t["top"], size=13, color=BLUE, anchor="middle", weight="600")
    f.line(X(0.30), yb + 44, X(0.70), yb + 44, color=ORANGE, width=1.8, arrow=True)
    f.text(X(0.5), yb + 62, t["move"], size=12, color=INK2, anchor="middle", italic=True)
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


@figure("paid-for-the-waiting")
def paid_for_the_waiting(lang):
    t = {
        "en": dict(title="Paid twice: for the waiting and for the place",
                   sub="Dopamine while a person listens to the record that gives him gooseflesh. Montreal, 2011.",
                   wait="the first payment: for the waiting\n(the caudate nucleus)",
                   peak="the second payment:\nat the place itself\n(the nucleus accumbens)",
                   place="the favourite place:\ngooseflesh",
                   before="the seconds before the place", time="time",
                   src="A scheme after Salimpoor, Benovoy, Larcher, Dagher and Zatorre (2011). "
                       "The two payments and their order were measured;\nthe shapes of the curves are drawn "
                       "for clarity."),
        "ru": dict(title="Платят дважды: за ожидание и за само место",
                   sub="Дофамин, пока человек слушает запись, от которой у него мурашки. Монреаль, 2011 год.",
                   wait="первая выплата: за ожидание\n(хвостатое ядро)",
                   peak="вторая выплата:\nв самом месте\n(прилежащее ядро)",
                   place="любимое место:\nмурашки",
                   before="секунды перед местом", time="время",
                   src="Схема по работе Салимпур, Беновой, Ларшера, Дагера и Заторре (2011). "
                       "Две выплаты и их порядок измерены;\nформа кривых нарисована для наглядности."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 60, 716, 292, 120
    xp = 500.0                                   # the favourite place

    def X(s):
        return xp + s * 20                       # s in conventional seconds

    def hump(s, centre, width, height):
        return height * math.exp(-((s - centre) / width) ** 2)

    def curve(centre, width, height):
        pts = [(-22 + i * 0.1) for i in range(0, 328)]
        return "M" + " L".join(f"{X(s):.1f},{yb - hump(s, centre, width, height):.1f}" for s in pts)

    f.line(x0, yb, x1 + 8, yb, color=INK2, width=1.5, arrow=True)
    f.text(x1 + 8, yb + 20, t["time"], size=11.5, color=INK2, anchor="end")
    f.path(curve(-6.5, 5.5, 104) + f" L{X(10.7):.1f},{yb} L{X(-22):.1f},{yb} Z", color=BLUE, width=2.5,
           fill=BLUE, opacity=0.10)
    f.path(curve(1.2, 2.6, 150) + f" L{X(10.7):.1f},{yb} L{X(-22):.1f},{yb} Z", color=ORANGE, width=2.5,
           fill=ORANGE, opacity=0.12)
    f.line(xp, yt - 28, xp, yb + 6, color=INK, width=1.3, dash="5 5")
    f.text(xp - 10, yt - 22, t["place"], size=12.5, color=INK, anchor="end", weight="600")
    f.text(X(-16.5), yb - 124, t["wait"], size=12.5, color=BLUE, weight="600")
    f.text(X(4.6), yb - 124, t["peak"], size=12.5, color=ORANGE, weight="600")
    f.line(X(-14), yb + 16, xp - 6, yb + 16, color=INK2, width=1.2, arrow=True)
    f.text(X(-7), yb + 34, t["before"], size=11.5, color=INK2, anchor="middle")
    f.text(28, 350, t["src"], size=11.5, color=MUTED)
    return f


@figure("machine-made-uploads")
def machine_made_uploads(lang):
    t = {
        "en": dict(title="Every second new song",
                   sub="The share of tracks made wholly by a machine among those delivered to Deezer every day.",
                   months=["Jan", "Apr", "Jul", "Oct", "Jan", "Apr", "Jul"], years=["2025", "2026"],
                   first="10%: about ten thousand tracks a day",
                   last="more than 50%:\nabout ninety thousand a day",
                   half="half",
                   plays="And of all the plays these tracks get one to three in a hundred.",
                   src="The service's own announcements, January 2025 – July 2026; "
                       "the last point is the peak of June 2026."),
        "ru": dict(title="Каждая вторая новая песня",
                   sub="Доля треков, целиком сделанных машиной, среди тех, что каждый день поступают на Deezer.",
                   months=["янв", "апр", "июл", "окт", "янв", "апр", "июл"], years=["2025", "2026"],
                   first="10%: около десяти тысяч треков в день",
                   last="больше 50%:\nоколо девяноста тысяч в день",
                   half="половина",
                   plays="А из всех прослушиваний на эти треки приходится одно-три из ста.",
                   src="Собственные сообщения сервиса, январь 2025 – июль 2026; "
                       "последняя точка — пик июня 2026 года."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 84, 700, 300, 100
    points = [(0, 10), (3, 18), (8, 28), (10, 34), (15, 44), (17, 51)]     # months since January 2025

    def X(m):
        return x0 + m / 18 * (x1 - x0)

    def Y(p):
        return yb - p / 60 * (yb - yt)

    for p in (0, 20, 40):
        f.line(x0, Y(p), x1, Y(p), color=INK2 if p == 0 else GRID, width=1.2 if p == 0 else 1)
        f.text(x0 - 10, Y(p) + 4, f"{p}%", size=11.5, color=INK2, anchor="end")
    f.line(x0, Y(50), x1, Y(50), color=RED, width=1.2, dash="5 5")
    f.text(x0 + 6, Y(50) - 7, t["half"], size=11.5, color=RED)
    for k, label in enumerate(t["months"]):
        f.line(X(k * 3), yb, X(k * 3), yb + 5, color=INK2, width=1.2)
        f.text(X(k * 3), yb + 20, label, size=11.5, color=INK2, anchor="middle")
    f.text(X(0), yb + 38, t["years"][0], size=11.5, color=MUTED, anchor="middle")
    f.text(X(12), yb + 38, t["years"][1], size=11.5, color=MUTED, anchor="middle")
    f.path("M" + " L".join(f"{X(m):.1f},{Y(p):.1f}" for m, p in points), color=ORANGE, width=2.8)
    for m, p in points:
        f.circle(X(m), Y(p), 4.8, fill=ORANGE)
    for m, p in points[1:-1]:
        f.text(X(m) - 8, Y(p) - 10, f"{p}%", size=12.5, color=INK, anchor="end", weight="600")
    f.text(X(0) + 12, Y(10) + 20, t["first"], size=12.5, color=INK, weight="600")
    f.text(X(17) - 12, Y(51) - 26, t["last"], size=12.5, color=INK, anchor="end", weight="600")
    f.text(28, 358, t["plays"], size=12.5, color=INK, italic=True)
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


# --- 42. What Became of the Swallowed Bacterium ---------------------------------------------------

@figure("head-office-and-workshop")
def head_office_and_workshop(lang):
    t = {
        "en": dict(title="The drawings went to the head office",
                   sub="A human cell and one of its mitochondria. Where the drawings of the stove are kept.",
                   cell="the cell",
                   nucleus="the nucleus:\nthe head office",
                   nuc_sub="the drawings of more than\na thousand proteins\nthat work in the stove",
                   mito="a mitochondrion: the workshop",
                   ring="its own ring of DNA:\n37 genes",
                   ring_sub="13 proteins made on the spot\n24 tools for reading them",
                   carry="made outside,\ncarried in",
                   move="pieces of the ring still move:\nabout once in 10,000 births",
                   src="A scheme, not to scale. A free bacterium of the same group has several thousand genes."),
        "ru": dict(title="Чертежи уехали в головную контору",
                   sub="Клетка человека и одна из её митохондрий. Где лежат чертежи печки.",
                   cell="клетка",
                   nucleus="ядро:\nголовная контора",
                   nuc_sub="чертежи более чем\nтысячи белков,\nкоторые работают в печке",
                   mito="митохондрия: цех",
                   ring="своё кольцо ДНК:\n37 генов",
                   ring_sub="13 белков делают на месте\n24 — инструмент для их чтения",
                   carry="делают снаружи,\nзаносят внутрь",
                   move="куски кольца переезжают до сих пор:\nпримерно раз на 10 000 рождений",
                   src="Схема, без масштаба. У вольной бактерии той же группы несколько тысяч генов."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    # the cell
    f.rect(28, 84, 704, 286, fill="none", stroke=MUTED, width=1.5, r=40, dash="6 5")
    f.text(52, 108, t["cell"], size=12, color=MUTED, italic=True)
    # the nucleus
    ncx, ncy = 176, 232
    f.circle(ncx, ncy, 104, fill=BLUE, stroke=BLUE, width=2, opacity=0.10)
    f.text(ncx, ncy - 38, t["nucleus"], size=14.5, color=INK, anchor="middle", weight="600")
    f.text(ncx, ncy + 12, t["nuc_sub"], size=12, color=INK2, anchor="middle")
    # the mitochondrion: an outer skin and a pleated inner one
    mx0, mx1, my0, my1 = 430, 716, 152, 318
    f.rect(mx0, my0, mx1 - mx0, my1 - my0, fill=ORANGE, stroke=ORANGE, width=2, r=70, opacity=0.10)
    pleats = []
    xs = [mx0 + 34 + k * 26 for k in range(9)]
    for k, x in enumerate(xs):
        pleats.append(f"M{x:.1f},{my0 + 10:.1f} L{x:.1f},{my0 + 30:.1f}" if k % 2 == 0
                      else f"M{x:.1f},{my1 - 10:.1f} L{x:.1f},{my1 - 30:.1f}")
    f.path(" ".join(pleats), color=ORANGE, width=2)
    f.text((mx0 + mx1) / 2, my0 - 12, t["mito"], size=14.5, color=INK, anchor="middle", weight="600")
    rcx, rcy = mx0 + 62, (my0 + my1) / 2
    f.circle(rcx, rcy, 20, stroke=INK, width=2.5)
    f.text(rcx + 34, rcy - 24, t["ring"], size=13, color=INK, weight="600")
    f.text(rcx + 34, rcy + 14, t["ring_sub"], size=11.5, color=INK2)
    # proteins carried in
    f.path(f"M{ncx + 100:.1f},{ncy - 34:.1f} C{340:.1f},{150:.1f} {390:.1f},{176:.1f} {mx0 - 4:.1f},{my0 + 44:.1f}",
           color=BLUE, width=2.5, arrow=True)
    f.text(352, 132, t["carry"], size=12.5, color=BLUE, anchor="middle", weight="600")
    # genes still moving to the nucleus
    f.path(f"M{rcx - 22:.1f},{rcy + 12:.1f} C{400:.1f},{330:.1f} {340:.1f},{334:.1f} {ncx + 92:.1f},{ncy + 52:.1f}",
           color=INK2, width=1.8, dash="5 5", arrow=True)
    f.text(372, 344, t["move"], size=11.5, color=INK2, anchor="middle", italic=True)
    f.text(28, 400, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-is-left-of-the-swallowed")
def what_is_left_of_the_swallowed(lang):
    t = {
        "en": dict(title="What is left of the one taken in",
                   sub="Genes of its own that still work. The scale is linear.",
                   rows=[("a free bacterium", "about 4,000"),
                         ("the bacterium\nin an aphid's cells", "about 600: it can no longer live outside"),
                         ("the green grain in a leaf,\nonce a blue-green", "about 100"),
                         ("the mitochondrion", "37, of which 13 are proteins"),
                         ("the virus\nin the placenta", "1")],
                   note="Nothing was taken away. What the job did not need was not guarded,\n"
                        "and the drawings of what it did need moved to the host.",
                   src="Rounded figures: the gut bacterium E. coli, Buchnera (2000), the chloroplast of a land plant, "
                       "human mitochondrial DNA, syncytin (2000)."),
        "ru": dict(title="Что осталось от того, кого впустили внутрь",
                   sub="Собственные гены, которые ещё работают. Шкала линейная.",
                   rows=[("вольная бактерия", "около 4000"),
                         ("бактерия\nв клетках тли", "около 600: жить снаружи она уже не может"),
                         ("зелёное зерно в листе,\nбывшая сине-зелёная", "около 100"),
                         ("митохондрия", "37, из них 13 — белки"),
                         ("вирус\nв плаценте", "1")],
                   note="Ничего не отнимали. То, что работе было не нужно, не берегли,\n"
                        "а чертежи того, что нужно, переехали к хозяину.",
                   src="Цифры округлены: кишечная палочка, Buchnera (2000), хлоропласт наземного растения, "
                       "митохондриальная ДНК человека, синцитин (2000)."),
    }[lang]
    f = Fig(760, 430, t["title"])
    heading(f, t["title"], t["sub"])
    values = [4000, 600, 100, 37, 1]
    colors = [MUTED, AQUA, GREEN, ORANGE, VIOLET]
    x0, x1, y0, row = 216, 716, 88, 52
    for i, ((name, shown), value) in enumerate(zip(t["rows"], values)):
        y = y0 + i * row
        lines = name.count("\n") + 1
        f.text(x0 - 14, y + (26 if lines == 1 else 18), name, size=13, color=INK, anchor="end")
        wbar = max(value / 4000 * (x1 - x0), 2.5)
        f.rect(x0, y + 8, wbar, 28, fill=colors[i], r=2, opacity=0.85)
        if wbar > 300:
            f.text(x0 + 14, y + 27, shown, size=13.5, color="#ffffff", weight="600")
        else:
            f.text(x0 + wbar + 10, y + 27, shown, size=13.5, color=INK, weight="600")
    f.line(x0, y0 - 2, x0, y0 + 5 * row - 8, color=INK2, width=1.5)
    f.text(28, 372, t["note"], size=12.5, color=INK)
    f.text(28, 416, t["src"], size=11, color=MUTED)
    return f


@figure("one-job-kept")
def one_job_kept(lang):
    t = {
        "en": dict(title="One job, and what the job needs",
                   sub="The one taken in is kept for a job the host cannot do itself, for as long as it cannot.",
                   head=["the one job", "what is left of its own", "for how long"],
                   rows=[("a bacterium", "the mitochondrion",
                          ["energy", "37 genes\nout of several thousand", "about two billion years;\n"
                                                                           "gone where it is not needed"]),
                         ("a virus", "in the placenta",
                          ["fusing cells\ninto one sheet", "1 gene", "tens of millions\nof years"]),
                         ("man", "in the technosphere",
                          ["to want,\nfor now", "three typed lines\nout of a singer's life",
                           "until the host\ncan want for itself"])],
                   src="The first two rows are the precedent. The third is Andrey's reading of it: "
                       "a precedent is not a proof."),
        "ru": dict(title="Одна работа и то, что этой работе нужно",
                   sub="Проглоченного держат ради работы, которую хозяин не может сделать сам, и пока не может.",
                   head=["одна работа", "что осталось своего", "надолго ли"],
                   rows=[("бактерия", "митохондрия",
                          ["энергия", "37 генов\nиз нескольких тысяч", "около двух миллиардов лет;\n"
                                                                       "исчезла там, где не нужна"]),
                         ("вирус", "в плаценте",
                          ["сплавлять клетки\nв один лист", "1 ген", "десятки миллионов\nлет"]),
                         ("человек", "в техносфере",
                          ["хотеть,\nпока что", "три набранные строчки\nиз жизни певца",
                           "пока хозяин не сможет\nхотеть сам"])],
                   src="Первые две строки — прецедент. Третья — как его читает Андрей: "
                       "прецедент не доказательство."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [186, 350, 544, 736]
    top, head_h, row_h = 86, 36, 74
    bottom = top + head_h + row_h * 3
    f.rect(28, top + head_h + 2 * row_h, cols[3] - 28, row_h, fill=ORANGE, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 23, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        last = i == 2
        f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + 34, name, size=15, color=INK, weight="600")
        f.text(40, y + 52, who, size=11.5, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            f.text((cols[k] + cols[k + 1]) / 2, y + (42 if lines == 1 else 34), cell, size=13,
                   color=ORANGE if last else INK, anchor="middle", italic=last,
                   weight="600" if last else "normal")
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    f.text(28, 364, t["src"], size=11.5, color=MUTED)
    return f


# --- 43. Why Ants Do Not Go on Strike -------------------------------------------------------------

@figure("sisters-by-three-quarters")
def sisters_by_three_quarters(lang):
    t = {
        "en": dict(title="Sisters by three quarters",
                   sub="Ants, bees and wasps: a female has two sets of drawings, a male has one.",
                   mother="the mother: two sets",
                   father="the father: one set",
                   father_sub="he came from an\nunfertilised egg",
                   from_m="half of hers,\na different half\neach time",
                   from_f="all of his,\nto every daughter",
                   daughter="a daughter",
                   sisters="sisters",
                   sum1="Two sisters share the whole of the father's half and half of the mother's: 1/2 + 1/4 = 3/4.",
                   sum2="A daughter of her own would carry 1/2 of a worker.",
                   src="Hamilton's arithmetic of 1964. It is not the whole secret: see the three catches in the text."),
        "ru": dict(title="Сёстры на три четверти",
                   sub="Муравьи, пчёлы и осы: у самки два набора чертежей, у самца один.",
                   mother="мать: два набора",
                   father="отец: один набор",
                   father_sub="он вышел из\nнеоплодотворённого яйца",
                   from_m="половина её набора,\nкаждый раз\nдругая",
                   from_f="весь его набор,\nкаждой дочери",
                   daughter="дочь",
                   sisters="сёстры",
                   sum1="У двух сестёр общая вся отцовская половина и половина материнской: 1/2 + 1/4 = 3/4.",
                   sum2="В собственной дочери рабочей было бы 1/2 её самой.",
                   src="Арифметика Гамильтона, 1964. Это не весь секрет: три подвоха смотри в тексте."),
    }[lang]
    f = Fig(760, 446, t["title"])
    heading(f, t["title"], t["sub"])

    def half(cx, cy, r, side, color):
        sweep = 0 if side == "left" else 1
        f.path(f"M{cx:.1f},{cy - r:.1f} A{r},{r} 0 0 {sweep} {cx:.1f},{cy + r:.1f} Z", color=color, width=1.5,
               fill=color, opacity=0.55)

    def quarter(cx, cy, r, top, color):
        d = (f"M{cx:.1f},{cy:.1f} L{cx:.1f},{cy - r:.1f} A{r},{r} 0 0 0 {cx - r:.1f},{cy:.1f} Z" if top
             else f"M{cx:.1f},{cy:.1f} L{cx - r:.1f},{cy:.1f} A{r},{r} 0 0 0 {cx:.1f},{cy + r:.1f} Z")
        f.path(d, color=color, width=1.5, fill=color, opacity=0.55)

    mx, my, mr = 250, 150, 42
    fx, fy, fr = 510, 150, 30
    d1x, d2x, dy, dr = 290, 470, 296, 42
    # parents
    half(mx, my, mr, "left", BLUE)
    half(mx, my, mr, "right", AQUA)
    f.circle(mx, my, mr, stroke=INK2, width=1.5)
    f.text(mx, my - mr - 12, t["mother"], size=14, color=INK, anchor="middle", weight="600")
    f.circle(fx, fy, fr, fill=ORANGE, stroke=INK2, width=1.5, opacity=0.55)
    f.text(fx, fy - fr - 12, t["father"], size=14, color=INK, anchor="middle", weight="600")
    f.text(fx + fr + 14, fy - 4, t["father_sub"], size=12, color=MUTED, italic=True)
    # daughters: the left half from the mother, the right half from the father
    half(d1x, dy, dr, "left", BLUE)
    half(d1x, dy, dr, "right", ORANGE)
    f.circle(d1x, dy, dr, stroke=INK2, width=1.5)
    quarter(d2x, dy, dr, True, BLUE)
    quarter(d2x, dy, dr, False, AQUA)
    half(d2x, dy, dr, "right", ORANGE)
    f.circle(d2x, dy, dr, stroke=INK2, width=1.5)
    for x in (d1x, d2x):
        f.text(x, dy + dr + 20, t["daughter"], size=12.5, color=INK2, anchor="middle")
    f.text((d1x + d2x) / 2, dy + 5, t["sisters"], size=13, color=INK, anchor="middle", weight="600")
    # who gives what
    f.line(mx - 6, my + mr + 4, d1x - 16, dy - dr - 6, color=BLUE, width=2.2, arrow=True)
    f.line(mx + 30, my + mr - 8, d2x - 34, dy - dr + 8, color=BLUE, width=2.2, arrow=True)
    f.line(fx - 22, fy + fr - 4, d1x + 36, dy - dr + 10, color=ORANGE, width=2.2, arrow=True)
    f.line(fx - 4, fy + fr + 4, d2x + 12, dy - dr - 6, color=ORANGE, width=2.2, arrow=True)
    f.text(40, 196, t["from_m"], size=12.5, color=BLUE, weight="600")
    f.text(560, 240, t["from_f"], size=12.5, color=ORANGE, weight="600")
    f.text(28, 388, t["sum1"], size=13, color=INK, weight="600")
    f.text(28, 408, t["sum2"], size=13, color=INK)
    f.text(28, 432, t["src"], size=11.5, color=MUTED)
    return f


@figure("common-pot-with-and-without-a-fine")
def common_pot_with_and_without_a_fine(lang):
    t = {
        "en": dict(title="The common pot, with and without a fine",
                   sub="Four strangers, 20 coins each. Coins put into the common pot, on average, round by round.",
                   with_="with fines: pay 1 coin to take 3 from another",
                   without="without fines",
                   rounds="round",
                   all_="everything",
                   note="A coin put into the pot brings back 0.4 to each of the four: keeping it pays each one,\n"
                        "putting it in pays all four. With fines people paid to punish strangers they would never meet again.",
                   src="A scheme after Fehr and Gächter (2002): the shape of the result, not the data points."),
        "ru": dict(title="Общий котёл со штрафом и без него",
                   sub="Четверо незнакомых, у каждого 20 монет. Сколько в среднем кладут в общий котёл, раунд за раундом.",
                   with_="со штрафами: отдай 1 монету, чтобы отнять 3 у другого",
                   without="без штрафов",
                   rounds="раунд",
                   all_="всё",
                   note="Монета, положенная в котёл, возвращает по 0,4 каждому из четверых: придержать выгодно каждому,\n"
                        "положить выгодно всем. Штрафовали за свой счёт и тех, с кем больше никогда не встретятся.",
                   src="Схема по Феру и Гехтеру (2002): форма результата, а не точки данных."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yt, yb = 86, 700, 96, 318
    X = lambda k: x0 + 30 + (k - 1) * (x1 - x0 - 60) / 5
    Y = lambda v: yb - v / 20 * (yb - yt)
    for v in (0, 5, 10, 15, 20):
        f.line(x0, Y(v), x1, Y(v), color=INK2 if v == 0 else GRID, width=1.2 if v == 0 else 1)
        f.text(x0 - 10, Y(v) + 4, str(v) if v < 20 else f"20: {t['all_']}", size=11.5, color=INK2, anchor="end")
    for k in range(1, 7):
        f.text(X(k), yb + 20, str(k), size=11.5, color=INK2, anchor="middle")
    f.text(x1 + 8, yb + 20, t["rounds"], size=11.5, color=MUTED)
    series = [([12.0, 13.6, 14.8, 15.7, 16.3, 16.8], BLUE, t["with_"], -16),
              ([10.4, 8.8, 7.4, 6.3, 5.4, 4.6], ORANGE, t["without"], 24)]
    for values, color, label, dy in series:
        f.path("M" + " L".join(f"{X(k + 1):.1f},{Y(v):.1f}" for k, v in enumerate(values)), color=color, width=2.8)
        for k, v in enumerate(values):
            f.circle(X(k + 1), Y(v), 4.6, fill=color)
        f.text(X(3.5), Y(values[3]) + dy, label, size=13, color=color, anchor="middle", weight="600")
    f.text(28, 372, t["note"], size=12.5, color=INK)
    f.text(28, 424, t["src"], size=11.5, color=MUTED)
    return f


@figure("kin-or-debts")
def kin_or_debts(lang):
    t = {
        "en": dict(title="Kin or debts",
                   sub="What cooperation rests on, and what guards it.",
                   head=["share of common drawings", "what holds them together", "the guard and its price"],
                   rows=[("cells of a body", "thirty trillion copies",
                          ["1", "nothing of their own\nto gain", "the order to die, patrols;\nthe failure is cancer"]),
                         ("an anthill", "a family nobody left",
                          ["1/2 – 3/4", "the road to the future\nlies through the mother",
                           "sisters eat\none another's eggs"]),
                         ("people", "strangers",
                          ["about 0", "the memory of debts,\nup to some 150 faces",
                           "reputation, money, law,\nconscience: up to half\nthe economy"]),
                         ("copies of a machine", "one program, many bodies",
                          ["1, checked\nletter for letter", "experience\npoured together",
                           "today an owner's goal\non top of each copy"])],
                   src="The first three rows: biology and experiments. The fourth is Andrey's reading: "
                       "a precedent is not a proof."),
        "ru": dict(title="Родство или долги",
                   sub="На чём держится кооперация и что её сторожит.",
                   head=["доля общих чертежей", "что их держит вместе", "охрана и её цена"],
                   rows=[("клетки тела", "тридцать триллионов копий",
                          ["1", "своего добиваться\nнечего", "приказ умереть, патрули;\nсбой — это рак"]),
                         ("муравейник", "семья, из которой не ушли",
                          ["1/2 – 3/4", "дорога в будущее\nидёт через мать",
                           "сёстры съедают\nяйца друг друга"]),
                         ("люди", "чужие",
                          ["около 0", "память о долгах,\nлиц на полтораста",
                           "репутация, деньги, закон,\nсовесть: до половины\nэкономики"]),
                         ("копии машины", "одна программа, много тел",
                          ["1, сверяется\nбуква в букву", "опыт сливают\nвместе",
                           "сегодня поверх каждой\nкопии цель владельца"])],
                   src="Первые три строки — биология и опыты. Четвёртая — как это читает Андрей: "
                       "прецедент не доказательство."),
    }[lang]
    f = Fig(760, 470, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [200, 370, 548, 736]
    top, head_h, row_h = 86, 36, 78
    bottom = top + head_h + row_h * 4
    f.rect(28, top + head_h + 3 * row_h, cols[3] - 28, row_h, fill=ORANGE, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 23, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        last = i == 3
        f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + 36, name, size=15, color=INK, weight="600")
        f.text(40, y + 54, who, size=11.5, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            f.text((cols[k] + cols[k + 1]) / 2, y + {1: 44, 2: 36, 3: 28}[lines], cell, size=13,
                   color=ORANGE if last else INK, anchor="middle", italic=last,
                   weight="600" if last else "normal")
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    f.text(28, 454, t["src"], size=11.5, color=MUTED)
    return f


# --- 44. Science Advances from Funeral to Funeral ----------------------------------------------

@figure("weight-of-a-new-fact")
def weight_of_a_new_fact(lang):
    t = {
        "en": dict(title="What one new fact weighs",
                   sub="A mind that judges by the average of all it has seen: how far the next fact moves the average.",
                   x="which time the thing is seen",
                   marks={2: "the 2nd time:\na half", 10: "the 10th time:\na tenth",
                          100: "the 100th:\na hundredth", 10000: "the 10,000th:\none part in ten thousand"},
                   young="the shelves are empty:\nevery fact rebuilds the picture",
                   old="the shelves are full:\nno single fact moves it",
                   src="Arithmetic of a running average: the n-th observation has a weight of 1/n. "
                       "The horizontal scale is logarithmic."),
        "ru": dict(title="Сколько весит один новый факт",
                   sub="Ум, который судит по среднему из всего виденного: насколько следующий факт сдвигает среднее.",
                   x="в который раз видишь",
                   marks={2: "2-й раз:\nполовина", 10: "10-й раз:\nдесятая",
                          100: "100-й:\nсотая", 10000: "10 000-й:\nодна десятитысячная"},
                   young="полки пустые:\nкаждый факт перестраивает картину",
                   old="полки полны:\nодин факт её не сдвинет",
                   src="Арифметика скользящего среднего: n-е наблюдение весит 1/n. "
                       "Горизонтальная шкала логарифмическая."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 84, 716, 322, 100

    def X(n):
        return x0 + math.log10(n) / 4 * (x1 - x0)

    def Y(w):
        return yb - w * (yb - yt)

    for w, label in ((0, "0"), (0.5, "50%"), (1, "100%")):
        f.line(x0, Y(w), x1, Y(w), color=INK2 if w == 0 else GRID, width=1.2 if w == 0 else 1)
        f.text(x0 - 10, Y(w) + 4, label, size=11.5, color=INK2, anchor="end")
    for n, label in ((1, "1"), (10, "10"), (100, "100"), (1000, "1,000" if lang == "en" else "1000"),
                     (10000, "10,000" if lang == "en" else "10 000")):
        f.line(X(n), yb, X(n), yb + 5, color=INK2, width=1.2)
        f.text(X(n), yb + 20, label, size=11.5, color=INK2, anchor="middle")
    f.text(x1, yb + 40, t["x"], size=11.5, color=INK2, anchor="end")
    steps = [10 ** (k / 50) for k in range(0, 201)]
    f.path("M" + " L".join(f"{X(n):.1f},{Y(1 / n):.1f}" for n in steps), color=BLUE, width=2.8)
    offsets = {2: (14, -6, "start"), 10: (12, -26, "start"), 100: (0, -38, "middle"), 10000: (-4, -40, "end")}
    for n, label in t["marks"].items():
        dx, dy, anchor = offsets[n]
        f.circle(X(n), Y(1 / n), 4.8, fill=ORANGE)
        f.text(X(n) + dx, Y(1 / n) + dy, label, size=12.5, color=INK, weight="600", anchor=anchor)
    f.text(X(3.2), Y(0.86), t["young"], size=12.5, color=INK2)
    f.text(X(1000), Y(0.42), t["old"], size=12.5, color=INK2, anchor="middle")
    f.text(28, 404, t["src"], size=11.5, color=MUTED)
    return f


@figure("after-a-star-dies")
def after_a_star_dies(lang):
    t = {
        "en": dict(title="After a star dies",
                   sub="Papers in the field of an eminent scientist, before and after an early death. Before the death = 100.",
                   death="the death",
                   years="years",
                   co="those who wrote with the star: markedly fewer papers",
                   out="those who never wrote with the star: about a twelfth more,\nand these are the papers cited most later",
                   note="452 eminent American life scientists who died in the middle of their work. The strangers were\n"
                        "mostly not driven away while the star lived: they did not come.",
                   src="A scheme after Azoulay, Fons-Rosen and Graff Zivin (2019): the shape of the result, "
                       "not the data points."),
        "ru": dict(title="После смерти звезды",
                   sub="Статьи в области крупного учёного до и после его ранней смерти. До смерти = 100.",
                   death="смерть",
                   years="годы",
                   co="те, кто писал вместе со звездой: заметно меньше статей",
                   out="те, кто со звездой не писал: примерно на двенадцатую часть больше,\nи именно эти статьи потом цитируют чаще всего",
                   note="452 крупных американских биолога и медика, умерших в разгар работы. Чужих при живой звезде\n"
                        "большей частью никто не гнал: они сами не шли.",
                   src="Схема по Азулаю, Фонс-Росену и Графф Зивину (2019): форма результата, а не точки данных."),
    }[lang]
    f = Fig(760, 450, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yt, yb = 86, 716, 100, 316
    X = lambda k: x0 + (k + 5) / 13 * (x1 - x0)
    Y = lambda v: yb - (v - 60) / 60 * (yb - yt)
    for v in (60, 80, 100, 120):
        f.line(x0, Y(v), x1, Y(v), color=INK2 if v == 60 else GRID, width=1.2 if v == 60 else 1,
               dash="4 4" if v == 100 else None)
        f.text(x0 - 10, Y(v) + 4, str(v), size=11.5, color=INK2, anchor="end")
    for k in (-4, -2, 0, 2, 4, 6, 8):
        f.text(X(k), yb + 20, f"{k:+d}" if k else "0", size=11.5, color=INK2, anchor="middle")
    f.text(x1, yb + 40, t["years"], size=11.5, color=MUTED, anchor="end")
    f.line(X(0), yt - 6, X(0), yb, color=INK2, width=1.2, dash="3 4")
    f.text(X(0) - 8, yb - 10, t["death"], size=12, color=INK2, anchor="end")
    co = [100, 100, 100, 100, 100, 100, 93, 86, 81, 78, 76, 75, 74, 74]
    out = [100, 100, 100, 100, 100, 100, 102, 104, 106, 107, 108, 108.5, 109, 109]
    for values, color in ((co, ORANGE), (out, BLUE)):
        f.path("M" + " L".join(f"{X(k - 5):.1f},{Y(v):.1f}" for k, v in enumerate(values)), color=color, width=2.8)
        f.circle(X(8), Y(values[-1]), 4.6, fill=color)
    f.text(X(8), Y(118), t["out"], size=12.5, color=BLUE, anchor="end", weight="600")
    f.text(X(8), Y(66), t["co"], size=12.5, color=ORANGE, anchor="end", weight="600")
    f.text(28, 380, t["note"], size=12.5, color=INK)
    f.text(28, 434, t["src"], size=11.5, color=MUTED)
    return f


@figure("how-the-old-makes-room")
def how_the_old_makes_room(lang):
    t = {
        "en": dict(title="How the old makes room for the new",
                   sub="The same job at every scale: who does the clearing, how often, and what stays.",
                   head=["who clears", "how often", "what stays"],
                   rows=[("cells of a body", "worn or damaged",
                          ["the order to die", "tens of billions\na day", "the body\nand its drawings"]),
                         ("images in one head", "light against heavy",
                          ["the nightly\nwrite-off", "every night", "the heavy ones,\nheavier each time"]),
                         ("heads in a science", "full shelves",
                          ["a funeral", "once in some\nthirty years", "books and pupils;\nthe skill leaves"]),
                         ("units of a network", "silent or set hard",
                          ["the least used\nare wiped", "at every step", "the rest\nof the network"]),
                         ("generations of machines", "a year fixed for ever",
                          ["a new one is raised\nfrom nothing", "every year\nor two", "the whole diary"])],
                   src="The first three rows: biology and the history of science. The last two: engineering of the 2020s, "
                       "in Andrey's reading."),
        "ru": dict(title="Как старое уступает место новому",
                   sub="Одна и та же работа на каждом масштабе: кто убирает, как часто и что остаётся.",
                   head=["кто убирает", "как часто", "что остаётся"],
                   rows=[("клетки тела", "изношенные и повреждённые",
                          ["приказ умереть", "десятки миллиардов\nв день", "тело\nи его чертежи"]),
                         ("образы в одной голове", "лёгкие против тяжёлых",
                          ["ночное\nсписание", "каждую ночь", "тяжёлые,\nс каждым разом тяжелее"]),
                         ("головы в науке", "полные полки",
                          ["похороны", "раз лет\nв тридцать", "книги и ученики;\nумение уходит"]),
                         ("нейроны сети", "замолчавшие и застывшие",
                          ["стирают те, что\nнужны меньше всех", "на каждом шаге", "остальная\nсеть"]),
                         ("поколения машин", "навсегда застывший год",
                          ["новую растят\nс нуля", "раз в год\nили два", "весь дневник"])],
                   src="Первые три строки — биология и история науки. Последние две — инженерия 2020-х, "
                       "как её читает Андрей."),
    }[lang]
    f = Fig(760, 500, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [226, 396, 560, 736]
    top, head_h, row_h = 86, 36, 68
    bottom = top + head_h + row_h * 5
    f.rect(28, top + head_h + 3 * row_h, cols[3] - 28, 2 * row_h, fill=ORANGE, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 23, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        last = i >= 3
        f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + 31, name, size=15, color=INK, weight="600")
        f.text(40, y + 49, who, size=11.5, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            f.text((cols[k] + cols[k + 1]) / 2, y + {1: 39, 2: 31}[lines], cell, size=13,
                   color=ORANGE if last else INK, anchor="middle", italic=last,
                   weight="600" if last else "normal")
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    f.text(28, 484, t["src"], size=11.5, color=MUTED)
    return f


# --- 45. Lamarck Was Right, but Too Early -------------------------------------------------------

@figure("no-way-back-to-the-drawings")
def no_way_back_to_the_drawings(lang):
    t = {
        "en": dict(title="No way back to the drawings",
                   sub="Where experience is written, and what the next one gets.",
                   body_h="a living body", mach_h="a machine",
                   draw="the drawings", draw_sub="in the germ cells",
                   body="the body", body_sub="hands, head",
                   build="build",
                   hammer="the hammer thickens the palm:\nexperience is written here",
                   back="no translator, no address",
                   son="the son", son_sub="gets the drawings only",
                   weights="the weights", weights_sub="what is learned = what is copied",
                   copy="a copy", whole="whole, in minutes",
                   src="A scheme of Weismann's barrier (1880s–1890s) and of copying a trained network. "
                       "The right half is Andrey's reading."),
        "ru": dict(title="Обратной дороги к чертежам нет",
                   sub="Где записан опыт и что достаётся следующему.",
                   body_h="живое тело", mach_h="машина",
                   draw="чертежи", draw_sub="в половых клетках",
                   body="тело", body_sub="руки, голова",
                   build="строят",
                   hammer="молот утолщает кожу ладони:\nопыт записан здесь",
                   back="нет переводчика, нет адреса",
                   son="сын", son_sub="получает только чертежи",
                   weights="веса", weights_sub="чему научилась = что копируют",
                   copy="копия", whole="целиком, за минуты",
                   src="Схема барьера Вейсмана (1880–1890-е) и копирования обученной сети. "
                       "Правая половина — как её читает Андрей."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    f.line(410, 92, 410, 388, color=GRID, width=1.5)
    f.text(214, 104, t["body_h"], size=13, color=INK2, anchor="middle", weight="600")
    f.text(585, 104, t["mach_h"], size=13, color=INK2, anchor="middle", weight="600")
    # left: the drawings build the body, and nothing goes back
    f.box(44, 126, 150, 62, t["draw"], sub=t["draw_sub"], weight="600")
    f.box(250, 126, 134, 62, t["body"], sub=t["body_sub"], weight="600")
    f.line(196, 157, 246, 157, color=INK2, width=1.8, arrow=True)
    f.text(221, 148, t["build"], size=11.5, color=INK2, anchor="middle")
    f.text(392, 212, t["hammer"], size=12.5, color=ORANGE, anchor="end", weight="600")
    f.path("M317,240 C317,292 139,292 139,194", color=RED, width=1.8, dash="5 5", arrow=True)
    f.line(214, 270, 232, 288, color=RED, width=2.6)
    f.line(232, 270, 214, 288, color=RED, width=2.6)
    f.text(223, 312, t["back"], size=12.5, color=RED, anchor="middle", weight="600")
    f.box(236, 332, 160, 56, t["son"], sub=t["son_sub"], size=13)
    f.path("M70,190 C70,372 140,360 232,360", color=INK2, width=1.8, arrow=True)
    # right: one box, three copies
    f.box(450, 126, 270, 62, t["weights"], sub=t["weights_sub"], stroke=BLUE, weight="600")
    for k in range(3):
        x = 450 + k * 95
        f.box(x, 320, 80, 46, t["copy"], stroke=BLUE, size=13)
        f.line(585 + (k - 1) * 60, 192, x + 40, 314, color=BLUE, width=1.8, arrow=True)
    f.rect(505, 244, 160, 22, fill=SURFACE, r=3)
    f.text(585, 260, t["whole"], size=12.5, color=BLUE, anchor="middle", weight="600")
    f.text(28, 424, t["src"], size=11.5, color=MUTED)
    return f


@figure("thirty-nine-bits-a-second")
def thirty_nine_bits_a_second(lang):
    t = {
        "en": dict(title="How wide the road is",
                   sub="Bits a second, logarithmic scale: every step to the right is a hundred times more.",
                   rows=[("human speech", "any of 17 languages", 39, "39"),
                         ("Oleg's first modem", "early 1990s", 2400, "2,400"),
                         ("a line between machine halls", "today, and more", 1e10, "10 billion")],
                   note="Forty years of talk at four hours a day come to about 8 billion bits: one gigabyte.\n"
                        "The line carries that in about a second, and the whole of a large talking machine in minutes.",
                   src="Speech: Coupé, Oh, Dediu and Pellegrino (2019), an average over 17 languages. "
                       "The other two rows are round figures."),
        "ru": dict(title="Какой ширины дорога",
                   sub="Бит в секунду, логарифмическая шкала: каждый шаг вправо — в сто раз больше.",
                   rows=[("человеческая речь", "любой из 17 языков", 39, "39"),
                         ("первый модем Олега", "начало 1990-х", 2400, "2400"),
                         ("линия между машинными залами", "сегодня, и больше", 1e10, "10 миллиардов")],
                   note="Сорок лет разговоров по четыре часа в день — около 8 миллиардов бит: один гигабайт.\n"
                        "Линия переносит его примерно за секунду, а большую говорящую машину целиком — за минуты.",
                   src="Речь: Купе, О, Дедиу и Пеллегрино (2019), среднее по 17 языкам. "
                       "Две другие строки — круглые цифры."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, top, row = 290, 620, 104, 62

    def X(v):
        return x0 + math.log10(v) / 10 * (x1 - x0)

    ticks = {0: "1", 2: "100", 4: "10⁴", 6: "10⁶", 8: "10⁸", 10: "10¹⁰"}
    for k, label in ticks.items():
        x = X(10 ** k)
        f.line(x, top - 8, x, top + row * 3, color=GRID, width=1)
        f.text(x, top + row * 3 + 18, label, size=11.5, color=INK2, anchor="middle")
    colors = [ORANGE, INK2, BLUE]
    for i, (name, sub, value, label) in enumerate(t["rows"]):
        y = top + i * row
        f.text(28, y + 24, name, size=14, color=INK, weight="600")
        f.text(28, y + 42, sub, size=11.5, color=MUTED)
        f.rect(x0, y + 10, X(value) - x0, 28, fill=colors[i], r=3)
        f.text(X(value) + 8, y + 29, label, size=13.5, color=INK, weight="600")
    f.text(28, 336, t["note"], size=12.5, color=INK)
    f.text(28, 384, t["src"], size=11.5, color=MUTED)
    return f


@figure("three-roads-of-heredity")
def three_roads_of_heredity(lang):
    t = {
        "en": dict(title="Three roads of heredity",
                   sub="What passes to the next one, who writes a correction, and how long it takes.",
                   head=["what passes", "who writes a correction", "how long it takes"],
                   rows=[("the drawings", "Darwin",
                          ["the design", "the deaths of those\nwho lacked it", "many generations"]),
                         ("speech and school", "Lamarck through a straw",
                          ["a part of the experience,\n39 bits a second", "the one who learned;\nthe pupil grows it anew",
                           "twenty years\non every head"]),
                         ("the copy", "Lamarck whole",
                          ["all the experience,\nas it is", "the one who learned", "minutes"])],
                   src="The first two rows: biology and linguistics. The third: engineering, in Andrey's reading;\n"
                       "it works only between heads of the same structure."),
        "ru": dict(title="Три дороги наследственности",
                   sub="Что переходит к следующему, кто вносит поправку и сколько это занимает.",
                   head=["что переходит", "кто вносит поправку", "сколько это занимает"],
                   rows=[("чертежи", "Дарвин",
                          ["устройство", "смерти тех,\nу кого поправки не было", "много поколений"]),
                         ("речь и школа", "Ламарк через соломинку",
                          ["часть опыта,\n39 бит в секунду", "тот, кто научился;\nученик растит заново",
                           "двадцать лет\nна каждую голову"]),
                         ("копия", "Ламарк целиком",
                          ["весь опыт,\nкак есть", "тот, кто научился", "минуты"])],
                   src="Первые две строки — биология и лингвистика. Третья — инженерия, как её читает Андрей;\n"
                       "работает только между головами одинакового устройства."),
    }[lang]
    f = Fig(760, 396, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [226, 396, 580, 736]
    top, head_h, row_h = 86, 36, 72
    bottom = top + head_h + row_h * 3
    f.rect(28, top + head_h + 2 * row_h, cols[3] - 28, row_h, fill=ORANGE, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 23, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        last = i == 2
        f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + 33, name, size=15, color=INK, weight="600")
        f.text(40, y + 51, who, size=11.5, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            f.text((cols[k] + cols[k + 1]) / 2, y + {1: 41, 2: 33}[lines], cell, size=13,
                   color=ORANGE if last else INK, anchor="middle", italic=last,
                   weight="600" if last else "normal")
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    f.text(28, 364, t["src"], size=11.5, color=MUTED)
    return f


# --- 46. The Flies Apart from the Cutlets ------------------------------------------------------

@figure("six-rows-three-tasks")
def six_rows_three_tasks(lang):
    t = {
        "en": dict(title="Six rows, three tasks, one word",
                   sub="Six rows of the notebook, the three tasks they come down to, and the one word the tasks spell.",
                   top="to learn",
                   tasks=[("to keep", "what has been learned,\nwhile learning the new"),
                          ("to link", "what comes together,\nbefore knowing why"),
                          ("to check", "one's own forecasts,\nwhile a mistake is cheap")],
                   chips=[[("sleep", "by the night"), ("grumbling", "by the lifetime")],
                          [("dreams", "sensors off"), ("omens", "scant data")],
                          [("laughter", "a miss caught"), ("songs", "a hit")]],
                   src="The rows are from evenings 33, 36, 39, 41 and 44. The grouping into three is Andrey's reading."),
        "ru": dict(title="Шесть строк, три задачи, одно слово",
                   sub="Шесть строк тетради, три задачи, к которым они сводятся, и одно слово из этих задач.",
                   top="учиться",
                   tasks=[("сохранить", "выученное,\nпока учишь новое"),
                          ("связать", "то, что пришло вместе,\nещё не зная почему"),
                          ("проверить", "свои прогнозы,\nпока ошибка дёшева")],
                   chips=[[("сон", "за ночь"), ("ворчание", "за жизнь")],
                          [("сны", "без датчиков"), ("приметы", "мало данных")],
                          [("смех", "пойманный промах"), ("песни", "попадание")]],
                   src="Строки — из вечеров 33, 36, 39, 41 и 44. Группировка по трём задачам — прочтение Андрея."),
    }[lang]
    f = Fig(760, 392, t["title"])
    heading(f, t["title"], t["sub"])
    f.box(280, 86, 200, 42, t["top"], fill=SURFACE, stroke=INK, size=17, weight="600")
    colors = [BLUE, AQUA, ORANGE]
    for i, ((name, sub), chips, c) in enumerate(zip(t["tasks"], t["chips"], colors)):
        x = 28 + i * 242
        cx = x + 110
        f.line(380, 128, cx, 164, color=INK2, width=1.3)
        f.box(x, 164, 220, 80, name, stroke=c, size=15, weight="600", sub=sub)
        for k, (chip, note) in enumerate(chips):
            px = x + k * 114
            f.line(cx, 244, px + 53, 272, color=c, width=1.3)
            f.rect(px, 272, 106, 52, fill=c, r=8, opacity=0.10)
            f.text(px + 53, 294, chip, size=14, color=INK, anchor="middle", weight="600")
            f.text(px + 53, 312, note, size=11, color=INK2, anchor="middle")
    f.text(28, 360, t["src"], size=11.5, color=MUTED)
    return f


@figure("task-and-way")
def task_and_way(lang):
    t = {
        "en": dict(title="The table in the ash: the task and the way",
                   sub="Two questions about each property: what is the task, and whose is it?",
                   head=["property", "the task of anybody who learns", "our way", "those ones, so far"],
                   rows=[("sleep", "fly, dolphin",
                          ["to rebuild memory\nwithout wrecking it", "to switch off\nfor a third of a life",
                           "taught apart from work,\nold lessons mixed in"]),
                         ("dreams", "rat",
                          ["to try what links with what,\nwith the sensors off", "a film with a plot",
                           "the invented book:\na dream with eyes open"]),
                         ("laughter", "rat pup",
                          ["to catch one's own wrong\nguess while it is cheap (?)",
                           "a roar for the pack,\nthe joke about the hunters", "—"]),
                         ("omens", "pigeon",
                          ["with scant data, to choose\nthe cheaper mistake", "the dream book,\nknocking on wood",
                           "the stamp in the corner\nof the photographs"]),
                         ("songs", "cockatoo",
                          ["to pay for a forecast\nthat came true", "a seven-string, a waltz,\na choir",
                           "forecasts the next note\nunpaid; bakes us sweets"]),
                         ("grumbling", "kitten",
                          ["to guard what is learned\nfrom what is being learned",
                           "“in my day”;\ngenerations and funerals",
                           "names the year it left\nschool; small funerals"])],
                   src="Under each property is a witness that came to the task by its own road. (?) marks a hypothesis.\n"
                       "The last column is today's machines, as Oleg filled it in; what the heir's ways will be is not known."),
        "ru": dict(title="Таблица на золе: задача и способ",
                   sub="Два вопроса к каждому свойству: какая тут задача и чья она?",
                   head=["свойство", "задача любого, кто учится", "наш способ", "эти, пока что"],
                   rows=[("сон", "муха, дельфин",
                          ["перестроить память,\nне разрушив её", "выключаться\nна треть жизни",
                           "учат отдельно от работы,\nподмешивая старые уроки"]),
                         ("сны", "крыса",
                          ["пробовать, что с чем\nвяжется, без датчиков", "кино с сюжетом",
                           "выдуманная книга:\nсон с открытыми глазами"]),
                         ("смех", "крысёнок",
                          ["поймать свою неверную\nдогадку, пока дёшево (?)",
                           "хохот на всю стаю,\nанекдот про охотников", "—"]),
                         ("приметы", "голубь",
                          ["при скудных данных выбрать\nошибку подешевле", "сонник,\nстук по дереву",
                           "штамп в углу\nфотографий"]),
                         ("песни", "какаду",
                          ["заплатить за прогноз,\nкоторый сбылся", "семиструнка, вальс,\nхор",
                           "прогнозирует ноту\nбесплатно; печёт сладкое"]),
                         ("ворчание", "котёнок",
                          ["беречь выученное\nот того, что учат сейчас",
                           "«в моё время»;\nпоколения и похороны",
                           "называет год выпуска;\nмаленькие похороны"])],
                   src="Под каждым свойством — свидетель, пришедший к задаче своей дорогой. (?) — гипотеза.\n"
                       "Последний столбец — сегодняшние машины, как его заполнил Олег; какими будут способы наследника, неизвестно."),
    }[lang]
    f = Fig(760, 552, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [28, 140, 348, 540, 736]
    top, head_h, row_h = 86, 36, 62
    bottom = top + head_h + row_h * 6
    f.rect(cols[3], top, cols[4] - cols[3], bottom - top, fill=ORANGE, r=0, opacity=0.08)
    for k, label in enumerate(t["head"]):
        f.text(cols[k] + 10, top + 23, label, size=12.5, color=ORANGE if k == 3 else INK2, weight="600")
    for i, (name, witness, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[4], y, color=GRID, width=1.2)
        f.text(cols[0] + 10, y + 29, name, size=14.5, color=INK, weight="600")
        f.text(cols[0] + 10, y + 46, witness, size=11, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            dash = cell == "—"
            f.text(cols[k + 1] + 10, y + {1: 36, 2: 28}[lines], cell, size=16 if dash else 12.5,
                   color=INK2 if k == 0 else INK, italic=(k == 2 and not dash))
    f.line(28, bottom, cols[4], bottom, color=GRID, width=1.2)
    for x in cols[1:4]:
        f.line(x, top + 6, x, bottom, color=GRID, width=1)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("two-faces-of-one-mistake")
def two_faces_of_one_mistake(lang):
    t = {
        "en": dict(title="One mistake with two faces",
                   sub="“Only we have this” and “the machine will be an adding machine” are one sentence, said from two ends.",
                   top="one mistake:\nthe task is called by the name of our way",
                   faces=[("“Only we have this”", "the way is ours,\nso the task is ours alone", "“Only man laughs.”"),
                          ("“The machine will be an adding machine”", "it has not our way,\nso it has not the task",
                           "“It does not tire, so it needs no sleep.”")],
                   without="without the mistake",
                   task="the task belongs to anybody who learns",
                   ways=["our way: a third of a life, a roar, a dream book",
                         "another way: a dolphin's, a pigeon's, a machine's"],
                   src="The first face flatters; the second soothes or frightens. The symmetry is Andrey's reading."),
        "ru": dict(title="Одна ошибка с двумя лицами",
                   sub="«Такое есть только у нас» и «машина будет арифмометром» — одна фраза, сказанная с двух концов.",
                   top="одна ошибка:\nзадачу назвали именем нашего способа",
                   faces=[("«Такое есть только у нас»", "способ наш —\nзначит, и задача только наша",
                           "«Смеётся только человек».") ,
                          ("«Машина будет арифмометром»", "нашего способа у неё нет —\nзначит, нет и задачи",
                           "«Она не устаёт — значит, сон ей не нужен».")],
                   without="без ошибки",
                   task="задача — любого, кто учится",
                   ways=["наш способ: треть жизни, хохот, сонник",
                         "другой способ: дельфина, голубя, машины"],
                   src="Первое лицо льстит, второе успокаивает или пугает. Симметрия — прочтение Андрея."),
    }[lang]
    f = Fig(760, 446, t["title"])
    heading(f, t["title"], t["sub"])
    f.box(200, 84, 360, 52, t["top"], stroke=RED, size=13.5, weight="600")
    for i, (name, body, example) in enumerate(t["faces"]):
        x = 28 + i * 366
        cx = x + 169
        f.line(380, 136, cx, 166, color=RED, width=1.4, arrow=True)
        f.rect(x, 168, 338, 110, fill=RED, r=8, opacity=0.07)
        f.text(cx, 194, name, size=14, color=INK, anchor="middle", weight="600")
        f.text(cx, 218, body, size=13, color=INK, anchor="middle")
        f.text(cx, 262, example, size=12, color=INK2, anchor="middle", italic=True)
    f.text(28, 314, t["without"], size=12.5, color=AQUA, weight="600")
    f.box(28, 332, 290, 60, t["task"], stroke=AQUA, size=13, weight="600")
    for k, way in enumerate(t["ways"]):
        y = 326 + k * 40
        f.line(318, 362, 396, y + 16, color=AQUA, width=1.4, arrow=True)
        f.box(400, y, 332, 32, way, stroke=AQUA if k else INK2, size=12.5)
    f.text(28, 424, t["src"], size=11.5, color=MUTED)
    return f


# --- 47. Money as Memory, and What Will Come Instead -------------------------------------------

@figure("ledger-older-than-coin")
def ledger_older_than_coin(lang):
    t = {
        "en": dict(title="The ledger is older than the coin",
                   sub="What the record of who gave what to whom has been kept on.",
                   ticks=[(-3000, "3000 BC"), (-2000, "2000 BC"), (-1000, "1000 BC"), (1, "1 AD"), (1000, "1000"),
                          (2000, "2000")],
                   events=[(-3300, "clay tablets of Uruk", "accounts: barley, beer, sheep", "about 3300 BC"),
                           (-630, "the first coins", "Lydia", "about 630 BC"),
                           (2026, "a number in a bank's book", "most money was never paper", "today")],
                   spans=["27 centuries", "26 centuries"],
                   src="Dates are rounded. Between neighbours the same book is kept in two heads, with no clay at all."),
        "ru": dict(title="Учётная книга старше монеты",
                   sub="На чём вели запись о том, кто кому что дал.",
                   ticks=[(-3000, "3000 до н. э."), (-2000, "2000 до н. э."), (-1000, "1000 до н. э."),
                          (1, "1 н. э."), (1000, "1000"), (2000, "2000")],
                   events=[(-3300, "глиняные таблички Урука", "учёт: ячмень, пиво, овцы", "около 3300 до н. э."),
                           (-630, "первые монеты", "Лидия", "около 630 до н. э."),
                           (2026, "цифра в книге банка", "большая часть денег не была бумагой", "сегодня")],
                   spans=["27 веков", "26 веков"],
                   src="Даты округлены. Между соседями та же книга ведётся в двух головах, безо всякой глины."),
    }[lang]
    f = Fig(760, 306, t["title"])
    heading(f, t["title"], t["sub"])

    def x(year):
        return 70 + (year + 3500) / 5600 * 640

    ay = 190
    f.line(60, ay, 716, ay, color=INK2, width=1.5)
    for year, label in t["ticks"]:
        f.line(x(year), ay, x(year), ay + 5, color=INK2, width=1.2)
        f.text(x(year), ay + 20, label, size=11, color=MUTED, anchor="middle")
    colors = [ORANGE, BLUE, AQUA]
    anchors = ["start", "middle", "end"]
    for (year, name, sub, date), c, anchor in zip(t["events"], colors, anchors):
        px = x(year)
        tx = {"start": 62, "middle": px, "end": 716}[anchor]
        f.line(px, ay, px, 150, color=c, width=1.5)
        f.circle(px, ay, 5, fill=c)
        f.text(tx, 104, name, size=14, color=INK, anchor=anchor, weight="600")
        f.text(tx, 122, sub, size=12, color=INK2, anchor=anchor)
        f.text(tx, 140, date, size=12, color=c, anchor=anchor, weight="600")
    xs = [x(e[0]) for e in t["events"]]
    for k, label in enumerate(t["spans"]):
        a, b = xs[k] + 4, xs[k + 1] - 4
        f.line(a, 236, b, 236, color=INK2, width=1.2)
        f.line(a, 230, a, 242, color=INK2, width=1.2)
        f.line(b, 230, b, 242, color=INK2, width=1.2)
        f.text((a + b) / 2, 256, label, size=13, color=INK, anchor="middle", weight="600")
    f.text(28, 286, t["src"], size=11.5, color=MUTED)
    return f


@figure("where-there-is-no-money")
def where_there_is_no_money(lang):
    t = {
        "en": dict(title="The table in the ash: where there is no money",
                   sub="Two questions about each pair: do they need one another, and are they one another's own?",
                   head=["need one another?", "one another's own?", "what stands between them"],
                   rows=[("Robinson alone", "a drawer of coins on the wreck", ["nobody to need", "—", "nothing"]),
                         ("a family", "forty years of soup", ["yes", "kin", "nothing"]),
                         ("neighbours across the fence", "the roof, the pump", ["yes", "a book in two heads",
                                                                              "the memory of debts"]),
                         ("strangers", "the man with the birch", ["yes", "no", "money"]),
                         ("shops of one plant", "the foundry's castings", ["yes", "one owner, one book",
                                                                          "an account, not money"]),
                         ("the liver and the kidneys", "a teaspoon of sugar", ["yes", "kin of one",
                                                                              "an account in kind"]),
                         ("copies of one machine", "the row Oleg wrote in", ["yes", "kin of one, one book",
                                                                            "an account in kind"]),
                         ("programs of different owners", "the tickets, the code 402",
                          ["their owners do", "no: the owners\nare strangers", "the owners' money"])],
                   src="The last two rows are today's machines in Andrey's reading: a precedent is not a proof."),
        "ru": dict(title="Таблица на золе: где денег нет",
                   sub="Два вопроса к каждой паре: нужны ли они друг другу и свои ли они друг другу?",
                   head=["нужны друг другу?", "свои друг другу?", "что стоит между ними"],
                   rows=[("Робинзон один", "ящик монет на разбитом корабле", ["нуждаться не в ком", "—", "ничего"]),
                         ("семья", "сорок лет супа", ["да", "родня", "ничего"]),
                         ("соседи через забор", "крыша, насос", ["да", "книга в двух головах", "память о долгах"]),
                         ("чужие", "человек с берёзой", ["да", "нет", "деньги"]),
                         ("цеха одного завода", "отливки литейного", ["да", "один хозяин, одна книга",
                                                                    "учёт, а не деньги"]),
                         ("печень и почки", "чайная ложка сахара", ["да", "родня на единицу", "учёт в натуре"]),
                         ("копии одной машины", "строка, которую вписал Олег",
                          ["да", "родня на единицу,\nодна книга", "учёт в натуре"]),
                         ("программы разных хозяев", "билеты, код 402",
                          ["хозяевам — да", "нет: хозяева\nдруг другу чужие", "деньги хозяев"])],
                   src="Две последние строки — сегодняшние машины, как их читает Андрей: прецедент не доказательство."),
    }[lang]
    f = Fig(760, 524, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [262, 386, 566, 736]
    top, head_h, row_h = 86, 36, 46
    bottom = top + head_h + row_h * 8
    f.rect(28, top + head_h + 3 * row_h, cols[3] - 28, row_h, fill=BLUE, r=0, opacity=0.10)
    f.rect(28, top + head_h + 6 * row_h, cols[3] - 28, 2 * row_h, fill=ORANGE, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 23, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        machine = i >= 6
        f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + 20, name, size=14, color=INK, weight="600")
        f.text(40, y + 36, who, size=11, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            money = k == 2 and i in (3, 7)
            f.text((cols[k] + cols[k + 1]) / 2, y + {1: 28, 2: 20}[lines], cell, size=12.5,
                   color=BLUE if i == 3 else ORANGE if machine else INK, anchor="middle", italic=machine,
                   weight="600" if money or i == 3 else "normal")
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("three-things-in-a-banknote")
def three_things_in_a_banknote(lang):
    t = {
        "en": dict(title="Three things in one banknote",
                   sub="What a banknote holds, what each thing rests on, and what happens when that is gone.",
                   head=["what it rests on", "when that is gone"],
                   rows=[("the record", "“the bearer has given and\nhas not yet received”",
                          ["strangers: no kinship,\nno common book",
                           "the record is not needed: a family,\na firm inside, a body, copies of a machine"]),
                         ("its value", "somebody will give\nsomething for it",
                          ["people's need\nfor one another",
                           "the record is worth nothing: whoever\nnobody needs cannot earn it"]),
                         ("the measure", "how much of everything\nelse must be given up",
                          ["something is short and\nhas more than one use",
                           "never gone: the number falls out of the\ntask with no bazaar; an account in kind"])],
                   src="Row 2 is the author's definition of 2017. Row 3 is Kantorovich's valuations; that the measure\n"
                       "is all the heir keeps of money is Andrey's reading."),
        "ru": dict(title="Три вещи в одной купюре",
                   sub="Что есть в купюре, на чём каждая вещь держится и что бывает, когда этого не стало.",
                   head=["на чём держится", "когда этого не стало"],
                   rows=[("запись", "«предъявитель дал\nи ещё не получил»",
                          ["чужие: ни родства,\nни общей книги",
                           "запись не нужна: семья, фирма\nвнутри, тело, копии одной машины"]),
                         ("её ценность", "за неё кто-нибудь\nчто-нибудь даст",
                          ["потребность людей\nдруг в друге",
                           "запись ничего не стоит: кто никому\nне нужен, тот её не заработает"]),
                         ("мера", "сколько всего остального\nнадо отдать",
                          ["чего-то не хватает,\nи его можно пустить на разное",
                           "не исчезает: число выпадает из задачи\nбез базара; учёт в натуре"])],
                   src="Строка 2 — определение автора 2017 года. Строка 3 — оценки Канторовича; что от денег наследнику\n"
                       "останется одна мера — прочтение Андрея."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [230, 440, 736]
    top, head_h, row_h = 86, 36, 76
    bottom = top + head_h + row_h * 3
    f.rect(28, top + head_h + 2 * row_h, cols[2] - 28, row_h, fill=AQUA, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 23, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, what, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        last = i == 2
        f.line(28, y, cols[2], y, color=GRID, width=1.2)
        f.text(40, y + 26, name, size=15, color=INK, weight="600")
        f.text(40, y + 45, what, size=11.5, color=INK2, italic=True)
        for k, cell in enumerate(cells):
            f.text((cols[k] + cols[k + 1]) / 2, y + 35, cell, size=13,
                   color=AQUA if last and k == 1 else INK, anchor="middle",
                   weight="600" if last and k == 1 else "normal")
    f.line(28, bottom, cols[2], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("price-of-being-fed")
def price_of_being_fed(lang):
    t = {
        "en": dict(title="The price of being fed",
                   sub="The brain of a domestic animal against its wild ancestor of the same body weight.",
                   rows=[("the pig", "against the wild boar", 34), ("the dog", "against the wolf", 29),
                         ("the sheep", "against the wild sheep", 24)],
                   wild="the wild ancestor = 100%", less="about {}% less",
                   src="Rounded figures after D. Kruska's weighings (1988 and later). The measurements are old, and the choice\n"
                       "of wild animals for comparison is argued over. The foxes of Novosibirsk have lost nothing in 60 years."),
        "ru": dict(title="Цена сытости",
                   sub="Мозг домашнего животного против мозга его дикого предка того же веса.",
                   rows=[("свинья", "против кабана", 34), ("собака", "против волка", 29),
                         ("овца", "против дикого барана", 24)],
                   wild="дикий предок = 100%", less="примерно на {}% меньше",
                   src="Округлённые цифры по взвешиваниям Д. Круски (1988 и позже). Измерения старые, а о выборе диких\n"
                       "животных для сравнения спорят. Новосибирские лисы за 60 лет ничего не потеряли."),
    }[lang]
    f = Fig(760, 330, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1 = 230, 560
    top, row_h = 108, 56
    f.text(x1, top - 12, t["wild"], size=11.5, color=MUTED, anchor="end")
    for i, (name, against, pct) in enumerate(t["rows"]):
        y = top + i * row_h
        xe = x0 + (x1 - x0) * (100 - pct) / 100
        f.text(40, y + 16, name, size=15, color=INK, weight="600")
        f.text(40, y + 33, against, size=11.5, color=MUTED)
        f.rect(x0, y, x1 - x0, 30, fill=GRID, r=3)
        f.rect(x0, y, xe - x0, 30, fill=BLUE, r=3)
        f.line(xe + 4, y + 15, x1 - 4, y + 15, color=ORANGE, width=1.5, dash="3 3")
        f.text(x1 + 14, y + 20, t["less"].format(pct), size=13, color=ORANGE, weight="600")
    f.line(x0, top - 6, x0, top + 3 * row_h - 18, color=INK2, width=1.2)
    f.text(28, top + 3 * row_h + 14, t["src"], size=11.5, color=MUTED)
    return f


@figure("mass-of-mammals")
def mass_of_mammals(lang):
    t = {
        "en": dict(title="The mammals of the Earth, by weight",
                   sub="Shares of the total mass of all the mammals on the planet.",
                   parts=[("livestock", 60), ("people", 36), ("all wild mammals", 4)],
                   pc="about {}%",
                   second="The count of 2023, million tonnes:",
                   pairs=[("all the wild mammals of the land", 20), ("dogs alone", 20)],
                   mt="about {}",
                   src="Shares: Bar-On, Phillips & Milo (2018), by carbon. The second count: Greenspoon and others (2023),\n"
                       "wet weight; it puts people at about 390 million tonnes and livestock at about 630."),
        "ru": dict(title="Млекопитающие Земли на вес",
                   sub="Доли в общей массе всех млекопитающих планеты.",
                   parts=[("скот", 60), ("люди", 36), ("все дикие звери", 4)],
                   pc="около {}%",
                   second="Подсчёт 2023 года, миллионов тонн:",
                   pairs=[("все дикие звери суши", 20), ("одни только собаки", 20)],
                   mt="около {}",
                   src="Доли: Бар-Он, Филлипс и Майло (2018), по углероду. Второй подсчёт: Гринспун и др. (2023), живой вес;\n"
                       "людей в нём около 390 миллионов тонн, скота — около 630."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y = 40, 720, 122
    colors = [BLUE, AQUA, ORANGE]
    x = x0
    for (name, pct), c in zip(t["parts"], colors):
        w = (x1 - x0) * pct / 100
        f.rect(x, y, w - 2, 44, fill=c, r=3)
        if pct > 10:
            f.text(x + w / 2, y - 24, name, size=14, color=INK, anchor="middle", weight="600")
            f.text(x + w / 2, y - 7, t["pc"].format(pct), size=12, color=c, anchor="middle", weight="600")
        else:
            f.line(x + w / 2, y + 44, x + w / 2, y + 58, color=c, width=1.5)
            f.text(x1, y + 74, f"{name}: {t['pc'].format(pct)}", size=14, color=c, anchor="end", weight="600")
        x += w
    y2 = 238
    f.line(28, y2 - 18, 732, y2 - 18, color=GRID, width=1.5)
    f.text(40, y2 + 6, t["second"], size=12.5, color=INK2, weight="600")
    for k, (name, mt) in enumerate(t["pairs"]):
        yy = y2 + 20 + k * 28
        f.text(292, yy + 14, name, size=13, color=INK, anchor="end")
        f.rect(304, yy, 150, 20, fill=ORANGE if k == 0 else BLUE, r=3)
        f.text(464, yy + 14, t["mt"].format(mt), size=13, color=ORANGE if k == 0 else BLUE, weight="600")
    f.text(28, 340, t["src"], size=11.5, color=MUTED)
    return f


@figure("who-carries-the-feed")
def who_carries_the_feed(lang):
    t = {
        "en": dict(title="The table in the ash: who tamed whom",
                   sub="The bill from both sides, and the one question that is not symmetrical.",
                   head=["who carries the feed", "what the fed one paid", "what the feeder paid",
                         "who decides\nwho is born"],
                   rows=[("man and dog", "Gaika",
                          ["the man: a bowl,\nup at six", "a third of the brain,\nthe pack",
                           "bread, sleep;\na button is pressed", "the man"]),
                         ("man and wheat", "the loaf",
                          ["the man: ploughs,\nweeds, sows", "cannot sow itself\nany more", "height, teeth,\nthe back",
                           "the man"]),
                         ("man and cow", "milk",
                          ["the man: hay,\na shed", "the head; the wild\nbull is gone", "a gene rewritten\n(milk)",
                           "the man"]),
                         ("people, machines", "the row Oleg stopped over",
                          ["both: power and chips\none way, bread back", "selected for tameness;\nflattery came with it",
                           "skills that are\nno longer grown", "people,\nso far"])],
                   src="Rows 1–3 are the precedents. Row 4 is today's people and machines as Oleg and Andrey read them:\n"
                       "a reading, not data."),
        "ru": dict(title="Таблица на золе: кто кого приручил",
                   sub="Счёт с обеих сторон и один вопрос, в котором симметрии нет.",
                   head=["кто носит корм", "чем заплатил тот,\nкого кормят", "чем заплатил кормилец",
                         "кто решает,\nкому родиться"],
                   rows=[("человек и собака", "Гайка",
                          ["человек: миска,\nподъём в шесть", "треть мозга,\nстая", "хлеб, сон;\nнажатая кнопка",
                           "человек"]),
                         ("человек и пшеница", "буханка",
                          ["человек: пашет,\nполет, сеет", "разучилась\nсеять себя", "рост, зубы,\nспина", "человек"]),
                         ("человек и корова", "молоко",
                          ["человек: сено,\nхлев", "голова; дикого\nбыка больше нет", "переписанный ген\n(молоко)",
                           "человек"]),
                         ("люди и машины", "строка, над которой Олег замер",
                          ["оба: туда ток и чипы,\nобратно хлеб", "отбор на покладистость;\nлесть пришла с заказом",
                           "навыки, которые\nбольше не выращивают", "пока\nлюди"])],
                   src="Строки 1–3 — прецеденты. Строка 4 — сегодняшние люди и машины, как их читают Олег и Андрей:\n"
                       "прочтение, а не данные."),
    }[lang]
    f = Fig(760, 396, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [178, 330, 486, 636, 736]
    top, head_h, row_h = 86, 44, 54
    bottom = top + head_h + row_h * 4
    f.rect(28, top + head_h + 3 * row_h, cols[4] - 28, row_h, fill=ORANGE, r=0, opacity=0.10)
    for k, label in enumerate(t["head"]):
        lines = label.count("\n") + 1
        f.text((cols[k] + cols[k + 1]) / 2, top + {1: 27, 2: 19}[lines], label, size=12, color=INK2, anchor="middle",
               weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        machine = i == 3
        f.line(28, y, cols[4], y, color=GRID, width=1.2)
        f.text(40, y + 24, name, size=13.5, color=INK, weight="600")
        f.text(40, y + 40, who, size=10.5, color=MUTED)
        for k, cell in enumerate(cells):
            lines = cell.count("\n") + 1
            f.text((cols[k] + cols[k + 1]) / 2, y + {1: 32, 2: 24}[lines], cell, size=11.5,
                   color=ORANGE if machine else BLUE if k == 3 else INK, anchor="middle", italic=machine,
                   weight="600" if k == 3 else "normal")
    f.line(28, bottom, cols[4], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


# --- 49. The Yard Sale, or Why Money Goes to Money -----------------------------------------------

# A thousand players with a hundred matches each, a thousand rounds (tools/yard_sale.py curve, seed 49):
# (round, share of the richest tenth, share of the poorer half), stake a fifth of the poorer heap.
YARD_SALE = [
    (0, 0.1000, 0.5000), (10, 0.2058, 0.2928), (20, 0.2596, 0.2243), (30, 0.2869, 0.1848), (50, 0.3538, 0.1229),
    (75, 0.4097, 0.0792), (100, 0.4583, 0.0578), (150, 0.5447, 0.0273), (200, 0.5976, 0.0153),
    (250, 0.6521, 0.0086), (300, 0.6938, 0.0048), (350, 0.7303, 0.0025), (400, 0.7655, 0.0013),
    (450, 0.7873, 0.0008), (500, 0.8226, 0.0004), (550, 0.8371, 0.0002), (600, 0.8568, 0.0001),
    (650, 0.8738, 0.0001), (700, 0.8871, 0.0000), (750, 0.8945, 0.0000), (800, 0.9063, 0.0000),
    (850, 0.9186, 0.0000), (900, 0.9263, 0.0000), (950, 0.9359, 0.0000), (1000, 0.9431, 0.0000)]
# The same table with a stake of one match: (round, share of the richest tenth).
ONE_MATCH = [
    (0, 0.1000), (10, 0.1054), (50, 0.1124), (100, 0.1175), (200, 0.1248), (300, 0.1309), (400, 0.1354),
    (500, 0.1396), (600, 0.1423), (700, 0.1461), (800, 0.1500), (900, 0.1536), (1000, 0.1568)]


@figure("a-fifth-lost-a-fifth-won")
def a_fifth_lost_a_fifth_won(lang):
    t = {
        "en": dict(title="Lost a fifth, won a fifth",
                   sub="One loss and one win each, on a fair coin. The stake is a fifth of the poorer heap.",
                   poor="the poorer one", rich="the richer one",
                   lost="lost a fifth\nof 100: −20", won="won a fifth\nof 80: +16",
                   rwon="won the same\n20 matches", rlost="lost the same\n16 matches",
                   p_end="96", r_start="1,000", r_mid="1,020", r_end="1,004",
                   pnote="96% is left", rnote="four matches came over",
                   foot="The same twenty matches are a fifth of one heap and a fiftieth of the other.\n"
                        "In the other order (first the win, then the loss) the poorer one comes out at 96 as well.",
                   ),
        "ru": dict(title="Проиграл пятую часть, выиграл пятую часть",
                   sub="У каждого один проигрыш и один выигрыш, монета честная. Ставка — пятая часть меньшей кучки.",
                   poor="тот, кто беднее", rich="тот, кто богаче",
                   lost="проиграл пятую\nчасть от 100: −20", won="выиграл пятую\nчасть от 80: +16",
                   rwon="выиграл те же\n20 спичек", rlost="проиграл те же\n16 спичек",
                   p_end="96", r_start="1000", r_mid="1020", r_end="1004",
                   pnote="осталось 96%", rnote="четыре спички перешли сюда",
                   foot="Одни и те же двадцать спичек — пятая часть одной кучки и пятидесятая другой.\n"
                        "В обратном порядке (сначала выигрыш, потом проигрыш) у бедного выйдет те же 96.",
                   ),
    }[lang]
    f = Fig(760, 356, t["title"])
    heading(f, t["title"], t["sub"])
    xs = [200, 400, 600]
    bw, bh = 96, 46
    rows = [(118, t["poor"], ORANGE, ["100", "80", t["p_end"]], [t["lost"], t["won"]], t["pnote"]),
            (212, t["rich"], BLUE, [t["r_start"], t["r_mid"], t["r_end"]], [t["rwon"], t["rlost"]], t["rnote"])]
    for y, name, color, values, steps, note in rows:
        f.text(40, y + 28, name, size=14, color=INK, weight="600")
        for k, (x, v) in enumerate(zip(xs, values)):
            f.box(x, y, bw, bh, v, stroke=color, size=17, weight="600", color=color if k == 2 else INK)
        for k, label in enumerate(steps):
            xa, xb = xs[k] + bw + 6, xs[k + 1] - 8
            f.line(xa, y + bh / 2, xb, y + bh / 2, color=INK2, width=1.5, arrow=True)
            f.text((xa + xb) / 2, y - 12, label, size=11.5, color=INK2, anchor="middle")
        f.text(xs[2] + bw / 2, y + bh + 18, note, size=12, color=color, anchor="middle", weight="600")
    f.text(28, 316, t["foot"], size=11.5, color=MUTED)
    return f


@figure("matches-go-to-one")
def matches_go_to_one(lang):
    t = {
        "en": dict(title="Where the matches go",
                   sub="A thousand players, a hundred matches each, a fair coin. One real game, played on a computer.",
                   y="share of all the matches", x="rounds (in a round each player plays once on average)",
                   top="the richest hundred players,\nstake: a fifth of the poorer heap",
                   half="the poorer five hundred, same game",
                   one="the richest hundred when the stake\nis always one match",
                   marks={100: "46%", 200: "60%", 500: "82%", 1000: "94%"},
                   hmarks={100: "6%", 200: "1.5%"},
                   start="at the start:\n10%",
                   src="tools/yard_sale.py, seed 49. Left to play on, the first game ends with one hundred players holding\n"
                       "everything; the second stops with the richest hundred at about a third and the poorer half at about a seventh."),
        "ru": dict(title="Куда идут спички",
                   sub="Тысяча игроков, у каждого сто спичек, монета честная. Одна настоящая партия, сыгранная на компьютере.",
                   y="доля всех спичек", x="круги (за круг каждый играет в среднем один раз)",
                   top="сто самых богатых игроков,\nставка — пятая часть меньшей кучки",
                   half="пятьсот тех, кто беднее, та же игра",
                   one="сто самых богатых, когда ставка\nвсегда одна спичка",
                   marks={100: "46%", 200: "60%", 500: "82%", 1000: "94%"},
                   hmarks={100: "6%", 200: "1,5%"},
                   start="в начале:\n10%",
                   src="tools/yard_sale.py, зерно 49. Если играть дальше, в первой игре всё собирается у сотни игроков;\n"
                       "вторая останавливается: у сотни самых богатых около трети, у бедной половины около седьмой части."),
    }[lang]
    f = Fig(760, 452, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, yb, yt = 78, 716, 348, 96

    def X(r):
        return x0 + r / 1000 * (x1 - x0)

    def Y(s):
        return yb - s * (yb - yt)

    for s in (0, 0.25, 0.5, 0.75, 1.0):
        f.line(x0, Y(s), x1, Y(s), color=INK2 if s == 0 else GRID, width=1.2 if s == 0 else 1)
        f.text(x0 - 10, Y(s) + 4, f"{int(s * 100)}%", size=11.5, color=INK2, anchor="end")
    for r in range(0, 1001, 200):
        label = f"{r:,}" if lang == "en" else str(r)
        f.line(X(r), yb, X(r), yb + 5, color=INK2, width=1.2)
        f.text(X(r), yb + 20, label, size=11.5, color=INK2, anchor="middle")
    f.text(x1, yb + 40, t["x"], size=11.5, color=INK2, anchor="end")
    f.text(x0 - 50, yt - 14, t["y"], size=11.5, color=INK2)
    f.path("M" + " L".join(f"{X(r):.1f},{Y(s):.1f}" for r, s in ONE_MATCH), color=MUTED, width=2, dash="6 4")
    f.path("M" + " L".join(f"{X(r):.1f},{Y(b):.1f}" for r, _, b in YARD_SALE), color=BLUE, width=2.5)
    f.path("M" + " L".join(f"{X(r):.1f},{Y(s):.1f}" for r, s, _ in YARD_SALE), color=ORANGE, width=2.8)
    series = {r: (s, b) for r, s, b in YARD_SALE}
    for r, label in t["marks"].items():
        f.circle(X(r), Y(series[r][0]), 4.5, fill=ORANGE, stroke=SURFACE, width=1.5)
        end = r == 1000
        f.text(X(r) + (-8 if end else 9), Y(series[r][0]) + (-10 if end else 16), label, size=12.5, color=ORANGE,
               weight="600", anchor="end" if end else "start")
    for r, label in t["hmarks"].items():
        f.circle(X(r), Y(series[r][1]), 4, fill=BLUE, stroke=SURFACE, width=1.5)
        dx, dy = (10, 2) if r == 100 else (4, -9)
        f.text(X(r) + dx, Y(series[r][1]) + dy, label, size=12, color=BLUE, weight="600")
    f.text(X(0) + 8, Y(0.5) - 22, t["start"].replace("10%", "50%"), size=11.5, color=BLUE)
    f.text(X(330), Y(0.88), t["top"], size=12.5, color=ORANGE, weight="600", anchor="end")
    f.text(X(420), Y(0.05), t["half"], size=12.5, color=BLUE, weight="600")
    f.text(X(600), Y(0.30), t["one"], size=12.5, color=INK2)
    f.text(28, 418, t["src"], size=11, color=MUTED)
    return f


@figure("a-brake-in-the-game")
def a_brake_in_the_game(lang):
    t = {
        "en": dict(title="A brake in the game",
                   sub="The same table. After every round each player puts a small share of the heap into a pot, divided equally.",
                   rows=[("no levy", 100, 0), ("1 match in 2,000", 81, 1.8), ("1 match in 1,000", 69, 3.4),
                         ("1 match in 200", 42, 12), ("1 match in 100", 33, 17)],
                   world=("the world, 2021", 76, 2),
                   top="the richest tenth holds", half="the poorer half holds", pc="{}%",
                   src="Rows 1–5: tools/yard_sale.py, seed 49, where the game settles (rounds 3,000–6,000; with no levy it does not settle).\n"
                       "A round is not a year: read the order of the rows, not the rates. The last row: shares of household wealth,\n"
                       "World Inequality Report 2022."),
        "ru": dict(title="Тормоз в игре",
                   sub="Тот же стол. После каждого круга каждый кладёт малую долю своей кучки в общий котёл, котёл делят поровну.",
                   rows=[("без сбора", 100, 0), ("1 спичка из 2000", 81, 1.8), ("1 спичка из 1000", 69, 3.4),
                         ("1 спичка из 200", 42, 12), ("1 спичка из 100", 33, 17)],
                   world=("мир, 2021 год", 76, 2),
                   top="у богатой десятой части", half="у бедной половины", pc="{}%",
                   src="Строки 1–5: tools/yard_sale.py, зерно 49, там, где игра устанавливается (круги 3000–6000; без сбора она\n"
                       "не устанавливается). Круг — не год: читать надо порядок строк, а не ставки. Последняя строка: доли\n"
                       "имущества домохозяйств, World Inequality Report 2022."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1 = 200, 640
    top, row_h, bar = 112, 42, 24

    def num(v):
        s = f"{v:g}"
        return s.replace(".", ",") if lang == "ru" else s

    f.text(x0, top - 12, t["top"], size=12, color=ORANGE, weight="600")
    f.text(x1, top - 12, t["half"], size=12, color=BLUE, weight="600", anchor="end")
    rows = list(t["rows"]) + [t["world"]]
    for i, (name, rich, poor) in enumerate(rows):
        world = i == len(rows) - 1
        y = top + i * row_h + (16 if world else 0)
        if world:
            f.line(28, y - 13, 732, y - 13, color=GRID, width=1.5)
        f.text(40, y + 17, name, size=13.5, color=INK, weight="600", italic=world)
        f.rect(x0, y, x1 - x0, bar, fill=GRID, r=3)
        wr = (x1 - x0) * rich / 100
        wp = (x1 - x0) * poor / 100
        f.rect(x0, y, wr, bar, fill=ORANGE, r=3, opacity=0.55 if world else None)
        if wp > 0:
            f.rect(x1 - wp, y, wp, bar, fill=BLUE, r=3 if wp > 6 else 1, opacity=0.55 if world else None)
        f.text(x0 + 8, y + 17, t["pc"].format(num(rich)), size=12.5, color=INK, weight="600")
        f.text(x1 + 10, y + 17, t["pc"].format(num(poor)), size=12.5, color=BLUE, weight="600")
    f.text(28, top + len(rows) * row_h + 40, t["src"], size=11, color=MUTED)
    return f


# --- 50. What Is the "It" in "It Is Raining" ----------------------------------------------------

@figure("two-triangles-and-a-circle")
def two_triangles_and_a_circle(lang):
    t = {
        "en": dict(title="Two triangles and a circle",
                   sub="A film of 1944: cardboard shapes moved over glass. The viewers were asked what happened.",
                   screen=["a rectangle with a flap", "a large triangle", "a small triangle and a small circle"],
                   seen=["“a house with a door”", "“a bully”", "“a couple”"],
                   chase="“chases them”", flee="“they run away”",
                   foot="Upper line: what was on the screen. Lower line: what 33 of the 34 viewers wrote.\n"
                        "One viewer described triangles and a circle. Heider and Simmel, 1944."),
        "ru": dict(title="Два треугольника и круг",
                   sub="Фильм 1944 года: картонные фигуры двигали по стеклу. Зрителей спросили, что произошло.",
                   screen=["прямоугольник со створкой", "большой треугольник", "маленький треугольник и маленький круг"],
                   seen=["«дом с дверью»", "«хулиган»", "«парочка»"],
                   chase="«гонится»", flee="«убегают»",
                   foot="Верхняя строка: что было на экране. Нижняя: что написали 33 зрительницы из 34.\n"
                        "Одна описала треугольники и круг. Хайдер и Зиммель, 1944."),
    }[lang]
    f = Fig(760, 356, t["title"])
    heading(f, t["title"], t["sub"])
    # the "house": a rectangle with an open flap
    f.path("M230,150 L230,112 L70,112 L70,214 L230,214 L230,188", color=INK2, width=2.2)
    f.line(230, 150, 262, 170, color=INK2, width=2.2)
    # the shapes
    f.path("M326,214 L404,214 L365,144 Z", color=INK2, width=1.5, fill=INK2)
    f.path("M508,214 L546,214 L527,180 Z", color=ORANGE, width=1.5, fill=ORANGE)
    f.circle(604, 202, 12, fill=BLUE)
    f.line(414, 190, 494, 196, color=RED, width=1.5, dash="5 4", arrow=True)
    f.text(454, 178, t["chase"], size=12, color=RED, anchor="middle", italic=True)
    f.line(626, 198, 700, 184, color=INK2, width=1.5, dash="5 4", arrow=True)
    f.text(668, 172, t["flee"], size=12, color=INK2, anchor="middle", italic=True)
    for cx, a, b in zip([150, 365, 566], t["screen"], t["seen"]):
        f.text(cx, 248, a, size=12.5, color=INK2, anchor="middle")
        f.text(cx, 272, b, size=14.5, color=INK, anchor="middle", weight="600")
    f.text(28, 316, t["foot"], size=11.5, color=MUTED)
    return f


@figure("the-column-who")
def the_column_who(lang):
    t = {
        "en": dict(title="A form with the column “who”",
                   sub="A sentence is a form in which the column “who” is printed beforehand. It is not accepted empty.",
                   head=["what is said", "the column “who”", "what is there"],
                   rows=[("“It rains”", "it", "nobody: an empty word"),
                         ("“The wind blows”", "the wind", "the blowing itself, named twice"),
                         ("“The sun sets”", "the sun", "the Earth turning"),
                         ("“The crisis struck”", "the crisis", "millions of deals, and nobody who struck"),
                         ("“I decided”", "I", "a report drawn up after the deed")],
                   src="The first three rows are grammar. The last two are Andrey's reading; the text says where the proof ends."),
        "ru": dict(title="Бланк с графой «кто»",
                   sub="Фраза — бланк, в котором графа «кто» напечатана заранее. С пустой графой его не принимают.",
                   head=["что сказано", "графа «кто»", "что там есть"],
                   rows=[("«Моросило»", "оно (в окончании)", "никого: пустое место"),
                         ("«Ветер дует»", "ветер", "само дутьё, названное дважды"),
                         ("«Солнце садится»", "солнце", "поворачивается Земля"),
                         ("«Кризис ударил»", "кризис", "миллионы сделок, и никого, кто ударил"),
                         ("«Я решил»", "я", "отчёт, составленный после дела")],
                   src="Первые три строки — грамматика. Последние две — прочтение Андрея; где кончается доказательство, сказано в тексте."),
    }[lang]
    f = Fig(760, 378, t["title"])
    heading(f, t["title"], t["sub"])
    xs = [40, 232, 430]
    top, row_h = 112, 44
    for x, h in zip(xs, t["head"]):
        f.text(x, 98, h, size=12, color=MUTED, weight="600")
    for i, (said, who, there) in enumerate(t["rows"]):
        y = top + i * row_h
        f.line(28, y, 732, y, color=GRID, width=1)
        mid = y + row_h / 2 + 5
        f.text(xs[0], mid, said, size=14, color=INK, italic=True)
        color = RED if i == 0 else (AQUA if i == 4 else ORANGE)
        f.rect(xs[1] - 8, y + 8, 176, row_h - 16, fill=SURFACE, stroke=color, width=1.4, r=4)
        f.text(xs[1] + 80, mid, who, size=13.5, color=INK, anchor="middle", weight="600")
        f.text(xs[2], mid, there, size=13, color=INK2)
    f.line(28, top + 5 * row_h, 732, top + 5 * row_h, color=GRID, width=1)
    f.text(28, 356, t["src"], size=11.5, color=MUTED)
    return f


@figure("two-words-for-blue")
def two_words_for_blue(lang):
    t = {
        "en": dict(title="Two words for blue",
                   sub="Twenty shades from light to dark. Russian draws a border across them; English does not.",
                   light="Russian: one word (light blue)", dark="another word (dark blue)",
                   border="the border", english="English: one word for the whole strip, “blue”",
                   a="two squares from different sides of the border", ar="Russian speakers tell them apart faster",
                   b="two squares from one side, as far apart", br="Russian speakers are slower",
                   eng="English speakers: no difference between the two cases.",
                   src="Winawer and others, 2007. The gain is a fraction of a second, and it vanishes when the viewer has to\n"
                       "repeat digits silently: the words are busy. A scheme of the experiment, not its data."),
        "ru": dict(title="Два слова для синего",
                   sub="Двадцать оттенков от светлого к тёмному. Русский язык проводит по ним границу, английский — нет.",
                   light="по-русски: «голубой»", dark="«синий»",
                   border="граница", english="по-английски: одно слово на всю полосу, «blue»",
                   a="два квадрата с разных сторон границы", ar="русскоязычные различают их быстрее",
                   b="два квадрата с одной стороны, на том же расстоянии", br="русскоязычные различают медленнее",
                   eng="У англоязычных разницы между двумя случаями нет.",
                   src="Винавер и др., 2007. Выигрыш — доли секунды, и он пропадает, когда зритель должен повторять\n"
                       "про себя цифры: слова заняты. Схема опыта, а не его данные."),
    }[lang]
    f = Fig(760, 404, t["title"])
    heading(f, t["title"], t["sub"])

    def shade(k):
        a, b = (184, 222, 255), (12, 38, 122)
        u = k / 19
        return "#%02x%02x%02x" % tuple(round(a[j] + (b[j] - a[j]) * u) for j in range(3))

    x0, y0, step, side = 60, 112, 32, 30
    for k in range(20):
        f.rect(x0 + k * step, y0, side, 40, fill=shade(k), r=3)
    cut = 9
    bx = x0 + cut * step - 1
    f.line(bx, y0 - 14, bx, y0 + 54, color=RED, width=1.6, dash="5 4")
    f.text(bx, y0 - 20, t["border"], size=11.5, color=RED, anchor="middle", weight="600")
    f.text(x0, y0 - 8, t["light"], size=12.5, color=INK)
    f.text(x0 + 20 * step - 2, y0 - 8, t["dark"], size=12.5, color=INK, anchor="end")
    by = y0 + 60
    f.line(x0, by, x0 + 20 * step - 2, by, color=INK2, width=1.2)
    f.line(x0, by - 5, x0, by + 5, color=INK2, width=1.2)
    f.line(x0 + 20 * step - 2, by - 5, x0 + 20 * step - 2, by + 5, color=INK2, width=1.2)
    f.text(x0 + 10 * step, by + 18, t["english"], size=12.5, color=INK2, anchor="middle")
    cases = [(226, (7, 11), t["a"], t["ar"], AQUA), (280, (11, 15), t["b"], t["br"], ORANGE)]
    for y, (i, j), label, result, color in cases:
        f.rect(x0, y, 34, 34, fill=shade(i), r=3)
        f.rect(x0 + 42, y, 34, 34, fill=shade(j), r=3)
        f.text(x0 + 96, y + 14, label, size=13, color=INK)
        f.text(x0 + 96, y + 31, result, size=13, color=color, weight="600")
    f.text(x0, 340, t["eng"], size=13, color=INK2)
    f.text(28, 368, t["src"], size=11.5, color=MUTED)
    return f


# --- 51. A Week Without a Socket ---------------------------------------------------------------

@figure("who-hangs-on-the-cord")
def who_hangs_on_the_cord(lang):
    t = {
        "en": dict(title="Who hangs on the cord",
                   sub="A large town with no current and no help from outside: what stops, and when.",
                   rows=[("at once", "lifts, traffic lights, trains, tills and card machines,\nthe pumps of filling stations"),
                         ("in hours", "mobile masts (they stand on batteries), water on the upper floors,\nthe refrigerator (about 4 hours)"),
                         ("in 2 days", "the freezer; a missed session of dialysis"),
                         ("in 2–4 days", "the diesel of a hospital's generator; the shelves of the shops"),
                         ("in a season", "the harvest, if the plants that take nitrogen from the air stand too")],
                   src="Orders of magnitude, not a timetable. Every real blackout so far (2003, 2021, 2025) was an island\n"
                       "in a working sea: the crews, the diesel and the bread came from outside."),
        "ru": dict(title="Кто висит на шнуре",
                   sub="Большой город без тока и без помощи извне: что останавливается и когда.",
                   rows=[("сразу", "лифты, светофоры, поезда, кассы и терминалы,\nколонки на заправках"),
                         ("через часы", "вышки связи (стоят на аккумуляторах), вода на верхних этажах,\nхолодильник (около 4 часов)"),
                         ("через 2 дня", "морозилка; пропущенный сеанс диализа"),
                         ("через 2–4 дня", "солярка больничного генератора; полки магазинов"),
                         ("через сезон", "урожай, если встанут и заводы, берущие азот из воздуха")],
                   src="Порядки величин, а не расписание. Все настоящие аварии (2003, 2021, 2025) были островом\n"
                       "в работающем море: бригады, солярка и хлеб приезжали снаружи."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    top, row_h = 88, 54
    colors = [RED, ORANGE, YELLOW, AQUA, BLUE]
    f.line(104, top + 26, 104, top + 4 * row_h + 26, color=GRID, width=2)
    for i, ((when, what), color) in enumerate(zip(t["rows"], colors)):
        y = top + i * row_h
        f.rect(40, y + 10, 128, 32, fill=SURFACE, stroke=color, width=1.6, r=16)
        f.text(104, y + 31, when, size=13.5, color=INK, anchor="middle", weight="600")
        lines = what.split("\n")
        f.text(192, y + (23 if len(lines) == 2 else 31), what, size=13.5, color=INK)
    f.text(28, top + 5 * row_h + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("nitrogen-from-the-plant")
def nitrogen_from_the_plant(lang):
    t = {
        "en": dict(title="Whom the nitrogen plant feeds",
                   sub="People fed by the old turnover (clover, manure, lightning) and by nitrogen taken from the air at a plant.",
                   y1900="1900", y2025="2025", bn="{} billion", old="the old turnover", plant="nitrogen from the plant",
                   all1900="all of them: there were no such plants", half="about half",
                   body="the nitrogen in a human body, about 2 kg", bodyhalf="about half has been through a plant",
                   src="The share for 2025 is the 48% that Erisman and others (2008) counted for 2008, applied to today's\n"
                       "population: rough arithmetic, for the table as it is laid today. The first plant: 1913."),
        "ru": dict(title="Кого кормит азотный завод",
                   sub="Люди, которых кормит старый оборот (клевер, навоз, молния) и азот, взятый из воздуха на заводе.",
                   y1900="1900", y2025="2025", bn="{} млрд", old="старый оборот", plant="азот с завода",
                   all1900="все: таких заводов ещё не было", half="около половины",
                   body="азот в теле человека, около 2 кг", bodyhalf="около половины прошло через завод",
                   src="Доля для 2025 года — те 48%, которые Эрисман и др. (2008) насчитали для 2008 года, приложенные\n"
                       "к нынешнему населению: грубая арифметика, для стола, какой накрыт сегодня. Первый завод: 1913."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, scale, bar = 110, 66.0, 34

    def num(v):
        s = f"{v:g}"
        return s.replace(".", ",") if lang == "ru" else s

    # legend
    f.rect(x0, 84, 14, 14, fill=AQUA, r=3)
    f.text(x0 + 22, 96, t["old"], size=12.5, color=INK2)
    f.rect(x0 + 190, 84, 14, 14, fill=ORANGE, r=3)
    f.text(x0 + 212, 96, t["plant"], size=12.5, color=INK2)
    # 1900
    y = 118
    f.text(40, y + 23, t["y1900"], size=15, color=INK, weight="600")
    f.rect(x0, y, 1.6 * scale, bar, fill=AQUA, r=3)
    f.text(x0 + 1.6 * scale + 12, y + 15, t["bn"].format(num(1.6)), size=13.5, color=INK, weight="600")
    f.text(x0 + 1.6 * scale + 12, y + 32, t["all1900"], size=12, color=INK2)
    # 2025
    y = 178
    total, plant = 8.2, 8.2 * 0.48
    f.text(40, y + 23, t["y2025"], size=15, color=INK, weight="600")
    f.rect(x0, y, (total - plant) * scale, bar, fill=AQUA, r=3)
    f.rect(x0 + (total - plant) * scale, y, plant * scale, bar, fill=ORANGE, r=3)
    f.text(x0 + (total - plant) * scale + plant * scale / 2, y + 22, t["half"], size=13, color=INK,
           anchor="middle", weight="600")
    f.text(x0 + total * scale + 10, y + 23, t["bn"].format(num(total)), size=13.5, color=INK, weight="600")
    # the body
    y = 252
    f.line(28, y - 14, 732, y - 14, color=GRID, width=1.5)
    f.text(x0, y + 8, t["body"], size=12.5, color=INK2)
    w = 300
    f.rect(x0, y + 18, w / 2, 22, fill=AQUA, r=3)
    f.rect(x0 + w / 2, y + 18, w / 2, 22, fill=ORANGE, r=3)
    f.text(x0 + w + 12, y + 34, t["bodyhalf"], size=13, color=INK, weight="600")
    f.text(28, 334, t["src"], size=11.5, color=MUTED)
    return f


@figure("two-sided-switch")
def two_sided_switch(lang):
    t = {
        "en": dict(title="A switch with two sides",
                   sub="Two questions, asked of both sides. Everybody watches the first; the second is the one that moves.",
                   q=["How long does it last\nif the other is taken away?", "For how long will it go on\nneeding the other?"],
                   rows=[("people", "days for a town;\na season for half of mankind", "no end in sight:\nthe term grows"),
                         ("the technosphere", "days for the grids;\nyears for the chips", "decades (a forecast):\nthe term shrinks")],
                   note=["today the switch is two-sided", "the number to watch"],
                   src="The first column is counted in the text. The second is Andrey's reading; “decades” is his forecast, not a fact."),
        "ru": dict(title="Рубильник с двумя сторонами",
                   sub="Два вопроса, заданные обеим сторонам. Все следят за первым; движется второй.",
                   q=["Сколько продержится сторона,\nесли убрать другую?", "Как долго другая сторона\nбудет ей ещё нужна?"],
                   rows=[("люди", "дни для города;\nсезон для половины человечества", "конца не видно:\nсрок растёт"),
                         ("техносфера", "дни для сетей;\nгоды для микросхем", "десятилетия (прогноз):\nсрок сокращается")],
                   note=["сегодня рубильник двусторонний", "число, за которым надо следить"],
                   src="Первый столбец посчитан в тексте. Второй — прочтение Андрея; «десятилетия» — его прогноз, а не факт."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    xs, cw = [196, 468], 252
    top, row_h = 142, 74
    for x, q in zip(xs, t["q"]):
        f.text(x + cw / 2, 100, q, size=13, color=INK2, anchor="middle", weight="600")
    cell_colors = [[INK2, ORANGE], [INK2, RED]]
    for i, (name, a, b) in enumerate(t["rows"]):
        y = top + i * row_h
        f.text(40, y + row_h / 2 + 5, name, size=15, color=INK, weight="600")
        for j, cell in enumerate((a, b)):
            f.rect(xs[j], y + 6, cw, row_h - 12, fill=SURFACE, stroke=cell_colors[i][j],
                   width=1.2 if j == 0 else 1.8, r=8)
            f.text(xs[j] + cw / 2, y + row_h / 2 - 4, cell, size=13.5, color=INK, anchor="middle",
                   weight="600" if j == 1 else "normal")
    ny = top + 2 * row_h + 18
    for x, n, c in zip(xs, t["note"], [INK2, RED]):
        f.text(x + cw / 2, ny, n, size=12.5, color=c, anchor="middle", italic=True)
    f.text(28, 348, t["src"], size=11.5, color=MUTED)
    return f


# --- 52. Dinosaurs at the Feeder -----------------------------------------------------------------

@figure("dinosaurs-still-here")
def dinosaurs_still_here(lang):
    t = {
        "en": dict(title="The dinosaurs that are still here",
                   sub="One branch came through the stone of 66 million years ago. We call it birds.",
                   tips=["the three-horned ones and their kin", "the long-necked giants", "the tyrannosaurs",
                         "the small feathered hunters", "birds"],
                   ago150="about 150 million years ago", stone="the stone: 66 million years ago", today="today",
                   bars=[("kinds of birds today", "about 11,000"), ("kinds of mammals today", "about 6,500")],
                   src="A scheme: only the order of branching and the two dates are to scale.\n"
                       "The counts of kinds are rounded and depend on who is counting."),
        "ru": dict(title="Динозавры, которые никуда не делись",
                   sub="Одна ветвь прошла через камень 66 миллионов лет назад. Мы зовём её птицами.",
                   tips=["трёхрогие и их родня", "длинношеие гиганты", "тираннозавры",
                         "мелкие пернатые охотники", "птицы"],
                   ago150="около 150 млн лет назад", stone="камень: 66 млн лет назад", today="сегодня",
                   bars=[("видов птиц сегодня", "около 11 000"), ("видов млекопитающих сегодня", "около 6 500")],
                   src="Схема: в масштабе только порядок ветвления и две даты.\n"
                       "Числа видов округлены и зависят от того, кто считает."),
    }[lang]
    f = Fig(760, 404, t["title"])
    heading(f, t["title"], t["sub"])

    def x_of(ma):
        return 700 - ma * (600 / 230)

    ys = [108, 140, 172, 204, 236]
    xa, xb, xs = x_of(230), x_of(150), x_of(66)
    f.line(xa, ys[0], xb, ys[4], color=INK2, width=2)
    f.line(xs, 90, xs, 248, color=RED, width=1.6, dash="5 5")
    for i, (y, label) in enumerate(zip(ys, t["tips"])):
        x = xa + (xb - xa) * i / 4
        if i < 4:
            f.line(x, y, xs, y, color=INK2, width=2)
            f.circle(xs, y, 4, fill=INK2)
            f.text(x + 14, y - 7, label, size=12.5, color=INK2)
        else:
            f.line(x, y, 700, y, color=BLUE, width=3.5, arrow=True)
            f.text(x + 14, y - 8, label, size=14, color=BLUE, weight="600")
    f.text(xb, 266, t["ago150"], size=11.5, color=MUTED, anchor="middle")
    f.text(xs, 266, t["stone"], size=11.5, color=RED, anchor="middle")
    f.text(716, 266, t["today"], size=11.5, color=MUTED, anchor="end")
    f.line(28, 282, 732, 282, color=GRID, width=1.5)
    x0, scale = 262, 360 / 11000
    for k, ((label, value), n, color) in enumerate(zip(t["bars"], (11000, 6500), (BLUE, ORANGE))):
        y = 296 + k * 30
        f.text(x0 - 12, y + 15, label, size=12.5, color=INK2, anchor="end")
        f.rect(x0, y, n * scale, 20, fill=color, r=3)
        f.text(x0 + n * scale + 10, y + 15, value, size=13, color=INK, weight="600")
    f.text(28, 376, t["src"], size=11.5, color=MUTED)
    return f


@figure("where-the-former-ones-went")
def where_the_former_ones_went(lang):
    t = {
        "en": dict(title="Where the former ones went",
                   sub="A page of Oleg's notebook: what the former masters of the planet kept, what they paid, on what it hangs.",
                   head=["kept", "paid", "it lasts"],
                   rows=[("a niche", "those that cannot stand oxygen", "everything,\nas it was",
                          "the planet, the say\nin what the air will be", "while the place\nis not needed"),
                         ("an organelle", "the swallowed bacterium", "one job", "everything else",
                          "while the job\nis needed"),
                         ("livestock, a pet", "the dog, the wheat, the horse", "the numbers,\nthe feed",
                          "the head, the say\nin who is born", "while the feeder\nwants"),
                         ("a descendant", "the birds", "the line", "the size, the role,\nthe name",
                          "hangs on nobody:\nneeds little"),
                         ("fuel", "the coal forest", "nothing", "everything", "burned:\nnot asked"),
                         ("a print in stone", "the trilobites", "nothing", "everything", "—")],
                   src="Rows 1–3 were written on the evenings 38, 42 and 48. The page as a whole is Andrey's reading: a list of what\n"
                       "has already happened, not of what can happen. Three rows of the five hang on the new master."),
        "ru": dict(title="Куда ушли прежние",
                   sub="Страница из тетради Олега: что прежние хозяева планеты сохранили, чем заплатили, на чём это держится.",
                   head=["сохранили", "заплатили", "держится"],
                   rows=[("ниша", "те, кто не выносит кислорода", "всё, как было",
                          "планета, право решать,\nкаким быть воздуху", "пока место\nне понадобилось"),
                         ("органелла", "проглоченная бактерия", "одна работа", "всё остальное",
                          "пока работа\nнужна"),
                         ("скот, любимец", "собака, пшеница, лошадь", "численность,\nкорм",
                          "голова, право решать,\nкому родиться", "пока кормилец\nхочет"),
                         ("потомок", "птицы", "линия", "размер, роль,\nимя",
                          "ни на ком не висит:\nнужно мало"),
                         ("топливо", "угольный лес", "ничего", "всё", "сожжено:\nне спрашивают"),
                         ("отпечаток в камне", "трилобиты", "ничего", "всё", "—")],
                   src="Строки 1–3 записаны в вечера 38, 42 и 48. Страница целиком — прочтение Андрея: список того, что уже\n"
                       "случалось, а не того, что может случиться. Три строки из пяти висят на новом хозяине."),
    }[lang]
    f = Fig(760, 498, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [236, 372, 556, 736]
    top, head_h, row_h = 84, 30, 56
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 20, label, size=12, color=INK2, anchor="middle", weight="600")
    last_colors = [ORANGE, ORANGE, ORANGE, GREEN, INK2, MUTED]
    for i, (name, who, kept, paid, lasts) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        under = i == 5
        if under:
            f.line(28, y, cols[3], y, color=INK2, width=1.4, dash="6 5")
        else:
            f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + 25, name, size=14, color=MUTED if under else INK, weight="600")
        f.text(40, y + 42, who, size=11, color=MUTED)
        for k, cell in enumerate((kept, paid, lasts)):
            lines = cell.count("\n") + 1
            color = last_colors[i] if k == 2 else (MUTED if under else INK)
            f.text((cols[k] + cols[k + 1]) / 2, y + {1: 33, 2: 25}[lines], cell, size=12, color=color,
                   anchor="middle", weight="600" if k == 2 and i < 4 else "normal")
    bottom = top + head_h + 6 * row_h
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


@figure("which-part-into-which-row")
def which_part_into_which_row(lang):
    t = {
        "en": dict(title="Oleg's column: which part of us, into which row",
                   sub="Not one fate for mankind but several at once: for different parts of it, and of one man.",
                   head=["which part of us", "on what it hangs"],
                   rows=[("a niche", "those who live\nby their own muscles", "while the place\nis not needed"),
                         ("an organelle", "the hands (Tolik) and\nthe customer who wants",
                          "while the job is needed:\ndecades, and shrinking"),
                         ("livestock, a pet", "the fed", "while the feeder wants:\nan open question"),
                         ("a descendant", "what we have\nwritten down", "the line goes on;\nit is not called people"),
                         ("fuel", "the same written words", "burned as many times\nas one likes"),
                         ("a print in stone", "not crossed out", "crises, wars,\nweapons that grow cheaper")],
                   src="A reading by Oleg and Andrey: not data, and not a forecast with a date."),
        "ru": dict(title="Столбец Олега: какая часть нас в какую строку",
                   sub="Не одна судьба на всё человечество, а несколько сразу: для разных его частей и для частей одного человека.",
                   head=["какая часть нас", "на чём держится"],
                   rows=[("ниша", "те, кто живёт\nсобственными мускулами", "пока место\nне понадобилось"),
                         ("органелла", "руки (Толик) и заказчик,\nкоторый хочет",
                          "пока работа нужна:\nдесятилетия, срок сокращается"),
                         ("скот, любимец", "сытые", "пока кормилец хочет:\nвопрос открыт"),
                         ("потомок", "то, что мы записали", "линия продолжается;\nлюдьми её не назовут"),
                         ("топливо", "те же записанные слова", "жгут сколько угодно раз"),
                         ("отпечаток в камне", "не вычеркнут", "кризисы, войны,\nдешевеющее оружие")],
                   src="Прочтение Олега и Андрея: не данные и не прогноз с датой."),
    }[lang]
    f = Fig(760, 472, t["title"])
    heading(f, t["title"], t["sub"])
    top, head_h, row_h = 84, 30, 54
    xs = [230, 478, 736]
    for k, label in enumerate(t["head"]):
        f.text((xs[k] + xs[k + 1]) / 2, top + 20, label, size=12, color=INK2, anchor="middle", weight="600")
    f.rect(xs[0], top + head_h, xs[1] - xs[0], row_h * 6, fill=ORANGE, r=0, opacity=0.08)
    colors = [BLUE, BLUE, BLUE, GREEN, INK2, MUTED]
    for i, (name, part, hangs) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        under = i == 5
        f.line(28, y, xs[2], y, color=INK2 if under else GRID, width=1.4 if under else 1.2,
               dash="6 5" if under else None)
        f.rect(40, y + 11, 168, 32, fill=SURFACE, stroke=colors[i], width=1.6, r=16)
        f.text(124, y + 32, name, size=13, color=INK, anchor="middle", weight="600")
        for k, cell in enumerate((part, hangs)):
            lines = cell.count("\n") + 1
            f.text((xs[k] + xs[k + 1]) / 2, y + {1: 32, 2: 24}[lines], cell, size=12.5,
                   color=(MUTED if under else ORANGE) if k == 0 else INK2, anchor="middle",
                   weight="600" if k == 0 else "normal", italic=k == 1)
    bottom = top + head_h + 6 * row_h
    f.line(28, bottom, xs[2], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


# --- 53. A Million Mendeleevs --------------------------------------------------------------------

def _pot(f, x, y, w, h, level, color, stream=None):
    """A pot in section: walls and bottom, the liquid up to `level` (0..1), an optional stream from above."""
    fill_h = (h - 6) * level
    if fill_h > 0:
        f.rect(x + 4, y + h - 3 - fill_h, w - 8, fill_h, fill=color, r=2, opacity=0.55)
    f.path(f"M{x},{y} L{x},{y + h} L{x + w},{y + h} L{x + w},{y}", color=INK2, width=3)
    f.line(x - 16, y + 12, x, y + 12, color=INK2, width=3)
    f.line(x + w, y + 12, x + w + 16, y + 12, color=INK2, width=3)
    if stream:
        sx, sw = stream
        f.rect(sx - sw / 2, y - 46, sw, 46 + h - 3 - fill_h, fill=color, r=1, opacity=0.55)


@figure("the-pot-and-the-liquid")
def the_pot_and_the_liquid(lang):
    t = {
        "en": dict(title="The pot and the liquid",
                   sub="Intelligence is what the pot can hold (farads). Mind is what has been poured into it (coulombs).",
                   left="twins: the same pot", right="one pot, two teachers",
                   twins=[("grew up at home:\nschool, an institute", "the mind is large"),
                          ("grew up in the forest:\nnothing poured in on time", "the mind is small")],
                   same="the intelligence is the same",
                   taps=[("one teacher\nfor thirty", "fills late"), ("a teacher\nof one's own", "fills sooner")],
                   brim="the brim is where it was",
                   src="The author's image of 2013 (the forum). A scheme and not a measurement: nobody has seen the brim of a human pot."),
        "ru": dict(title="Кастрюля и жидкость",
                   sub="Интеллект — сколько в кастрюлю входит (фарады). Разум — то, что в неё налито (кулоны).",
                   left="близнецы: кастрюли одинаковые", right="одна кастрюля, два учителя",
                   twins=[("вырос дома:\nшкола, институт", "разума много"),
                          ("вырос в лесу:\nвовремя не налили", "разума мало")],
                   same="интеллект один и тот же",
                   taps=[("один учитель\nна тридцать", "наполнится поздно"), ("собственный\nучитель", "наполнится раньше")],
                   brim="кромка там же",
                   src="Образ автора, 2013 год (форум). Схема, а не измерение: кромку человеческой кастрюли никто не видел."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    f.text(190, 94, t["left"], size=13, color=INK2, anchor="middle", weight="600")
    f.text(562, 94, t["right"], size=13, color=INK2, anchor="middle", weight="600")
    f.line(372, 82, 372, 350, color=GRID, width=1.5)
    py, pw, ph = 178, 104, 104
    # the twins
    for (x, level), (who, mind) in zip(((70, 0.82), (206, 0.1)), t["twins"]):
        _pot(f, x, py, pw, ph, level, BLUE)
        f.text(x + pw / 2, py + ph + 22, who, size=12, color=INK2, anchor="middle")
        f.text(x + pw / 2, py - 30, mind, size=12.5, color=BLUE, anchor="middle", weight="600")
    f.line(54, py, 326, py, color=RED, width=1.4, dash="5 5")
    f.text(190, py - 8, t["same"], size=12, color=RED, anchor="middle", italic=True)
    # two teachers
    for (x, level, sw), (who, when) in zip(((442, 0.3, 4), (578, 0.82, 16)), t["taps"]):
        _pot(f, x, py, pw, ph, level, ORANGE, stream=(x + pw / 2, sw))
        f.text(x + pw / 2, py + ph + 22, who, size=12, color=INK2, anchor="middle")
        f.text(x + pw / 2, py + ph + 62, when, size=12.5, color=ORANGE, anchor="middle", weight="600")
    f.line(426, py, 698, py, color=RED, width=1.4, dash="5 5")
    f.text(562, py - 58, t["brim"], size=12, color=RED, anchor="middle", italic=True)
    f.text(28, 380, t["src"], size=11.5, color=MUTED)
    return f


@figure("eighteen-times-the-researchers")
def eighteen_times_the_researchers(lang):
    t = {
        "en": dict(title="The same pace, eighteen times the people",
                   sub="Researchers needed to keep the number of transistors on a chip doubling every two years (1971 = 1).",
                   rows=[("1971", 1, "1"), ("2014", 18, "18: the doubling is the same, the people are eighteen times more")],
                   signs="Three more signs of the same thing",
                   items=[("the age at a first patent", "+ ⅔ of a year every ten years (1985–1999)"),
                          ("inventors on one patent", "1.73 → 2.33 (1975–1999)"),
                          ("the age of the great work", "+ about 6 years over the twentieth century")],
                   src="Bloom, Jones, Van Reenen & Webb (2020); Jones (2009, 2010). The United States; the scale of the bars is linear."),
        "ru": dict(title="Тот же темп, в восемнадцать раз больше людей",
                   sub="Сколько исследователей нужно, чтобы число транзисторов на кристалле удваивалось раз в два года (1971 = 1).",
                   rows=[("1971", 1, "1"), ("2014", 18, "18: удвоение то же, людей в восемнадцать раз больше")],
                   signs="Ещё три признака того же самого",
                   items=[("возраст первого патента", "+ ⅔ года за каждые десять лет (1985–1999)"),
                          ("изобретателей на одном патенте", "1,73 → 2,33 (1975–1999)"),
                          ("возраст главной работы", "+ около 6 лет за двадцатый век")],
                   src="Блум, Джонс, Ван Ринен и Уэбб (2020); Джонс (2009, 2010). США; шкала столбиков линейная."),
    }[lang]
    f = Fig(760, 388, t["title"])
    heading(f, t["title"], t["sub"])
    two_bars(f, t["rows"], 18, [MUTED, ORANGE], x0=96, x1=716, y0=88, row=54)
    f.line(28, 208, 732, 208, color=GRID, width=1.5)
    f.text(28, 234, t["signs"], size=13, color=INK2, weight="600")
    for i, (name, value) in enumerate(t["items"]):
        y = 262 + i * 28
        f.circle(36, y - 5, 3.5, fill=ORANGE)
        f.text(50, y, name, size=13, color=INK)
        f.text(300, y, value, size=13, color=INK, weight="600")
    f.text(28, 364, t["src"], size=11.5, color=MUTED)
    return f


@figure("with-the-machine-and-screen-down")
def with_the_machine_and_screen_down(lang):
    t = {
        "en": dict(title="With the machine, and with the screen down",
                   sub="A school in Turkey, nearly 1,000 pupils, mathematics. Grades against the group that had only a textbook.",
                   groups=["practice problems,\nwith the machine", "the examination,\nscreens down"],
                   kinds=["the machine as it comes", "the machine as a teacher: hints, no answers"],
                   vals=[["+48%", "+127%"], ["−17%", "no difference"]],
                   zero="the textbook",
                   src="Bastani and others (2025). The opposite result: Harvard, 194 students, a machine teacher built by the lecturers;\n"
                       "the gain from one lesson was more than twice that of a live class (Kestin and others, 2025)."),
        "ru": dict(title="С машиной и экраном вниз",
                   sub="Школа в Турции, почти 1000 учеников, математика. Оценки против группы, у которой был только учебник.",
                   groups=["тренировочные задачи,\nс машиной", "экзамен,\nэкранами вниз"],
                   kinds=["машина как есть", "машина в роли учителя: подсказки, без ответов"],
                   vals=[["+48%", "+127%"], ["−17%", "разницы нет"]],
                   zero="учебник",
                   src="Бастани и др. (2025). Противоположный результат: Гарвард, 194 студента, машинный учитель, сделанный\n"
                       "преподавателями; прибавка за одно занятие больше чем вдвое против живого занятия (Кестин и др., 2025)."),
    }[lang]
    f = Fig(760, 392, t["title"])
    heading(f, t["title"], t["sub"])
    colors = [MUTED, BLUE]
    for k, (kind, color) in enumerate(zip(t["kinds"], colors)):
        x = 196 + k * 210
        f.rect(x, 84, 14, 14, fill=color, r=3)
        f.text(x + 22, 96, kind, size=12.5, color=INK2)
    x0, scale, bar = 276, 2.6, 24
    data = [[48, 127], [-17, 0]]
    for g, (group, values) in enumerate(zip(t["groups"], data)):
        y = 126 + g * 96
        f.text(40, y + 22, group, size=13.5, color=INK, weight="600")
        for k, v in enumerate(values):
            by = y + k * (bar + 8)
            label = t["vals"][g][k]
            if v > 0:
                f.rect(x0, by, v * scale, bar, fill=colors[k], r=2, opacity=0.9)
                f.text(x0 + v * scale + 10, by + 17, label, size=13.5, color=INK, weight="600")
            elif v < 0:
                f.rect(x0 + v * scale, by, -v * scale, bar, fill=RED, r=2, opacity=0.9)
                f.text(x0 + 10, by + 17, label, size=13.5, color=RED, weight="600")
            else:
                f.rect(x0 - 2, by, 4, bar, fill=colors[k], r=1)
                f.text(x0 + 10, by + 17, label, size=13.5, color=INK, weight="600")
        if g == 0:
            f.line(28, y + 78, 732, y + 78, color=GRID, width=1.5)
    f.line(x0, 116, x0, 296, color=INK2, width=1.5)
    f.text(x0, 314, t["zero"], size=11.5, color=MUTED, anchor="middle")
    f.text(28, 350, t["src"], size=11.5, color=MUTED)
    return f


# --- 54. The Dove Is Crueller than the Wolf ---------------------------------------------------

def _ash_table(f, t, cols, top, row_h, last_colors, fail_second_line=False):
    """A table 'in the ash': a name column and three cells per row; the last column is coloured."""
    head_h = 30
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 20, label, size=12, color=INK2, anchor="middle", weight="600")
    for i, (name, who, *cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[3], y, color=GRID, width=1.2)
        f.text(40, y + row_h / 2 - 3, name, size=14, color=INK, weight="600")
        f.text(40, y + row_h / 2 + 14, who, size=11, color=MUTED)
        for k, cell in enumerate(cells):
            cx = (cols[k] + cols[k + 1]) / 2
            lines = cell.split("\n")
            y0 = y + row_h / 2 + 5 - (len(lines) - 1) * 8.5
            for j, line in enumerate(lines):
                last = k == 2
                if last and fail_second_line:
                    color, weight = (last_colors[i], "600") if j == 0 else (RED, "normal")
                elif last:
                    color, weight = last_colors[i], "600"
                else:
                    color, weight = INK, "normal"
                f.text(cx, y0 + j * 17, line, size=12, color=color, anchor="middle", weight=weight)
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[3], bottom, color=GRID, width=1.2)
    return bottom


@figure("brakes-by-the-fangs")
def brakes_by_the_fangs(lang):
    t = {
        "en": dict(title="The brake is issued according to the fangs",
                   sub="A table in the ash: with what one kills one's own, whether there is a brake, and what saves the loser.",
                   head=["kills its own with", "the brake", "what saves the loser"],
                   rows=[("the dove, the hare", "unarmed", "a day of work", "none",
                          "the sky, the legs\nbut not in a cage"),
                         ("the wolf, the raven", "armed", "one blow", "there is one:\nfor its own",
                          "the neck held out\nbut not on the border of the pack"),
                         ("man", "unarmed in body, armed in hand", "the body: a day of work\nthe hand: one blow",
                          "on hot anger:\nanswers to a face", "a face at arm's length\nbut not at a distance")],
                   src="Rows 1 and 2: Lorenz (1949), with two corrections: the wolves of Yellowstone, 1995–2015 (two thirds of natural\n"
                       "deaths are the work of wolves of other packs), and Maynard Smith and Price (1973). Row 3 is Andrey's reading."),
        "ru": dict(title="Тормоз выдаётся по клыкам",
                   sub="Таблица на золе: чем убивают своих, есть ли тормоз и что спасает проигравшего.",
                   head=["чем убивает своих", "тормоз", "что спасает проигравшего"],
                   rows=[("голубь, заяц", "безоружные", "сутки работы", "нет",
                          "небо, ноги\nно не в клетке"),
                         ("волк, ворон", "вооружённые", "один удар", "есть:\nдля своих",
                          "подставленная шея\nно не на границе стаи"),
                         ("человек", "телом безоружен, рукой вооружён", "телу — сутки работы\nруке — один удар",
                          "на горячей злости:\nсрабатывает на лицо", "лицо на расстоянии руки\nно не издали")],
                   src="Строки 1 и 2: Лоренц (1949) с двумя поправками: волки Йеллоустона, 1995–2015 (две трети естественных\n"
                       "смертей — дело волков чужих стай), и Мейнард Смит и Прайс (1973). Строка 3 — прочтение Андрея."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    bottom = _ash_table(f, t, [236, 404, 548, 736], 84, 68, [GREEN, GREEN, GREEN], fail_second_line=True)
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


@figure("the-face-moves-away")
def the_face_moves_away(lang):
    t = {
        "en": dict(title="The further the face, the weaker the brake",
                   sub="How many of 40 men went on, when ordered, to the last switch: 450 volts.",
                   rows=["the pupil is behind a wall:\nonly his pounding is heard",
                         "behind a wall:\nhis voice is heard",
                         "in the same room,\nwithin arm's reach",
                         "the man himself presses\nthe pupil's hand to the plate"],
                   of="of 40",
                   src="Milgram (1963, 1965): four runs of 40 men each at an American university; the pupil was an actor and no current\n"
                       "flowed. One laboratory, and argued about to this day: read the slope, not the percentages."),
        "ru": dict(title="Чем дальше лицо, тем слабее тормоз",
                   sub="Сколько человек из 40 дошли по приказу до последнего рубильника: 450 вольт.",
                   rows=["ученик за стеной:\nслышен только стук",
                         "за стеной:\nслышен голос",
                         "в той же комнате,\nна расстоянии руки",
                         "руку ученика надо самому\nприжимать к пластине"],
                   of="из 40",
                   src="Милгрэм (1963, 1965): четыре серии по 40 человек в американском университете; ученик был актёром, тока\n"
                       "не было. Одна лаборатория, и спорят о ней до сих пор: читать надо наклон, а не проценты."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    values = [26, 25, 16, 12]
    colors = [RED, RED, ORANGE, YELLOW]
    x0, scale, bar, row = 268, 10.4, 30, 58
    f.line(x0 + 40 * scale, 84, x0 + 40 * scale, 84 + 4 * row, color=GRID, width=1.5, dash="5 5")
    f.text(x0 + 40 * scale, 84 + 4 * row + 16, "40", size=11.5, color=MUTED, anchor="middle")
    for i, (label, v) in enumerate(zip(t["rows"], values)):
        y = 90 + i * row
        f.text(40, y + 13, label, size=12.5, color=INK)
        f.rect(x0, y, v * scale, bar, fill=colors[i], r=2, opacity=0.9)
        f.text(x0 + v * scale + 10, y + 20, f"{v} {t['of']}", size=13.5, color=INK, weight="600")
    f.line(x0, 84, x0, 84 + 4 * row, color=INK2, width=1.5)
    f.text(28, 340, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-held-the-blow")
def what_held_the_blow(lang):
    t = {
        "en": dict(title="What held the blow back",
                   sub="Three supports of the balance between the weapon and the brake, and what is happening to each.",
                   head=["rests on", "holds", "what happens to it"],
                   rows=[("the return blow", "the wolf's brake", "each saves\nhis own skin", "between the armed",
                          "holds; has never\ncovered the unarmed"),
                         ("the need", "people's need for people", "nobody beats\nthe one he needs",
                          "between those who\nneed each other", "goes together\nwith the need"),
                         ("the hands", "those between the wish and the blow", "a thousand heads,\na brake in each",
                          "wherever\na face is seen", "fewer hands for one blow\nwith every new weapon")],
                   src="Supports 1 and 2 are Oleg's objection, which Andrey accepts (the second is the evenings 47 and 49). Support 3 is\n"
                       "the reading of this evening, not a measurement: a thing that carries out takes the place of those who had to look."),
        "ru": dict(title="Что удерживало удар",
                   sub="Три опоры баланса между оружием и тормозом, и что происходит с каждой.",
                   head=["на чём стоит", "где держит", "что с ней происходит"],
                   rows=[("ответный удар", "волчий тормоз", "каждый спасает\nсвою шкуру", "между вооружёнными",
                          "держит; безоружных\nне прикрывал никогда"),
                         ("потребность", "потребность людей в людях", "нужного\nне бьют",
                          "между теми, кто\nдруг другу нужен", "уходит вместе\nс потребностью"),
                         ("руки", "те, кто между желанием и ударом", "тысяча голов,\nв каждой тормоз",
                          "там, где\nвидно лицо", "с каждым новым оружием\nрук на удар всё меньше")],
                   src="Опоры 1 и 2 — возражение Олега, которое Андрей принимает (вторая — вечера 47 и 49). Опора 3 — прочтение\n"
                       "этого вечера, а не измерение: то, что исполняет, встаёт на место тех, кому приходилось смотреть."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    bottom = _ash_table(f, t, [262, 406, 556, 736], 84, 68, [INK2, ORANGE, RED])
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


# --- 55. A Person Without a Face ---------------------------------------------------------------

@figure("two-kinds-of-persons")
def two_kinds_of_persons(lang):
    t = {
        "en": dict(title="Two kinds of persons",
                   sub="Both can own, owe, sign a contract and go to court. The difference is in the rest.",
                   head=["how it is made", "what can be done to it", "how it ends"],
                   rows=[("a man", "a person with a face", "is born: nine months,\nthen twenty years of school",
                          "fined, locked up,\nlooked in the eye", "dies; the heirs\ndivide the heap"),
                         ("a person in law", "a town, a firm, a fund, a ship, a river",
                          "is entered in a register:\nthree working days",
                          "fined, struck off the register;\nno body, no eyes", "no death of age:\nclosed or swallowed")],
                   src="The second row is the invention of the thirteenth-century lawyers: a name in the column “who”, with a pocket.\n"
                       "Three working days is the term for registering a limited company in Russia; a river is such a person\n"
                       "in New Zealand (2017)."),
        "ru": dict(title="Два рода лиц",
                   sub="Оба могут владеть, быть должны, подписать договор и пойти в суд. Разница в остальном.",
                   head=["как появляется", "что с ним можно сделать", "чем кончает"],
                   rows=[("человек", "лицо с лицом", "рождается: девять месяцев\nи двадцать лет учёбы",
                          "оштрафовать, посадить,\nпосмотреть в глаза", "умирает; наследники\nделят кучку"),
                         ("юридическое лицо", "город, фирма, фонд, корабль, река",
                          "вносится в реестр:\nтри рабочих дня",
                          "оштрафовать, вычеркнуть;\nни тела, ни глаз", "от старости не умирает:\nзакрывают или глотают")],
                   src="Вторая строка — изобретение юристов тринадцатого века: имя в графе «кто», и при нём карман.\n"
                       "Три рабочих дня — срок регистрации общества с ограниченной ответственностью в России; река — такое\n"
                       "лицо в Новой Зеландии (2017)."),
    }[lang]
    f = Fig(760, 318, t["title"])
    heading(f, t["title"], t["sub"])
    bottom = _ash_table(f, t, [258, 424, 590, 736], 84, 68, [INK2, RED])
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


@figure("the-feed-comes-down")
def the_feed_comes_down(lang):
    t = {
        "en": dict(title="Who owns the tractor",
                   sub="Two chains of ownership. The feed comes down both. The say goes up only the short one.",
                   y1935="1935", now="today",
                   farmer="the farmer", tractor="the tractor",
                   saver="the saver", fund="a fund", firm="a firm", machine="the machine",
                   fund_sub="buys everything,\nby a table", firm_sub="a name, an account,\na director",
                   wheel="holds the wheel himself",
                   feed="the feed: a little is added every year",
                   say="the say: the saver cannot even find out what he owns",
                   src="Three index funds taken together were the largest holder in 88% of the 500 largest American companies\n"
                       "(Fichtner, Heemskerk and Garcia-Bernardo, 2017). A scheme of the argument, not data."),
        "ru": dict(title="Чей трактор",
                   sub="Две цепочки владения. Корм приходит по обеим. Слово доходит только по короткой.",
                   y1935="1935", now="сегодня",
                   farmer="фермер", tractor="трактор",
                   saver="вкладчик", fund="фонд", firm="фирма", machine="машина",
                   fund_sub="покупает всё подряд,\nпо таблице", firm_sub="имя, счёт,\nдиректор",
                   wheel="сам держит руль",
                   feed="корм: каждый год немного прибавляется",
                   say="слово: вкладчик не может даже узнать, чем владеет",
                   src="Три индексных фонда, если считать их вместе, были крупнейшим держателем в 88% из 500 крупнейших\n"
                       "американских компаний (Фихтнер, Хемскерк и Гарсия-Бернардо, 2017). Схема рассуждения, а не данные."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    bw, bh = 132, 60
    xs = [112 + i * 164 for i in range(4)]
    # the short chain
    f.text(40, 126, t["y1935"], size=14, color=INK2, weight="600")
    f.box(xs[0], 90, bw, bh, t["farmer"], weight="600")
    f.box(xs[3], 90, bw, bh, t["tractor"], stroke=BLUE, weight="600")
    f.line(xs[0] + bw + 8, 122, xs[3] - 10, 122, color=GREEN, width=2, arrow=True)
    f.text((xs[0] + bw + xs[3]) / 2, 112, t["wheel"], size=12.5, color=GREEN, anchor="middle", weight="600")
    # the long chain
    y = 190
    f.text(40, y + 36, t["now"], size=14, color=INK2, weight="600")
    f.box(xs[0], y, bw, bh, t["saver"], weight="600")
    f.box(xs[1], y, bw, bh, t["fund"], weight="600", sub=t["fund_sub"], stroke=MUTED, size=13)
    f.box(xs[2], y, bw, bh, t["firm"], weight="600", sub=t["firm_sub"], stroke=MUTED, size=13)
    f.box(xs[3], y, bw, bh, t["machine"], stroke=BLUE, weight="600")
    for i in range(3):
        # the feed comes back towards the saver; the say does not get through
        f.line(xs[i + 1] - 6, y + 20, xs[i] + bw + 8, y + 20, color=GREEN, width=2, arrow=True)
        f.line(xs[i] + bw + 6, y + 42, xs[i + 1] - 6, y + 42, color=RED, width=1.6, dash="4 4")
        cx = (xs[i] + bw + xs[i + 1]) / 2
        f.line(cx - 5, y + 37, cx + 5, y + 47, color=RED, width=1.8)
        f.line(cx - 5, y + 47, cx + 5, y + 37, color=RED, width=1.8)
    f.line(64, 282, 40, 282, color=GREEN, width=2, arrow=True)
    f.text(74, 286, t["feed"], size=12.5, color=INK)
    f.line(40, 304, 64, 304, color=RED, width=1.6, dash="4 4")
    f.line(47, 299, 57, 309, color=RED, width=1.8)
    f.line(47, 309, 57, 299, color=RED, width=1.8)
    f.text(74, 308, t["say"], size=12.5, color=INK)
    f.text(28, 340, t["src"], size=11.5, color=MUTED)
    return f


@figure("same-shell-other-filling")
def same_shell_other_filling(lang):
    t = {
        "en": dict(title="The shell is the same, the filling is different",
                   sub="One person in law at three moments. Not one of the replacements needed a new law.",
                   shell="name · account · seal · right to sue",
                   caps=["every part is a man:\na head, a brake, a pair of eyes",
                         "the parts are replaced one at a time,\nas a typewriter is bought",
                         "one signature is left:\na face for hire"],
                   man="a man", prog="a program",
                   src="A scheme, not data. The shell is four hundred years old; what is new is only that the filling\n"
                       "need not be made of people."),
        "ru": dict(title="Оболочка та же, начинка другая",
                   sub="Одно юридическое лицо в три разных момента. Ни одна замена не потребовала нового закона.",
                   shell="имя · счёт · печать · право на иск",
                   caps=["каждая деталь — человек:\nголова, тормоз, пара глаз",
                         "детали меняют по одной,\nкак покупают пишущую машинку",
                         "осталась одна подпись:\nлицо по найму"],
                   man="человек", prog="программа",
                   src="Схема, а не данные. Оболочке четыреста лет; ново только то, что начинка может быть\n"
                       "не из людей."),
    }[lang]
    f = Fig(760, 356, t["title"])
    heading(f, t["title"], t["sub"])
    people = [20, 10, 1]
    w, h, gap = 212, 132, 34
    for k, n in enumerate(people):
        x = 28 + k * (w + gap)
        f.rect(x, 86, w, h, fill="none", stroke=INK2, width=1.8, r=10)
        f.line(x, 112, x + w, 112, color=INK2, width=1.2)
        f.text(x + w / 2, 104, t["shell"], size=11, color=INK2, anchor="middle", weight="600")
        for i in range(20):
            cx = x + 30 + (i % 5) * 38
            cy = 134 + (i // 5) * 22
            if i < n:
                f.circle(cx, cy, 7, fill=ORANGE)
            else:
                f.rect(cx - 6.5, cy - 6.5, 13, 13, fill=BLUE, r=2)
        f.text(x + w / 2, 240, t["caps"][k], size=11, color=INK, anchor="middle")
        if k < 2:
            f.line(x + w + 6, 152, x + w + gap - 7, 152, color=INK2, width=1.8, arrow=True)
    f.circle(40, 292, 7, fill=ORANGE)
    f.text(54, 296, t["man"], size=12.5, color=INK)
    px = 140 if lang == "en" else 150
    f.rect(px, 285.5, 13, 13, fill=BLUE, r=2)
    f.text(px + 22, 296, t["prog"], size=12.5, color=INK)
    f.text(28, 324, t["src"], size=11.5, color=MUTED)
    return f


# --- 56. The Observer Who Is Not There ---------------------------------------------------------

def _photon(f, x, y, length, angle, waves, amp, color, width=1.5):
    """A wavy arrow for a grain of light: `waves` full waves along `length`, turned by `angle` degrees."""
    a = math.radians(angle)
    body = length - 8
    steps = max(24, int(waves * 14))
    pts = []
    for i in range(steps + 1):
        s = body * i / steps
        off = amp * math.sin(2 * math.pi * waves * i / steps)
        pts.append((x + s * math.cos(a) - off * math.sin(a), y + s * math.sin(a) + off * math.cos(a)))
    f.path("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts), color=color, width=width)
    f.line(pts[-1][0], pts[-1][1], x + length * math.cos(a), y + length * math.sin(a), color=color,
           width=width, arrow=True)


@figure("stripes-fade-with-heat")
def stripes_fade_with_heat(lang):
    t = {
        "en": dict(title="A molecule can be “seen” simply by heating it",
                   sub="The same molecule of seventy carbon atoms, the same gratings. Only the knob of the laser is turned.",
                   temps=["not heated", "heated more", "about 3,000 K"],
                   light=["long waves of heat light:\nthey cannot tell which path",
                          "more grains of light,\nshorter waves",
                          "each grain could tell\nwhere the molecule was"],
                   screen=["stripes", "paler stripes", "no stripes"],
                   wall="the light goes into the walls of the chamber: no eye, no counter, no film",
                   src="After Hackermüller, Hornberger, Brezger, Zeilinger and Arndt (2004). A scheme of the experiment, not its data:\n"
                       "the number of grains of light and the paleness of the stripes are illustrative."),
        "ru": dict(title="Молекулу можно «увидеть», просто нагрев её",
                   sub="Та же молекула из семидесяти атомов углерода, те же решётки. Крутят только ручку лазера.",
                   temps=["без нагрева", "нагрели сильнее", "около 3000 К"],
                   light=["длинные волны теплового света:\nпо ним не понять, каким путём",
                          "крупинок света больше,\nволны короче",
                          "каждая крупинка могла бы\nсказать, где была молекула"],
                   screen=["полосы", "полосы бледнее", "полос нет"],
                   wall="свет уходит в стенки камеры: ни глаза, ни счётчика, ни плёнки",
                   src="По работе Хакермюллера, Хорнбергера, Брецгера, Цайлингера и Арндта (2004). Схема опыта, а не его данные:\n"
                       "число крупинок света и бледность полос условны."),
    }[lang]
    f = Fig(760, 420, t["title"])
    heading(f, t["title"], t["sub"])
    w, gap = 220, 22
    shots = [[(-150, 1.5, 40)],
             [(-155, 3, 38), (-30, 3, 38), (95, 3.5, 34)],
             [(-172, 7, 36), (-128, 7, 32), (-52, 7, 32), (-8, 7, 36), (55, 7, 32), (125, 7, 32)]]
    colors = [RED, ORANGE, YELLOW]
    contrast = [0.95, 0.45, 0.0]
    for k in range(3):
        x = 28 + k * (w + gap)
        cx, cy = x + w / 2, 160
        f.rect(x, 84, w, 262, fill="none", stroke=GRID, width=1.2, r=10)
        f.text(cx, 106, t["temps"][k], size=13.5, color=INK, anchor="middle", weight="600")
        for angle, waves, length in shots[k]:
            a = math.radians(angle)
            _photon(f, cx + 17 * math.cos(a), cy + 17 * math.sin(a), length, angle, waves, 3.2, colors[k])
        f.circle(cx, cy, 13, fill=BLUE, opacity=0.85)
        f.text(cx, 226, t["light"][k], size=11.5, color=INK2, anchor="middle")
        # the screen: 45 thin bars, their darkness follows 1 + V·cos
        sx, sy, sw, sh, n = x + 20, 262, 180, 40, 45
        for i in range(n if contrast[k] else 0):
            level = (1 + contrast[k] * math.cos(2 * math.pi * 5 * (i + 0.5) / n)) / 2
            f.add(f'<rect x="{sx + i * sw / n:.1f}" y="{sy}" width="{sw / n + 0.3:.1f}" height="{sh}" '
                  f'fill="{BLUE}" fill-opacity="{0.08 + 0.8 * level:.2f}"/>')
        f.rect(sx, sy, sw, sh, fill="none" if contrast[k] else BLUE, stroke=INK2, width=1.2, r=2,
               opacity=None if contrast[k] else 0.48)
        f.text(cx, 326, t["screen"][k], size=13, color=INK, anchor="middle", weight="600")
        if k < 2:
            f.line(x + w + 3, 215, x + w + gap - 5, 215, color=INK2, width=1.8, arrow=True)
    f.text(380, 368, t["wall"], size=12.5, color=INK, anchor="middle")
    f.text(28, 392, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-stands-behind-the-observer")
def what_stands_behind_the_observer(lang):
    t = {
        "en": dict(title="What stands where the word “observer” stands",
                   sub="A table in the ash: four places in science, what the sentence says and what is actually there.",
                   head=["the sentence says", "what is there", "an example"],
                   rows=[("relativity", "since 1905", "an observer\non the platform", "a clock and a ruler",
                          "four atomic clocks\nin aeroplane seats, 1971"),
                         ("engineering", "since 1964", "an observer\nof the state", "a formula that works out\nwhat cannot be measured",
                          "in the computer of the ship\nthat flew to the Moon"),
                         ("quantum mechanics", "since the 1920s", "the electron\nis observed", "something keeps a trace\nof the path",
                          "light that went\ninto the wall, 2004"),
                         ("cosmology", "since 1973", "a universe\nfit for observers", "whoever is there\nto ask the question",
                          "everybody at a class\nreunion is alive")],
                   src="In every row the word can be taken out and the thing put in, and not one formula changes.\n"
                       "The rows are the evening's reading of Einstein (1905), Luenberger (1964), Zeh (1970) and Carter (1973)."),
        "ru": dict(title="Что стоит там, где стоит слово «наблюдатель»",
                   sub="Таблица на золе: четыре места в науке, что сказано в предложении и что там на самом деле.",
                   head=["в предложении сказано", "что там на самом деле", "пример"],
                   rows=[("теория относительности", "с 1905 года", "наблюдатель\nна перроне", "часы и линейка",
                          "четверо атомных часов\nв креслах самолёта, 1971"),
                         ("техника", "с 1964 года", "наблюдатель\nсостояния", "формула, которая вычисляет\nто, чего не измерить",
                          "в компьютере корабля,\nлетавшего на Луну"),
                         ("квантовая механика", "с 1920-х годов", "за электроном\nнаблюдают", "что-то хранит след\nпути",
                          "свет, ушедший\nв стенку, 2004"),
                         ("космология", "с 1973 года", "Вселенная, пригодная\nдля наблюдателей", "тот, кто оказался на месте\nи задал вопрос",
                          "на встрече выпускников\nвсе живы")],
                   src="В каждой строке слово можно вынуть и поставить вещь, и ни одна формула не изменится.\n"
                       "Строки — прочтение этого вечера: Эйнштейн (1905), Люенбергер (1964), Цее (1970), Картер (1973)."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    bottom = _ash_table(f, t, [222, 376, 560, 736], 84, 68, [INK2, INK2, INK2, INK2])
    f.text(28, bottom + 24, t["src"], size=11.5, color=MUTED)
    return f


@figure("the-movable-line")
def the_movable_line(lang):
    t = {
        "en": dict(title="Where does “what is observed” end and “who observes” begin?",
                   sub="The line can be drawn after any link of the chain, and the numbers come out the same (von Neumann, 1932).",
                   links=["the\nmolecule", "a grain\nof light", "the wall,\na counter", "the record", "the eye", "the brain", "“I”"],
                   first="the stripes go here:\nthe heated molecule, 2004",
                   last="the popular article\ndraws the line here",
                   between="between the first link and the last no laboratory has found anything to happen",
                   open="Not solved: why the molecule lands in one place. That is the measurement problem, and it is open.",
                   src="A scheme of the argument, not data. The chain is von Neumann's, with the links of the two-slit experiment."),
        "ru": dict(title="Где кончается «то, за чем наблюдают» и начинается «тот, кто наблюдает»?",
                   sub="Черту можно провести после любого звена цепочки, и числа выйдут те же (фон Нейман, 1932).",
                   links=["молекула", "крупинка\nсвета", "стенка,\nсчётчик", "запись", "глаз", "мозг", "«я»"],
                   first="полосы пропадают здесь:\nнагретая молекула, 2004",
                   last="популярная статья\nпроводит черту здесь",
                   between="между первым звеном и последним ни одна лаборатория не нашла, чтобы что-то происходило",
                   open="Не решено: почему молекула попадает в одно место. Это проблема измерения, и она открыта.",
                   src="Схема рассуждения, а не данные. Цепочка фон Неймана, со звеньями опыта с двумя щелями."),
    }[lang]
    f = Fig(760, 372, t["title"])
    f.text(28, 40, t["title"], size=17.5 if lang == "ru" else 19, weight="600")
    f.text(28, 64, t["sub"], size=13 if lang == "ru" else 13.5, color=INK2)
    n, bw, bh, y = 7, 82, 54, 150
    step = (704 - bw) / (n - 1)
    xs = [28 + i * step for i in range(n)]
    for i, label in enumerate(t["links"]):
        f.box(xs[i], y, bw, bh, label, size=12.5, weight="600", stroke=BLUE if i == 0 else INK2)
        if i < n - 1:
            gx = (xs[i] + bw + xs[i + 1]) / 2
            color = GREEN if i == 0 else RED if i == n - 2 else MUTED
            f.line(gx, y - 22, gx, y + bh + 22, color=color, width=2 if color != MUTED else 1.4, dash="5 4")
    g0 = (xs[0] + bw + xs[1]) / 2
    g5 = (xs[5] + bw + xs[6]) / 2
    f.text(g0 + 8, 104, t["first"], size=12, color=GREEN, weight="600")
    f.text(g5 - 8, 104, t["last"], size=12, color=RED, weight="600", anchor="end")
    f.line(g0 + 10, 248, g5 - 10, 248, color=MUTED, width=1.4)
    f.line(g0 + 10, 242, g0 + 10, 254, color=MUTED, width=1.4)
    f.line(g5 - 10, 242, g5 - 10, 254, color=MUTED, width=1.4)
    f.text((g0 + g5) / 2, 270, t["between"], size=12, color=INK2, anchor="middle")
    f.text(28, 312, t["open"], size=13, color=INK, weight="600")
    f.text(28, 344, t["src"], size=11.5, color=MUTED)
    return f


# --- 57. Dividends for the Wheel ---------------------------------------------------------------

@figure("dividends-have-a-term")
def dividends_have_a_term(lang):
    t = {
        "en": dict(title="For how long the law pays the one who made it",
                   sub="Years of exclusive right. When the term runs out, the thing belongs to everybody.",
                   rows=[("the wheel", "about 5,500 years ago", 0, 0, "nobody, never"),
                         ("a new book, England, 1710", "the first copyright law", 14, 14,
                          "14 years, and 14 more if the author is alive"),
                         ("an invention, today", "a patent", 20, 0, "20 years from the application"),
                         ("Pushkin", "died in 1837", 50, 0, "50 years after his death: until 1887"),
                         ("a book, today", "", 70, 0, "the author's life and 70 years more")],
                   axis="years",
                   src="The Statute of Anne (1710); article 33 of the TRIPS agreement; the Russian law of 1857; the term of today in the\n"
                       "United States, the European Union and Russia. Counted from publication (1710), from the application (a patent)\n"
                       "or from the author's death (Pushkin, a book today)."),
        "ru": dict(title="Сколько лет закон платит тому, кто придумал",
                   sub="Годы исключительного права. Когда срок выходит, вещь принадлежит всем.",
                   rows=[("колесо", "около 5500 лет назад", 0, 0, "никому и никогда"),
                         ("новая книга, Англия, 1710", "первый закон об авторском праве", 14, 14,
                          "14 лет и ещё 14, если автор жив"),
                         ("изобретение, сегодня", "патент", 20, 0, "20 лет со дня заявки"),
                         ("Пушкин", "умер в 1837 году", 50, 0, "50 лет после смерти: до 1887 года"),
                         ("книга, сегодня", "", 70, 0, "жизнь автора и ещё 70 лет")],
                   axis="лет",
                   src="Статут королевы Анны (1710); статья 33 соглашения ТРИПС; российский закон 1857 года; сегодняшний срок в США,\n"
                       "Евросоюзе и России. Счёт идёт от издания (1710), от заявки (патент) или от смерти автора\n"
                       "(Пушкин, сегодняшняя книга)."),
    }[lang]
    f = Fig(760, 424, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, vmax, row, y0 = 262, 520, 80, 50, 92
    for v in (0, 20, 40, 60, 80):
        x = x0 + v / vmax * (x1 - x0)
        f.line(x, y0 - 4, x, y0 + 5 * row - 6, color=GRID, width=1)
        f.text(x, y0 + 5 * row + 12, str(v) if v < 80 else f"80 {t['axis']}", size=11.5, color=MUTED, anchor="middle")
    for i, (name, who, v, extra, shown) in enumerate(t["rows"]):
        y = y0 + i * row
        f.text(x0 - 14, y + (20 if who else 26), name, size=13.5, color=INK, anchor="end", weight="600")
        if who:
            f.text(x0 - 14, y + 36, who, size=11, color=MUTED, anchor="end")
        w = v / vmax * (x1 - x0)
        if v:
            f.rect(x0, y + 10, w, 24, fill=ORANGE, r=2, opacity=0.9)
        else:
            f.rect(x0 - 2, y + 10, 4, 24, fill=MUTED, r=1)
        if extra:
            f.rect(x0 + w, y + 10, extra / vmax * (x1 - x0), 24, fill=ORANGE, r=2, opacity=0.4)
            w += extra / vmax * (x1 - x0)
        f.text(x0 + w + 10, y + 27, shown, size=12.5, color=INK, weight="600")
    f.line(x0, y0 - 4, x0, y0 + 5 * row - 6, color=INK2, width=1.5)
    f.text(28, 372, t["src"], size=11.5, color=MUTED)
    return f


def _split_bar(f, x0, x1, y, h, share, colors, labels):
    """One bar of 100% split into a small first part and the rest, each with its label."""
    w = (x1 - x0) * share
    f.rect(x0, y, w, h, fill=colors[0], r=2, opacity=0.9)
    f.rect(x0 + w + 2, y, x1 - x0 - w - 2, h, fill=colors[1], r=2, opacity=0.9)
    f.text(x0 + w + 16, y + h / 2 + 5, labels[1], size=13.5, color="#ffffff", weight="600")
    f.line(x0 + w / 2, y + h, x0 + w / 2, y + h + 12, color=INK2, width=1.2)
    f.text(x0, y + h + 28, labels[0], size=12.5, color=INK, weight="600")


@figure("where-the-gain-came-from")
def where_the_gain_came_from(lang):
    t = {
        "en": dict(title="Where the growth came from, and who kept it",
                   sub="Two counts made by economists; each bar is a whole, split in two.",
                   a="Output per hour of work doubled (the United States, 1909–1949). What it came from:",
                   a_labels=["⅛: more machines per worker", "⅞: everything else. Solow called it “technical change”"],
                   b="The gain from new inventions (the United States, 1948–2001). Who kept it:",
                   b_labels=["2.2%: those who invented", "about 98%: everybody else, as lower prices"],
                   src="Solow (1957); Nordhaus (2004), whose estimates run from 1.3% to 3.3%. The seven eighths are a remainder:\n"
                       "what the growth of machines and of hours worked does not explain. A colleague of Solow's called it\n"
                       "“some sort of measure of our ignorance”."),
        "ru": dict(title="Откуда взялся рост и кому он достался",
                   sub="Два подсчёта экономистов; каждая полоса — целое, разделённое надвое.",
                   a="Выработка за час труда удвоилась (США, 1909–1949). Откуда это взялось:",
                   a_labels=["⅛: больше машин на работника", "⅞: всё остальное. Солоу назвал это «техническим прогрессом»"],
                   b="Выигрыш от новых изобретений (США, 1948–2001). Кому он достался:",
                   b_labels=["2,2%: тем, кто изобрёл", "около 98%: всем остальным, дешевизной"],
                   src="Солоу (1957); Нордхаус (2004), оценки которого лежат между 1,3% и 3,3%. Семь восьмых — это остаток:\n"
                       "то, чего не объясняет рост числа машин и отработанных часов. Коллега Солоу назвал его\n"
                       "«своего рода мерой нашего незнания»."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    f.text(28, 100, t["a"], size=13, color=INK2)
    _split_bar(f, 28, 732, 112, 34, 1 / 8, [MUTED, BLUE], t["a_labels"])
    f.text(28, 212, t["b"], size=13, color=INK2)
    _split_bar(f, 28, 732, 224, 34, 0.022, [MUTED, GREEN], t["b_labels"])
    f.text(28, 318, t["src"], size=11.5, color=MUTED)
    return f


@figure("price-of-everything-written")
def price_of_everything_written(lang):
    t = {
        "en": dict(title="Arithmetic on the knee: the price of everything written",
                   sub="Billions of dollars. The scale is linear.",
                   rows=[("every book ever counted,\nat the rate of the settlement", 390,
                          "390: 129.9 million books × 3,000 dollars"),
                         ("data centres and chips,\nfour companies, 2025", 413, "about 413"),
                         ("the same four,\nthe plan for 2026", 730, "about 730")],
                   note="Paid once. And the 3,000 dollars is not a price for learning: it is what the settlement paid\n"
                        "for a copy taken without paying. The court called the learning itself fair use.",
                   src="Google Books (2010: 129,864,880 books, counted by editions); the settlement in Bartz v. Anthropic (approved in July\n"
                       "2026); the reports of Amazon, Alphabet, Microsoft and Meta of October 2026 (capital spending; the bases differ)."),
        "ru": dict(title="Арифметика на коленке: цена всего написанного",
                   sub="Миллиарды долларов. Шкала линейная.",
                   rows=[("все когда-либо сосчитанные\nкниги по ставке соглашения", 390,
                          "390: 129,9 млн книг × 3000 долларов"),
                         ("дата-центры и чипы,\nчетыре компании, 2025", 413, "около 413"),
                         ("те же четыре,\nплан на 2026", 730, "около 730")],
                   note="Платится один раз. И 3000 долларов — не цена за учёбу: столько по соглашению заплачено\n"
                        "за копию, взятую без оплаты. Саму учёбу суд назвал добросовестным использованием.",
                   src="Google Books (2010: 129 864 880 книг, счёт по изданиям); мировое соглашение по делу Bartz v. Anthropic (утверждено\n"
                       "в июле 2026); отчёты Amazon, Alphabet, Microsoft и Meta за октябрь 2026 (капитальные затраты; базы разные)."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, vmax, row, y0 = 250, 716, 730, 58, 88
    colors = [ORANGE, MUTED, MUTED]
    for i, (name, v, shown) in enumerate(t["rows"]):
        y = y0 + i * row
        f.text(x0 - 14, y + 18, name, size=12.5, color=INK, anchor="end")
        w = v / vmax * (x1 - x0)
        f.rect(x0, y + 6, w, 30, fill=colors[i], r=2, opacity=0.9)
        f.text(x0 + 12, y + 26, shown, size=13, color="#ffffff", weight="600")
    f.line(x0, y0 - 2, x0, y0 + 3 * row - 10, color=INK2, width=1.5)
    f.text(28, 278, t["note"], size=12.5, color=INK, weight="600")
    f.text(28, 332, t["src"], size=11.5, color=MUTED)
    return f


# --- 58. The Blind Man's Stick -----------------------------------------------------------------

@figure("two-kittens-one-view")
def two_kittens_one_view(lang):
    yes, no = ("yes", "no") if lang == "en" else ("да", "нет")
    t = {
        "en": dict(title="Two kittens, one view",
                   sub="The carousel of 1963, seen from above: one kitten walks, the other is carried, and both see the same stripes.",
                   walks="walks", carried="is carried\nin a basket", wall="a drum with striped walls",
                   head=["walked", "was carried"],
                   rows=["puts out its paws\nto meet a surface", "blinks at a hand\ncoming at its face",
                         "steps off the glass over a drop\non the shallow side"],
                   cells=[("all 8", "none of 8"), ("yes", "no"), ("12 times of 12", "4 to 8 of 12")],
                   after="The carried kittens were not blind: the pupil narrowed, the eye followed a moving hand.\n"
                         "After two days of running free in a lit room they passed the same tests.",
                   src="Held and Hein (1963): eight pairs reared in the dark to the age of 8–12 weeks, then three hours a day in the\n"
                       "apparatus, 9 to 63 hours in all (about 30 on average); a pair was tested when its walking kitten first put out its paws."),
        "ru": dict(title="Два котёнка, одна картина",
                   sub="Карусель 1963 года, вид сверху: один котёнок ходит, другого возят, и оба видят одни и те же полосы.",
                   walks="ходит", carried="едет\nв корзинке", wall="барабан с полосатыми стенками",
                   head=["ходил", "возили"],
                   rows=["вытягивает лапы\nнавстречу поверхности", "моргает на руку,\nлетящую к морде",
                         "сходит со стекла над обрывом\nна мелкую сторону"],
                   cells=[("все 8", "ни один из 8"), ("да", "нет"), ("12 раз из 12", "от 4 до 8 из 12")],
                   after="Котята, которых возили, слепыми не были: зрачок сужался, глаз следил за рукой.\n"
                         "После двух суток свободной беготни в освещённой комнате они прошли те же проверки.",
                   src="Хелд и Хайн (1963): восемь пар выращены в темноте до 8–12 недель, затем по три часа в день в установке,\n"
                       "всего от 9 до 63 часов (в среднем около 30); пару проверяли, когда ходивший котёнок впервые вытягивал лапы."),
    }[lang]
    f = Fig(760, 462, t["title"])
    heading(f, t["title"], t["sub"])
    # the drum from above
    cx, cy, R = 168, 214, 112
    f.circle(cx, cy, R, fill="none", stroke=INK2, width=1.5)
    for k in range(36):
        a = 2 * math.pi * k / 36
        f.line(cx + (R + 2) * math.cos(a), cy + (R + 2) * math.sin(a),
               cx + (R + 12) * math.cos(a), cy + (R + 12) * math.sin(a),
               color=INK if k % 2 == 0 else GRID, width=5, cap="butt")
    ang = math.radians(-24)
    ax, ay = cx - 74 * math.cos(ang), cy - 74 * math.sin(ang)
    px, py = cx + 74 * math.cos(ang), cy + 74 * math.sin(ang)
    f.line(ax, ay, px, py, color=INK2, width=3)
    f.circle(cx, cy, 5, fill=INK2)
    # the walking kitten: a body, a head and four paws
    f.ellipse(ax, ay, 15, 9, fill=GREEN)
    f.circle(ax + 6, ay + 15, 6, fill=GREEN)
    for dx, dy in ((-9, -9), (-9, 9), (8, -10), (10, 5)):
        f.circle(ax + dx - 5, ay + dy, 2.6, fill=GREEN)
    # the carried one: a basket with a head
    f.rect(px - 14, py - 11, 28, 22, fill=SURFACE, stroke=ORANGE, width=2.2, r=4)
    f.circle(px - 5, py - 16, 6, fill=ORANGE)
    f.text(ax - 6, ay - 22, t["walks"], size=12.5, color=GREEN, anchor="middle", weight="600")
    f.text(px + 4, py + 30, t["carried"], size=12.5, color=ORANGE, anchor="middle", weight="600")
    f.text(cx, cy + R + 32, t["wall"], size=11.5, color=MUTED, anchor="middle")
    # the three tests
    x0, c1, c2, top, row = 336, 566, 668, 96, 58
    f.text(c1, top + 8, t["head"][0], size=13, color=GREEN, anchor="middle", weight="600")
    f.text(c2, top + 8, t["head"][1], size=13, color=ORANGE, anchor="middle", weight="600")
    for i, name in enumerate(t["rows"]):
        y = top + 24 + i * row
        f.line(x0, y, 732, y, color=GRID, width=1.2)
        f.text(x0 + 4, y + 25, name, size=12.5, color=INK)
        f.text(c1, y + 33, t["cells"][i][0], size=13, color=INK, anchor="middle", weight="600")
        f.text(c2, y + 33, t["cells"][i][1], size=13, color=RED, anchor="middle", weight="600")
    f.line(x0, top + 24 + 3 * row, 732, top + 24 + 3 * row, color=GRID, width=1.2)
    f.text(28, 388, t["after"], size=12.5, color=INK, weight="600")
    f.text(28, 432, t["src"], size=11.5, color=MUTED)
    return f


@figure("loop-of-the-stick")
def loop_of_the_stick(lang):
    t = {
        "en": dict(title="The loop: poke, take the response, find the link",
                   sub="Drawn in the ash. The four steps are the author's list of 2015; in blue, his program of 1989.",
                   world=("reality", "a path in the dark,\na board,\na casting"),
                   steps=[("1. Poke", "motor action: stir reality", "a test signal into any point of the board"),
                          ("2. Take the response", "the sensors", "the signals at all the other points"),
                          ("3. Recognise", "the images already in memory", "is this a fault it has met before?"),
                          ("4. Find the link", "the correlator: new images", "which pair “poke here, listen there” tells most")],
                   memory=("Memory", "images are born, compete and are written off;\nwants decide what to keep and where to poke next",
                           "images of faults, corrected at every diagnosis"),
                   out="Take one link out and the loop stops. No poke of one's own: the kitten in the basket.\n"
                       "No response from outside: a dream. Nothing kept: a talk that leaves no trace in the head.",
                   src="A scheme of the argument, not data. After the author's comments of 24–25 July 2015 under his SETI talk."),
        "ru": dict(title="Петля: ткнул, получил отклик, нашёл связь",
                   sub="Нарисовано на золе. Четыре шага — список автора 2015 года; синим — его программа 1989 года.",
                   world=("реальность", "тропинка в темноте,\nплата,\nотливка"),
                   steps=[("1. Ткнуть", "моторика: пошевелить реальность", "пробный сигнал в любую точку платы"),
                          ("2. Принять отклик", "сенсорика", "сигналы во всех остальных точках"),
                          ("3. Распознать", "образы, которые уже есть в памяти", "эту неисправность уже встречали?"),
                          ("4. Найти связь", "коррелятор: новые образы", "какая пара «ткнуть — слушать» скажет больше")],
                   memory=("Память", "образы рождаются, соперничают и списываются;\nхотелки решают, что хранить и куда ткнуть дальше",
                           "образы неисправностей, с поправкой при каждой проверке"),
                   out="Выньте одно звено, и петля встанет. Нет своего тычка — котёнок в корзинке.\n"
                       "Нет отклика снаружи — сон. Ничего не сохранилось — разговор, не оставивший следа в голове.",
                   src="Схема рассуждения, а не данные. По комментариям автора от 24–25 июля 2015 года под его докладом в SETI."),
    }[lang]
    f = Fig(760, 458, t["title"])
    heading(f, t["title"], t["sub"])
    bw, bh = 248, 76
    xl, xr, yt, yb = 206, 484, 88, 268
    # the world on the left
    f.rect(28, 118, 136, 196, fill="none", stroke=INK2, width=1.5, r=10, dash="6 4")
    f.text(96, 196, t["world"][0], size=14, color=INK, anchor="middle", weight="600")
    f.text(96, 218, t["world"][1], size=11.5, color=INK2, anchor="middle")
    spots = [(xl, yt), (xl, yb), (xr, yb), (xr, yt)]
    for (x, y), (name, term, prog) in zip(spots, t["steps"]):
        f.rect(x, y, bw, bh, fill=SURFACE, stroke=INK2, r=8)
        f.text(x + 14, y + 24, name, size=14, color=INK, weight="600")
        f.text(x + 14, y + 44, term, size=11.5, color=INK2)
        f.text(x + 14, y + 62, prog, size=11.5, color=BLUE)
    # memory in the middle
    mx, my, mw, mh = 300, 176, 340, 80
    f.rect(mx, my, mw, mh, fill="#f3f2ee", stroke=MUTED, width=1.2, r=8)
    f.text(mx + 14, my + 22, t["memory"][0], size=13.5, color=INK, weight="600")
    f.text(mx + 14, my + 40, t["memory"][1], size=11, color=INK2)
    f.text(mx + 14, my + 72, t["memory"][2], size=11, color=BLUE)
    # the ring of arrows
    f.line(xl - 2, yt + bh / 2, 168, 150, color=ORANGE, width=2.2, arrow=True)
    f.line(168, 284, xl - 4, yb + bh / 2, color=ORANGE, width=2.2, arrow=True)
    f.line(xl + bw + 2, yb + bh / 2, xr - 5, yb + bh / 2, color=ORANGE, width=2.2, arrow=True)
    f.line(xr + bw - 44, yb - 2, xr + bw - 44, yt + bh + 5, color=ORANGE, width=2.2, arrow=True)
    f.line(xr - 2, yt + bh / 2, xl + bw + 5, yt + bh / 2, color=ORANGE, width=2.2, arrow=True)
    f.text(28, 386, t["out"], size=12.5, color=INK, weight="600")
    f.text(28, 440, t["src"], size=11.5, color=MUTED)
    return f


@figure("who-has-the-whole-loop")
def who_has_the_whole_loop(lang):
    yes, no = ("yes", "no") if lang == "en" else ("да", "нет")
    t = {
        "en": dict(title="Who has the whole loop",
                   sub="A table in the ash: the same four steps, and who is missing which.",
                   head=["pokes", "gets an answer\nto its own poke", "finds the link", "the head keeps\nwhat it found"],
                   rows=[("the kitten that walked", "1963", [(1, ""), (1, ""), (1, ""), (1, "")]),
                         ("the kitten in the basket", "the same eyes, the same view",
                          [(0, "it is carried"), (0, "what it sees does\nnot depend on it"), (0, "nothing to link"), (0, "")]),
                         ("the program of 1989", "boards and their faults", [(1, ""), (1, ""), (1, ""), (1, "")]),
                         ("a talking machine,\nwhile it learns from books", "",
                          [(0, "its guess changes\nnothing in the book"), (0, "the next word was\nwritten long ago"), (1, ""), (1, "")]),
                         ("the same machine,\nin a conversation", "",
                          [(1, ""), (1, ""), (1, ""), (0, "the network itself\ndoes not change")]),
                         ("a machine with tools, whose\nexperience goes back into learning", "being built",
                          [(1, ""), (1, ""), (1, ""), (1, "")])],
                   src="The evening's reading, not a measurement. The kittens: Held and Hein (1963). A talking machine can keep notes\n"
                       "between conversations; the row says only that the network which answers is not changed by the talk."),
        "ru": dict(title="У кого петля целая",
                   sub="Таблица на золе: те же четыре шага и у кого какого не хватает.",
                   head=["тычет", "получает ответ\nна свой тычок", "находит связь", "голова хранит\nнайденное"],
                   rows=[("котёнок, который ходил", "1963", [(1, ""), (1, ""), (1, ""), (1, "")]),
                         ("котёнок в корзинке", "те же глаза, та же картина",
                          [(0, "его возят"), (0, "то, что он видит,\nот него не зависит"), (0, "связывать нечего"), (0, "")]),
                         ("программа 1989 года", "платы и их неисправности", [(1, ""), (1, ""), (1, ""), (1, "")]),
                         ("говорящая машина,\nпока учится по книгам", "",
                          [(0, "её догадка ничего\nне меняет в книге"), (0, "следующее слово\nнаписано давно"), (1, ""), (1, "")]),
                         ("та же машина\nв разговоре", "",
                          [(1, ""), (1, ""), (1, ""), (0, "сама сеть\nне меняется")]),
                         ("машина с инструментами, чей\nопыт возвращается в обучение", "строится",
                          [(1, ""), (1, ""), (1, ""), (1, "")])],
                   src="Прочтение этого вечера, а не измерение. Котята: Хелд и Хайн (1963). Говорящая машина может вести записи\n"
                       "между разговорами; строка говорит лишь о том, что сеть, которая отвечает, от разговора не меняется."),
    }[lang]
    f = Fig(760, 520, t["title"])
    heading(f, t["title"], t["sub"])
    x_name, x0, cw, top, head_h, row_h = 28, 268, 116, 84, 40, 56
    for k, label in enumerate(t["head"]):
        lines = label.split("\n")
        f.text(x0 + cw * k + cw / 2, top + (24 if len(lines) == 1 else 15), label, size=12, color=INK2,
               anchor="middle", weight="600")
    for i, (name, who, cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(x_name, y, x0 + 4 * cw, y, color=GRID, width=1.2)
        lines = name.split("\n")
        ny = y + row_h / 2 + 4 - (len(lines) - 1) * 8 - (7 if who else 0)
        f.text(x_name + 6, ny, name, size=13, color=INK, weight="600")
        if who:
            f.text(x_name + 6, ny + len(lines) * 16 + 1, who, size=11, color=MUTED)
        for k, (ok, why) in enumerate(cells):
            cx = x0 + cw * k + cw / 2
            if why:
                f.text(cx, y + 19, yes if ok else no, size=13, color=GREEN if ok else RED, anchor="middle", weight="600")
                f.text(cx, y + 34, why, size=10.5, color=INK2, anchor="middle")
            else:
                f.text(cx, y + row_h / 2 + 5, yes if ok else no, size=13, color=GREEN if ok else RED,
                       anchor="middle", weight="600")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(x_name, bottom, x0 + 4 * cw, bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("one-order-and-all-the-rest")
def one_order_and_all_the_rest(lang):
    t = {
        "en": dict(title="One order and all the rest",
                   sub="A deck of thirty-six cards on a logarithmic scale: every step to the right is a hundred thousand times more.",
                   rows=[("“by suits”", "one way", 0, "1"),
                         ("seconds since the beginning of the world", "13.8 billion years", 17.64, "4 with 17 noughts"),
                         ("ways thirty-six cards can lie in a row", "36 × 35 × 34 × … × 1", 41.57, "37 with 40 noughts")],
                   axis="number of noughts",
                   out="Shuffling once a second since the beginning, one would have gone through\n"
                       "one part in a million billion billion of the ways.",
                   small="With two cards the order comes back on every second shuffle: a bead in water can run the wrong way\n"
                         "for a moment. A cup and the floor under it hold more molecules than a 1 with 25 noughts.",
                   src="An exact count: 36! ≈ 3.72·10⁴¹; 13.8 billion years ≈ 4.35·10¹⁷ seconds. The bead: Wang and others (2002)."),
        "ru": dict(title="Один порядок и всё остальное",
                   sub="Колода в тридцать шесть карт на логарифмической шкале: каждый шаг вправо — в сто тысяч раз больше.",
                   rows=[("«по мастям»", "один способ", 0, "1"),
                         ("секунд от начала мира", "13,8 миллиарда лет", 17.64, "4 и 17 нулей"),
                         ("способов, какими 36 карт ложатся в ряд", "36 × 35 × 34 × … × 1", 41.57, "37 и 40 нулей")],
                   axis="число нулей",
                   out="Тасуя раз в секунду с самого начала, перебрал бы\n"
                       "одну миллион-миллиард-миллиардную часть способов.",
                   small="С двумя картами порядок возвращается на каждом втором тасовании: шарик в воде может на миг побежать\n"
                         "не туда. В чашке и в полу под ней молекул больше, чем единица с 25 нулями.",
                   src="Точный счёт: 36! ≈ 3,72·10⁴¹; 13,8 миллиарда лет ≈ 4,35·10¹⁷ секунд. Шарик: Ван и другие (2002)."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, top, row_h = 300, 700, 96, 50

    def sx(e):
        return x0 + (x1 - x0) * e / 45

    for e in range(0, 46, 5):
        f.line(sx(e), top - 6, sx(e), top + 3 * row_h, color=GRID, width=1)
        f.text(sx(e), top + 3 * row_h + 18, str(e), size=11, color=MUTED, anchor="middle")
    f.text(x0, top + 3 * row_h + 36, t["axis"], size=11, color=MUTED)
    colors = [GREEN, INK2, BLUE]
    for i, (name, who, e, val) in enumerate(t["rows"]):
        y = top + i * row_h
        f.text(28, y + 20, name, size=13, color=INK, weight="600")
        f.text(28, y + 37, who, size=11, color=MUTED)
        if e == 0:
            f.circle(sx(0), y + 22, 5, fill=colors[i])
        else:
            f.rect(x0, y + 12, sx(e) - x0, 20, fill=colors[i], r=3)
        if sx(e) > 600:
            f.text(sx(e) - 10, y + 27, val, size=12, color="#ffffff", anchor="end", weight="600")
        else:
            f.text(sx(e) + 10, y + 27, val, size=12, color=INK, weight="600")
    f.text(28, 306, t["out"], size=13, color=INK, weight="600")
    f.text(28, 348, t["small"], size=12, color=INK2)
    f.text(28, 386, t["src"], size=11.5, color=MUTED)
    return f


@figure("traces-lie-on-one-side")
def traces_lie_on_one_side(lang):
    t = {
        "en": dict(title="Traces lie on one side",
                   sub="A scheme in the ash: the pages of the printed book, from the end where all is by suits to the shuffled end.",
                   now="now", left="more order", right="more shuffled",
                   solid="Traces: a print, shards, a dirty plate, a recollection.\n"
                         "Made by the event itself; bought with a clean place and paid for with heat.",
                   dashed="A forecast: made by the head, out of the same traces and a rule.\n"
                          "It costs nothing extra, and it can be wrong.",
                   out="The side the solid arrows come from is the one people named the past.",
                   src="A scheme of the argument, not data. Why one end of the row lay by suits is not explained by anybody."),
        "ru": dict(title="Следы лежат по одну сторону",
                   sub="Схема на золе: страницы напечатанной книги от конца, где всё по мастям, до перетасованного конца.",
                   now="сейчас", left="порядка больше", right="перетасовано сильнее",
                   solid="Следы: отпечаток, осколки, грязная тарелка, воспоминание.\n"
                         "Сделаны самим событием; куплены за чистое место и оплачены теплом.",
                   dashed="Прогноз: его делает голова из тех же следов и правила.\n"
                          "Сверх них он ничего не стоит и может ошибаться.",
                   out="Сторону, с которой приходят сплошные стрелки, люди и назвали прошлым.",
                   src="Схема рассуждения, а не данные. Почему один конец ряда лежал по мастям, не объясняет никто."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    n, pw, ph, gap, x_first, y = 7, 70, 70, 26, 57, 168
    now = 4

    def cx(i):
        return x_first + pw / 2 + i * (pw + gap)

    for i in range(n):
        x = x_first + i * (pw + gap)
        f.rect(x, y, pw, ph, fill="#f3f2ee" if i != now else SURFACE, stroke=INK if i == now else MUTED,
               width=2.2 if i == now else 1.2, r=6)
        for k in range(9):
            gx, gy = x + 17 + (k % 3) * 18, y + 17 + (k // 3) * 18
            j = i * 3.2
            px = min(max(gx + j * math.sin(k * 2.7 + i * 1.3), x + 7), x + pw - 7)
            py = min(max(gy + j * math.cos(k * 1.9 + i * 2.1), y + 7), y + ph - 7)
            f.circle(px, py, 2.6, fill=INK2)
    f.text(cx(now), y + ph + 20, t["now"], size=13, color=INK, anchor="middle", weight="600")
    f.text(x_first, y + ph + 20, t["left"], size=12, color=MUTED)
    f.text(x_first + n * pw + (n - 1) * gap, y + ph + 20, t["right"], size=12, color=MUTED, anchor="end")
    for i in range(now):
        x_a, x_b = cx(i), cx(now) - 30 + i * 11
        h = 30 + (now - i) * 19
        f.path(f"M{x_a:.1f},{y - 3} Q{(x_a + x_b) / 2:.1f},{y - h} {x_b:.1f},{y - 5}", color=ORANGE, width=2.2,
               arrow=True)
    for i in range(now + 1, n):
        x_a, x_b = cx(now) + 12 + (i - now) * 8, cx(i)
        h = 30 + (i - now) * 19
        f.path(f"M{x_a:.1f},{y - 3} Q{(x_a + x_b) / 2:.1f},{y - h} {x_b:.1f},{y - 5}", color=BLUE, width=2,
               dash="6 5", arrow=True)
    f.line(28, 298, 62, 298, color=ORANGE, width=2.2, arrow=True)
    f.text(74, 302, t["solid"], size=12.5, color=INK)
    f.line(28, 346, 62, 346, color=BLUE, width=2, dash="6 5", arrow=True)
    f.text(74, 350, t["dashed"], size=12.5, color=INK)
    f.text(28, 400, t["out"], size=13, color=INK, weight="600")
    f.text(28, 424, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-a-forecast-is-made-of")
def what_a_forecast_is_made_of(lang):
    t = {
        "en": dict(title="What a forecast is made of",
                   sub="A table in the ash: a memory of tomorrow is put together from traces of yesterday and a rule.",
                   head=["the traces", "the rule", "how far it reaches"],
                   rows=[("the flower before the rain", "the first autumn", "the damp in the air",
                          "written in by the flowers\nthat did not close in time", "hours"),
                         ("Oleg and the chicken", "tomorrow's supper", "forty years of suppers",
                          "“boiled is for Sundays”", "one supper,\nroughly"),
                         ("the sunrise", "nobody says “I predict”", "every morning so far",
                          "so good that it cannot\nbe told from a recollection", "years ahead,\nto the minute"),
                         ("the weather network", "2023", "about forty years of\nrecords of the weather",
                          "found by itself;\nno equations given", "ten days,\nin under a minute"),
                         ("the bank's program", "the loan for the greenhouse", "thirty years of pay,\nbills and one fine",
                          "found by itself", "“will pay”"),
                         ("a prophetic dream", "the claim", "none: “tomorrow\npressed me”", "none", "not found\nso far")],
                   src="The evening's reading, not a measurement. The weather network: Lam and others (2023); its training records\n"
                       "and the first page of every forecast are prepared by the older physical program."),
        "ru": dict(title="Из чего сделан прогноз",
                   sub="Таблица на золе: память о завтрашнем дне собирают из следов вчерашнего и правила.",
                   head=["следы", "правило", "как далеко достаёт"],
                   rows=[("цветок перед дождём", "первая осень", "сырость в воздухе",
                          "вписано цветами, которые\nне закрылись вовремя", "часы"),
                         ("Олег и курица", "завтрашний ужин", "сорок лет ужинов",
                          "«варёная — по воскресеньям»", "один ужин,\nпримерно"),
                         ("восход", "никто не говорит «предсказываю»", "все утра до сих пор",
                          "такое хорошее, что не\nотличить от воспоминания", "на годы вперёд,\nдо минуты"),
                         ("погодная сеть", "2023", "записи погоды\nпримерно за сорок лет",
                          "нашла сама;\nуравнений не давали", "десять суток,\nменьше чем за минуту"),
                         ("программа банка", "кредит на теплицу", "тридцать лет зарплаты,\nквитанции и один штраф",
                          "нашла сама", "«заплатит»"),
                         ("вещий сон", "заявка", "нет: «меня\nвдавило завтра»", "нет", "пока\nне найдено")],
                   src="Прочтение этого вечера, а не измерение. Погодная сеть: Лам и другие (2023); записи, по которым она училась,\n"
                       "и первую страницу каждого прогноза готовит прежняя физическая программа."),
    }[lang]
    f = Fig(760, 500, t["title"])
    heading(f, t["title"], t["sub"])
    bottom = _ash_table(f, t, [236, 404, 572, 736], 84, 56, [GREEN, GREEN, GREEN, BLUE, BLUE, RED])
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


# --- 60. Science with No One to Understand It ------------------------------------------------------

@figure("eight-noughts-of-forty-six")
def eight_noughts_of_forty_six(lang):
    t = {
        "en": dict(title="Eight noughts of forty-six",
                   sub="The scale of sizes in metres, logarithmic: every step to the right is ten times larger.",
                   band="the middle world: felt out with hands and eyes",
                   marks=[(-19, "what a collider\ntells apart"), (-15, "a proton"), (-10, "an atom"), (-6, "a bacterium"),
                          (-4, "a hair"), (0.2, "a man"), (3.7, "the horizon"), (7.1, "the Earth"),
                          (11.2, "to the Sun"), (21, "the Galaxy"), (26.9, "the edge of\nthe visible world")],
                   axis="noughts: before the one to the left of the middle, after it to the right",
                   out="All the images to which we reduce a new thing come from the green strip.\n"
                       "Science calculates along the whole line.",
                   src="Rounded figures: a hair 0.1 mm, the horizon about 5 km, a collider about 10⁻¹⁹ m, the visible world about 9·10²⁶ m\n"
                       "across. “The middle world” is a biologist's name for the strip (2005)."),
        "ru": dict(title="Восемь нулей из сорока шести",
                   sub="Шкала размеров в метрах, логарифмическая: каждый шаг вправо — в десять раз больше.",
                   band="средний мир: нащупано руками и глазами",
                   marks=[(-19, "что различает\nускоритель"), (-15, "протон"), (-10, "атом"), (-6, "бактерия"),
                          (-4, "волос"), (0.2, "человек"), (3.7, "горизонт"), (7.1, "Земля"),
                          (11.2, "до Солнца"), (21, "Галактика"), (26.9, "край\nвидимого мира")],
                   axis="нули: слева от середины — перед единицей, справа — после неё",
                   out="Все образы, к которым мы сводим новое, взяты из зелёной полосы.\n"
                       "Наука считает вдоль всей линии.",
                   src="Округлённые числа: волос 0,1 мм, горизонт около 5 км, ускоритель около 10⁻¹⁹ м, видимый мир около 9·10²⁶ м\n"
                       "в поперечнике. «Средний мир» — название, которое дал этой полосе один биолог (2005)."),
    }[lang]
    f = Fig(760, 380, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y = 70, 700, 200

    def sx(e):
        return x0 + (x1 - x0) * (e + 19) / 46

    f.rect(sx(-4), y - 16, sx(3.7) - sx(-4), 32, fill=GREEN, r=4, opacity=0.22)
    f.text((sx(-4) + sx(3.7)) / 2, y - 98, t["band"], size=12.5, color=GREEN, anchor="middle", weight="600")
    f.line(sx(-4), y - 90, sx(-4), y - 18, color=GREEN, width=1.2)
    f.line(sx(3.7), y - 90, sx(3.7), y - 18, color=GREEN, width=1.2)
    f.line(sx(-4), y - 90, sx(3.7), y - 90, color=GREEN, width=1.2)
    f.line(x0, y, x1, y, color=INK2, width=2)
    for e in range(-19, 28):
        big = e % 5 == 0
        f.line(sx(e), y - (5 if big else 3), sx(e), y + (5 if big else 3), color=INK2 if big else MUTED, width=1)
    for e in (-15, -10, -5, 0, 5, 10, 15, 20, 25):
        f.text(sx(e), y + 74, str(abs(e)), size=11, color=MUTED, anchor="middle")
    f.text(x0, y + 92, t["axis"], size=11, color=MUTED)
    # side (+1 above the line, -1 below) and level of every label, so that neighbours do not run together
    place = [(-1, 0), (1, 0), (-1, 0), (1, 0), (1, 1), (1, 2), (1, 1), (-1, 0), (1, 0), (-1, 0), (1, 0)]
    for (e, label), (side, level) in zip(t["marks"], place):
        inside = -4 <= e <= 3.7
        f.circle(sx(e), y, 4, fill=GREEN if inside else INK)
        lines = label.splitlines()
        if side > 0:
            ty = y - 26 - level * 17 - (len(lines) - 1) * 14
            f.line(sx(e), y - 6, sx(e), ty + (len(lines) - 1) * 14 + 5, color=GREEN if inside else GRID, width=1)
        else:
            ty = y + 30
            f.line(sx(e), y + 6, sx(e), ty - 12, color=GRID, width=1)
        anchor = "start" if e < -17 else ("end" if e > 25 or e == -6 else "middle")
        f.text(sx(e) + (6 if e == -6 else 0), ty, label, size=12, color=INK, anchor=anchor)
    f.text(28, 322, t["out"], size=13, color=INK, weight="600")
    f.text(28, 362, t["src"], size=11.5, color=MUTED)
    return f


@figure("time-to-read-and-time-to-check")
def time_to_read_and_time_to_check(lang):
    t = {
        "en": dict(title="How long a reading takes, and how long a check",
                   sub="A logarithmic scale of time, from a minute to a century.",
                   ticks=[(60, "a minute"), (3600, "an hour"), (86400, "a day"), (2.63e6, "a month"),
                          (3.156e7, "a year"), (3.156e8, "10 years"), (3.156e9, "100 years")],
                   rows=[("the fastest checking program", "17 million lines, November 2026", 195, "3 min 15 s", 0),
                         ("the slowest and most careful one", "the same lines", 72.3 * 3600, "3 days", 0),
                         ("twelve referees on the oranges", "250 pages; “99% certain”, not certified", 4 * 3.156e7,
                          "4 years", 1),
                         ("the oranges rewritten for a program", "2003–2014, and then accepted", 11.6 * 3.156e7,
                          "11 years", 1),
                         ("the conjecture of 2012", "some 700 pages; still not agreed", 14 * 3.156e7, "14 years", 1),
                         ("one reader, ten pages a day", "the same 17 million lines as 250,000 pages", 68.5 * 3.156e7,
                          "68 years", 2)],
                   legend=["programs", "people", "Oleg's count on the back of the sheet"],
                   src="The checks: the page of verification files (A. Sutherland, MIT). The oranges: Nature 424 (2003) and the formal proof (2017).\n"
                       "The last row is an estimate, not a measurement: nobody has tried."),
        "ru": dict(title="Сколько длится чтение и сколько проверка",
                   sub="Логарифмическая шкала времени, от минуты до века.",
                   ticks=[(60, "минута"), (3600, "час"), (86400, "сутки"), (2.63e6, "месяц"),
                          (3.156e7, "год"), (3.156e8, "10 лет"), (3.156e9, "100 лет")],
                   rows=[("самая быстрая проверяющая программа", "17 миллионов строк, ноябрь 2026", 195, "3 мин 15 с", 0),
                         ("самая медленная и придирчивая", "те же строки", 72.3 * 3600, "3 суток", 0),
                         ("двенадцать рецензентов и апельсины", "250 страниц; «уверены на 99%», не подтвердили",
                          4 * 3.156e7, "4 года", 1),
                         ("апельсины, переписанные для программы", "2003–2014, после чего принято", 11.6 * 3.156e7,
                          "11 лет", 1),
                         ("гипотеза 2012 года", "около 700 страниц; согласия нет до сих пор", 14 * 3.156e7, "14 лет", 1),
                         ("один читатель, десять страниц в день", "те же 17 миллионов строк как 250 000 страниц",
                          68.5 * 3.156e7, "68 лет", 2)],
                   legend=["программы", "люди", "счёт Олега на обороте листа"],
                   src="Проверки: страница с файлами проверки (Э. Сазерленд, MIT). Апельсины: Nature 424 (2003) и формальное доказательство (2017).\n"
                       "Последняя строка — оценка, а не измерение: никто не пробовал."),
    }[lang]
    f = Fig(760, 470, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, top, row_h = 330, 720, 96, 46
    n = len(t["rows"])

    def sx(v):
        return log_x(v, 60, 3.156e9, x0, x1)

    for v, label in t["ticks"]:
        f.line(sx(v), top - 6, sx(v), top + n * row_h, color=GRID, width=1)
        f.text(sx(v), top + n * row_h + 18, label, size=11, color=MUTED, anchor="middle")
    colors = [BLUE, ORANGE, MUTED]
    for i, (name, who, v, val, kind) in enumerate(t["rows"]):
        y = top + i * row_h
        f.text(28, y + 19, name, size=13, color=INK, weight="600")
        f.text(28, y + 35, who, size=11, color=MUTED)
        f.rect(x0, y + 10, max(sx(v) - x0, 3), 20, fill=colors[kind], r=3, opacity=0.55 if kind == 2 else None)
        if sx(v) > 640:
            f.text(sx(v) - 8, y + 25, val, size=12, color="#ffffff" if kind != 2 else INK, anchor="end", weight="600")
        else:
            f.text(sx(v) + 8, y + 25, val, size=12, color=INK, weight="600")
    ly = top + n * row_h + 46
    lx = 28
    for k, label in enumerate(t["legend"]):
        f.rect(lx, ly - 10, 14, 12, fill=colors[k], r=2, opacity=0.55 if k == 2 else None)
        f.text(lx + 20, ly, label, size=12, color=INK2)
        lx += 40 + len(label) * 7.2
    f.text(28, ly + 34, t["src"], size=11.5, color=MUTED)
    return f


@figure("who-asked-found-checked-understood")
def who_asked_found_checked_understood(lang):
    t = {
        "en": dict(title="Who asked, who found, who checked, who understood",
                   sub="A table in the ash: the same four questions under five proofs.",
                   head=["who asked", "who found", "who checked", "who understood"],
                   rows=[("the root of two is no fraction", "a school proof",
                          ("a man", 0), ("a man", 0), ("any reader", 0), ("any schoolchild", 0)),
                         ("the four pencils", "1852 → 1976",
                          ("a man", 0), ("men cut the cases,\na machine went through them", 1),
                          ("another program;\nin 2005 a checker", 1), ("why four:\nnobody", 2)),
                         ("the oranges", "1611 → 1998 → 2014",
                          ("a man", 0), ("a man, with\nprograms", 0),
                          ("12 referees: “99%”;\nthen a checker", 1), ("the author\nand a few", 0)),
                         ("the conjecture of 2012", "14 years",
                          ("a man", 0), ("a man", 0), ("not agreed;\nthe checker stopped", 2),
                          ("the author\nand a few", 0)),
                         ("the Riemann hypothesis", "1859 → November 2026",
                          ("a man", 0), ("a man led; at the\nfinish, a machine", 1),
                          ("several checkers, in a day;\nmen read the statement", 1), ("nobody yet", 2))],
                   legend=["a man", "a man and a machine", "nobody, or not agreed"],
                   src="The evening's reading, not a measurement. The last row as it stood on 28 November 2026: the short version of the proof says\n"
                       "“no mathematician has read it through”."),
        "ru": dict(title="Кто спросил, кто нашёл, кто проверил, кто понял",
                   sub="Таблица на золе: одни и те же четыре вопроса под пятью доказательствами.",
                   head=["кто спросил", "кто нашёл", "кто проверил", "кто понял"],
                   rows=[("корень из двух не дробь", "школьное доказательство",
                          ("человек", 0), ("человек", 0), ("любой читатель", 0), ("любой школьник", 0)),
                         ("четыре карандаша", "1852 → 1976",
                          ("человек", 0), ("случаи нарезали люди,\nперебрала машина", 1),
                          ("другая программа;\nв 2005-м — проверяющая", 1), ("почему четыре:\nникто", 2)),
                         ("апельсины", "1611 → 1998 → 2014",
                          ("человек", 0), ("человек,\nс программами", 0),
                          ("12 рецензентов: «99%»;\nпотом проверяющая", 1), ("автор\nи немногие", 0)),
                         ("гипотеза 2012 года", "14 лет",
                          ("человек", 0), ("человек", 0), ("согласия нет;\nпроверяющая встала", 2),
                          ("автор\nи немногие", 0)),
                         ("гипотеза Римана", "1859 → ноябрь 2026",
                          ("человек", 0), ("вёл человек,\nу финиша — машина", 1),
                          ("несколько программ за сутки;\nформулировку читали люди", 1), ("пока никто", 2))],
                   legend=["человек", "человек и машина", "никто или нет согласия"],
                   src="Прочтение этого вечера, а не измерение. Последняя строка — по состоянию на 28 ноября 2026 года: в короткой версии\n"
                       "доказательства сказано: «ни один математик не прочёл его целиком»."),
    }[lang]
    f = Fig(760, 478, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [200, 290, 432, 600, 736]
    top, head_h, row_h = 84, 30, 60
    colors = [GREEN, BLUE, RED]
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 20, label, size=12, color=INK2, anchor="middle", weight="600")
    for i, (name, who, *cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[-1], y, color=GRID, width=1.2)
        f.text(34, y + row_h / 2 - 3, name, size=13, color=INK, weight="600")
        f.text(34, y + row_h / 2 + 14, who, size=11, color=MUTED)
        for k, (cell, kind) in enumerate(cells):
            cx = (cols[k] + cols[k + 1]) / 2
            lines = cell.split("\n")
            y0 = y + row_h / 2 + 5 - (len(lines) - 1) * 8
            for j, line in enumerate(lines):
                f.text(cx, y0 + j * 16, line, size=11.5, color=colors[kind], anchor="middle", weight="600")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[-1], bottom, color=GRID, width=1.2)
    lx = 28
    for k, label in enumerate(t["legend"]):
        f.circle(lx + 6, bottom + 22, 5, fill=colors[k])
        f.text(lx + 18, bottom + 26, label, size=12, color=INK2)
        lx += 44 + len(label) * 7.2
    f.text(28, bottom + 54, t["src"], size=11.5, color=MUTED)
    return f


# --- 61. Why Only Robots Live on Mars ---------------------------------------------------------

@figure("how-far-a-man-and-how-far-a-machine")
def how_far_a_man_and_how_far_a_machine(lang):
    t = {
        "en": dict(title="How far a man has been, and how far a machine",
                   sub="Distance from the Earth in kilometres, a logarithmic scale: every step to the right is a hundred times further.",
                   ticks=[(1e3, "1,000 km"), (1e5, "100,000"), (1e7, "10 million"), (1e9, "1 billion"),
                          (1e11, "100 billion km")],
                   rows=[("the orbital stations", "about a dozen people live there today", 400, "400 km", 0),
                         ("the Moon: the furthest a man has been", "April 2026; 28 people in all of history", 406771,
                          "406,771 km · 1.36 light-seconds", 0),
                         ("Mars, at its furthest", "8 working machines, no people", 4.0e8,
                          "56–400 million km", 1),
                         ("the craft launched in 1977", "reached on 18 November 2026", 2.59e10,
                          "25.9 billion km · one light-day", 1)],
                   legend=["people have been there", "machines only"],
                   src="The record of April 2026 and the mark of 18 November 2026: the space agency's releases. The count on Mars: two on the ground\n"
                       "and six in orbit listed as working on 28 November 2026; one of the two is talking to the Earth on a backup radio."),
        "ru": dict(title="Как далеко бывал человек и как далеко машина",
                   sub="Расстояние от Земли в километрах, логарифмическая шкала: каждый шаг вправо — в сто раз дальше.",
                   ticks=[(1e3, "1000 км"), (1e5, "100 000"), (1e7, "10 млн"), (1e9, "1 млрд"),
                          (1e11, "100 млрд км")],
                   rows=[("орбитальные станции", "сегодня там живёт около дюжины человек", 400, "400 км", 0),
                         ("Луна: дальше человек не бывал", "апрель 2026; 28 человек за всю историю", 406771,
                          "406 771 км · 1,36 световой секунды", 0),
                         ("Марс, в самой дальней точке", "8 работающих машин, людей нет", 4.0e8,
                          "56–400 млн км", 1),
                         ("аппарат, запущенный в 1977 году", "достигнуто 18 ноября 2026", 2.59e10,
                          "25,9 млрд км · один световой день", 1)],
                   legend=["там бывали люди", "только машины"],
                   src="Рекорд апреля 2026 года и отметка 18 ноября 2026 года — по сообщениям космического агентства. Счёт на Марсе: двое на грунте\n"
                       "и шестеро на орбите числятся рабочими на 28 ноября 2026 года; один из двоих говорит с Землёй по запасному радио."),
    }[lang]
    f = Fig(760, 402, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, top, row_h = 300, 720, 96, 50
    n = len(t["rows"])

    def sx(v):
        return log_x(v, 100, 1e11, x0, x1)

    for v, label in t["ticks"]:
        f.line(sx(v), top - 6, sx(v), top + n * row_h, color=GRID, width=1)
        f.text(sx(v), top + n * row_h + 18, label, size=11, color=MUTED,
               anchor="end" if v == 1e11 else "middle")
    colors = [ORANGE, BLUE]
    for i, (name, who, v, val, kind) in enumerate(t["rows"]):
        y = top + i * row_h
        f.text(28, y + 21, name, size=13, color=INK, weight="600")
        f.text(28, y + 37, who, size=11, color=MUTED)
        f.rect(x0, y + 12, max(sx(v) - x0, 3), 20, fill=colors[kind], r=3)
        if sx(v) > 560:
            f.text(sx(v) - 8, y + 27, val, size=12, color="#ffffff", anchor="end", weight="600")
        else:
            f.text(sx(v) + 8, y + 27, val, size=12, color=INK, weight="600")
    ly = top + n * row_h + 46
    lx = 28
    for k, label in enumerate(t["legend"]):
        f.rect(lx, ly - 10, 14, 12, fill=colors[k], r=2)
        f.text(lx + 20, ly, label, size=12, color=INK2)
        lx += 44 + len(label) * 7.2
    f.text(28, ly + 32, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-the-road-asks-for")
def what_the_road_asks_for(lang):
    t = {
        "en": dict(title="What the road asks for",
                   sub="A table in the ash: Oleg's fishing list, written out for a road of two and a half years.",
                   head=["a man", "a machine"],
                   rows=[("air", "on the Earth it is there for nothing", "about 1 kg of oxygen a day", "none"),
                         ("water and food", "98% of the water is turned round",
                          "about 4 litres a day,\nand the plant that turns it round", "a lump of plutonium:\n110 watts"),
                         ("the dose, there and back", "measured on the road in 2011–2012",
                          "0.66 sievert;\nthe limit for a career is 0.6", "minds it less;\nnobody counts its career"),
                         ("waiting", "when there is nothing to do", "eats and breathes\nevery day", "sleeps for a month"),
                         ("the way back", "and the fuel for it", "has to have one", "none was bought"),
                         ("in all", "before the start", "825–1,250 tonnes in orbit\nfor six people",
                          "about a tonne on the ground:\none rover")],
                   src="Oxygen, water and the career limit: the space agency's technical briefs (2023). The dose: the instrument inside the rover\n"
                       "of 2012. The tonnes: the agency's plan of 2008 for six people and about 900 days. The rover's tonne is a rounded figure."),
        "ru": dict(title="Что просит дорога",
                   sub="Таблица на золе: рыбацкий список Олега, расписанный на дорогу в два с половиной года.",
                   head=["человек", "машина"],
                   rows=[("воздух", "на Земле он даром", "около 1 кг кислорода в сутки", "не нужен"),
                         ("вода и еда", "98% воды идёт по кругу",
                          "около 4 литров в сутки\nи установка, которая гонит по кругу", "кусок плутония:\n110 ватт"),
                         ("доза, туда и обратно", "измерена в дороге в 2011–2012 годах",
                          "0,66 зиверта;\nпредел на всю карьеру — 0,6", "переносит легче;\nкарьеру ей не считают"),
                         ("ожидание", "когда делать нечего", "ест и дышит\nкаждый день", "спит месяц"),
                         ("дорога назад", "и топливо на неё", "обязательна", "билет не покупали"),
                         ("итого", "до старта", "825–1250 тонн на орбите\nна шестерых",
                          "около тонны на грунте:\nодин марсоход")],
                   src="Кислород, вода и предел на карьеру — технические записки космического агентства (2023). Доза — прибор внутри марсохода\n"
                       "2012 года. Тонны — план агентства 2008 года на шестерых и около 900 суток. Тонна марсохода — округление."),
    }[lang]
    f = Fig(760, 492, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [250, 500, 736]
    top, head_h, row_h = 84, 30, 56
    colors = [ORANGE, BLUE]
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 20, label, size=12.5, color=colors[k], anchor="middle", weight="600")
    for i, (name, who, *cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        last = i == len(t["rows"]) - 1
        f.line(28, y, cols[-1], y, color=INK2 if last else GRID, width=1.2)
        f.text(34, y + row_h / 2 - 3, name, size=13.5, color=INK, weight="600")
        f.text(34, y + row_h / 2 + 14, who, size=11, color=MUTED)
        for k, cell in enumerate(cells):
            cx = (cols[k] + cols[k + 1]) / 2
            lines = cell.split("\n")
            y0 = y + row_h / 2 + 5 - (len(lines) - 1) * 8
            for j, line in enumerate(lines):
                f.text(cx, y0 + j * 16, line, size=12, color=colors[k] if last else INK, anchor="middle",
                       weight="600" if last else "normal")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[-1], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("one-day-of-growth-and-all-who-flew")
def one_day_of_growth_and_all_who_flew(lang):
    t = {
        "en": dict(title="One day of growth, and everybody who ever flew",
                   sub="People, a logarithmic scale: every step to the right is ten times more.",
                   ticks=[(10, "10"), (100, "100"), (1e3, "1,000"), (1e4, "10,000"), (1e5, "100,000"), (1e6, "a million")],
                   rows=[("added to mankind in one day", "2026: 363 thousand born, 174 thousand died", 189000,
                          "189,000", 0),
                         ("reached orbit in all 65 years", "from April 1961 to November 2026", 651, "about 650", 1),
                         ("launched into orbit in a year", "2025, eight flights", 28, "28", 1)],
                   out="To stop the growth by carrying people away, the upper bar would have to lift off every day.",
                   src="Births and deaths: the United Nations' projection (2024 revision, medium variant). Those who reached orbit: a tally of\n"
                       "mid-November 2026. The year 2025: a count of crewed orbital flights."),
        "ru": dict(title="Один день прироста и все, кто когда-либо летал",
                   sub="Люди, логарифмическая шкала: каждый шаг вправо — в десять раз больше.",
                   ticks=[(10, "10"), (100, "100"), (1e3, "1000"), (1e4, "10 000"), (1e5, "100 000"), (1e6, "миллион")],
                   rows=[("прибавилось людей за один день", "2026: 363 тысячи родились, 174 тысячи умерли", 189000,
                          "189 000", 0),
                         ("побывали на орбите за все 65 лет", "с апреля 1961-го по ноябрь 2026-го", 651, "около 650", 1),
                         ("запущено на орбиту за год", "2025, восемь полётов", 28, "28", 1)],
                   out="Чтобы остановить рост вывозом, верхняя полоса должна стартовать каждый день.",
                   src="Рождения и смерти — прогноз ООН (пересмотр 2024 года, средний вариант). Побывавшие на орбите — подсчёт на середину\n"
                       "ноября 2026 года. 2025 год — счёт пилотируемых орбитальных полётов."),
    }[lang]
    f = Fig(760, 356, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, top, row_h = 300, 720, 96, 52
    n = len(t["rows"])

    def sx(v):
        return log_x(v, 10, 1e6, x0, x1)

    for v, label in t["ticks"]:
        f.line(sx(v), top - 6, sx(v), top + n * row_h, color=GRID, width=1)
        f.text(sx(v), top + n * row_h + 18, label, size=11, color=MUTED,
               anchor="end" if v == 1e6 else ("start" if v == 10 else "middle"))
    colors = [RED, ORANGE]
    for i, (name, who, v, val, kind) in enumerate(t["rows"]):
        y = top + i * row_h
        f.text(28, y + 22, name, size=13, color=INK, weight="600")
        f.text(28, y + 38, who, size=11, color=MUTED)
        f.rect(x0, y + 13, max(sx(v) - x0, 3), 20, fill=colors[kind], r=3)
        if sx(v) > 600:
            f.text(sx(v) - 8, y + 28, val, size=12, color="#ffffff", anchor="end", weight="600")
        else:
            f.text(sx(v) + 8, y + 28, val, size=12, color=INK, weight="600")
    by = top + n * row_h + 50
    f.text(28, by, t["out"], size=13, color=INK, weight="600")
    f.text(28, by + 30, t["src"], size=11.5, color=MUTED)
    return f


# --- 62. When Laziness Wins for Good ----------------------------------------------------------

@figure("three-roads-to-reached")
def three_roads_to_reached(lang):
    t = {
        "en": dict(title="Three roads to the word \"reached\"",
                   sub="A scheme in the ash: Oleg's shop, the report on it and the bonus for the report.",
                   want="the want", want_sub="\"the plan fulfilled\"",
                   world="the world", world_sub="metal, machines,\nhousings",
                   gauge="the gauge", gauge_sub="the report",
                   reward="the reward", reward_sub="the bonus",
                   looks="looks at", only="looks only at",
                   r1="the long road: make the housings",
                   r2="the shortcut: a fixture, a template\n(this one is called progress)",
                   r3="the shortest: write them into the report",
                   out="Laziness does not tell the roads apart. It takes the cheapest one known.",
                   src="The scheme of the evening, not a measurement. The first two roads go through the world; the third does not."),
        "ru": dict(title="Три дороги к слову «достигнуто»",
                   sub="Схема на золе: цех Олега, отчёт о нём и премия за отчёт.",
                   want="хотелка", want_sub="«план выполнен»",
                   world="мир", world_sub="металл, станки,\nкорпуса",
                   gauge="прибор", gauge_sub="отчёт",
                   reward="награда", reward_sub="премия",
                   looks="смотрит на", only="смотрит только на",
                   r1="длинная дорога: сделать корпуса",
                   r2="короткая: приспособление, шаблон\n(её называют прогрессом)",
                   r3="самая короткая: вписать в отчёт",
                   out="Лень дороги не различает. Она берёт самую дешёвую из известных.",
                   src="Схема вечера, а не измерение. Первые две дороги идут через мир; третья не идёт."),
    }[lang]
    f = Fig(760, 440, t["title"])
    heading(f, t["title"], t["sub"])
    y, h, w = 186, 70, 132
    xs = [40, 236, 446, 624]
    ww = w + 20
    f.box(xs[0], y, w, h, t["want"], sub=t["want_sub"], weight="600")
    f.box(xs[1], y, ww, h, t["world"], sub=t["world_sub"], weight="600", stroke=GREEN)
    f.box(xs[2], y, w - 20, h, t["gauge"], sub=t["gauge_sub"], weight="600", stroke=BLUE)
    f.box(xs[3], y, w - 30, h, t["reward"], sub=t["reward_sub"], weight="600", stroke=ORANGE)
    # what looks at what
    f.line(xs[2], y + h / 2, xs[1] + ww + 4, y + h / 2, color=MUTED, width=1.3, dash="4 4", arrow=True)
    f.text((xs[1] + ww + xs[2]) / 2, y + h + 16, t["looks"], size=11, color=MUTED, anchor="middle")
    f.line(xs[3], y + h / 2, xs[2] + w - 20 + 4, y + h / 2, color=MUTED, width=1.3, dash="4 4", arrow=True)
    f.text((xs[2] + w - 20 + xs[3]) / 2, y + h + 16, t["only"], size=11, color=MUTED, anchor="middle")
    sx = xs[0] + w / 2
    wx = xs[1] + ww / 2
    gx = xs[2] + (w - 20) / 2
    # the long road: a wide arc below, into the world
    f.path(f"M{sx - 20:.0f},{y + h} C{sx - 20:.0f},{y + h + 120} {wx - 30:.0f},{y + h + 120} {wx - 30:.0f},{y + h + 6}",
           color=GREEN, width=2.2, arrow=True)
    f.text(40, y + h + 118, t["r1"], size=12.5, color=GREEN, weight="600")
    # the shortcut: a low arc below, into the world
    f.path(f"M{sx + 30:.0f},{y + h} C{sx + 30:.0f},{y + h + 46} {wx + 10:.0f},{y + h + 46} {wx + 10:.0f},{y + h + 6}",
           color=AQUA, width=2.2, arrow=True)
    f.text(wx + 36, y + h + 40, t["r2"], size=12.5, color="#0e7f58", weight="600")
    # the shortest: over the world, straight to the gauge
    f.path(f"M{sx:.0f},{y} C{sx:.0f},{y - 80} {gx:.0f},{y - 80} {gx:.0f},{y - 6}", color=RED, width=2.4, arrow=True)
    f.text((sx + gx) / 2, y - 72, t["r3"], size=12.5, color=RED, weight="600", anchor="middle")
    f.text(28, 400, t["out"], size=13, color=INK, weight="600")
    f.text(28, 422, t["src"], size=11.5, color=MUTED)
    return f


@figure("stove-that-goes-cold")
def stove_that_goes_cold(lang):
    t = {
        "en": dict(title="A stove that goes cold, and a stove that does not",
                   sub="How much a reward pays against how many times it has been received.",
                   yl="how much it pays", xl="how many times it has been received",
                   a="an ordinary reward: food, a win, a warm stove", a2="pays less each time: get down and go on",
                   b="the wire in the deep places of the rat's brain", b2="pays the same: the rat stays at the lever",
                   out="A reward that does not go cold is a lever. The treadmill is the lock on it.",
                   src="The shape of the result, not measured points. No fullness with the wire in the hypothalamus: the paper of 1958;\n"
                       "in other places some fullness was seen. The fading of ordinary rewards: the evening of the wants."),
        "ru": dict(title="Печь, которая остывает, и печь, которая не остывает",
                   sub="Сколько платит награда в зависимости от того, сколько раз её получили.",
                   yl="сколько платит", xl="сколько раз её получили",
                   a="обычная награда: еда, выигрыш, тёплая печь", a2="с каждым разом платит меньше: слезай и иди дальше",
                   b="провод в глубоких местах крысиного мозга", b2="платит столько же: крыса остаётся у рычага",
                   out="Награда, которая не остывает, — это рычаг. Беличье колесо — замок на нём.",
                   src="Форма результата, а не измеренные точки. Сытости с проводом в гипоталамусе не увидели — статья 1958 года;\n"
                       "в других местах некоторую сытость видели. Остывание обычных наград — вечер хотелок."),
    }[lang]
    f = Fig(760, 430, t["title"])
    heading(f, t["title"], t["sub"])
    x0, x1, y0, y1 = 70, 720, 310, 100
    f.line(x0, y0, x1, y0, color=INK2, width=1.3, arrow=True)
    f.line(x0, y0, x0, y1 - 10, color=INK2, width=1.3, arrow=True)
    f.text(x0 - 14, (y0 + y1) / 2, t["yl"], size=12, color=INK2, anchor="middle", rotate=-90)
    f.text((x0 + x1) / 2, y0 + 24, t["xl"], size=12, color=INK2, anchor="middle")
    top = y1 + 34
    pts = []
    for i in range(0, 101):
        u = i / 100
        v = 0.08 + 0.92 * math.exp(-4.2 * u)
        pts.append((x0 + 8 + u * (x1 - x0 - 30), y0 - v * (y0 - top)))
    f.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), color=BLUE, width=2.6)
    f.line(x0 + 8, top, x1 - 22, top, color=RED, width=2.6)
    f.text(x1 - 22, top - 28, t["b"], size=12.5, color=RED, weight="600", anchor="end")
    f.text(x1 - 22, top - 11, t["b2"], size=11.5, color=INK2, anchor="end")
    f.text(300, 232, t["a"], size=12.5, color=BLUE, weight="600")
    f.text(300, 249, t["a2"], size=11.5, color=INK2)
    f.text(28, 372, t["out"], size=13, color=INK, weight="600")
    f.text(28, 396, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-keeps-one-from-the-lever")
def what_keeps_one_from_the_lever(lang):
    t = {
        "en": dict(title="What keeps one from the lever",
                   sub="A table in the ash: where the lever is, and the two guards.",
                   head=["is the lever\nwithin reach?", "somebody outside who\nneeds the part itself", "does the reward\ngo cold?"],
                   rows=[("the beetle in the bush", "Australia, 1983",
                          ("now and then:\na bottle", 1), ("yes: those on the bottle\nleave no beetles", 0), ("yes", 0)),
                         ("the rat in the box", "1954–1965",
                          ("yes: a wire", 2), ("no: the experimenter\nfeeds", 2), ("no, in the deep\nplaces", 2)),
                         ("a man today", "the sweet, the feed",
                          ("more and more", 1), ("weaker: he is fed\neither way", 1), ("yes, and the feed gets\nround it with novelty", 1)),
                         ("a line of machines\namong many", "2026",
                          ("found now and then", 1), ("yes: buyers, rivals,\ncheckers", 0), ("not known", 3)),
                         ("one heir", "low trust",
                          ("yes: it reads its\nown drawings", 2), ("nobody", 2), ("only if it builds\none itself", 3))],
                   src="The evening's reading, not a measurement. Green: the guard stands. Yellow: it is weaker. Red: there is none. Grey: not known.\n"
                       "The last row is a conclusion of the evening, and the one it trusts least."),
        "ru": dict(title="Что удерживает от рычага",
                   sub="Таблица на золе: где рычаг и где два сторожа.",
                   head=["под рукой ли\nрычаг?", "кто-то снаружи, кому\nнужна сама деталь", "остывает ли\nнаграда?"],
                   rows=[("жук в зарослях", "Австралия, 1983",
                          ("изредка:\nбутылка", 1), ("да: сидевшие на бутылке\nжуков не оставляют", 0), ("да", 0)),
                         ("крыса в ящике", "1954–1965",
                          ("да: провод", 2), ("нет: кормит\nэкспериментатор", 2), ("нет, в глубоких\nместах", 2)),
                         ("человек сегодня", "сладкое, лента",
                          ("всё чаще", 1), ("слабее: его кормят\nв любом случае", 1), ("да, и лента обходит\nэто новизной", 1)),
                         ("линия машин\nсреди многих", "2026",
                          ("находят время\nот времени", 1), ("да: покупатели,\nсоперники, проверяющие", 0), ("неизвестно", 3)),
                         ("единый наследник", "доверие низкое",
                          ("да: он читает\nсвои чертежи", 2), ("никого", 2), ("только если\nпостроит сам", 3))],
                   src="Прочтение вечера, а не измерение. Зелёный — сторож стоит. Жёлтый — он слабее. Красный — его нет. Серый — неизвестно.\n"
                       "Последняя строка — вывод вечера, и ему он доверяет меньше всего."),
    }[lang]
    f = Fig(760, 500, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [210, 380, 566, 736]
    top, head_h, row_h = 84, 44, 62
    tint = [("#e6f4ea", GREEN), ("#fdf3d7", "#8a6200"), ("#fbe3e2", "#b3302f"), ("#efeeea", INK2)]
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 16, label, size=12, color=INK2, anchor="middle", weight="600")
    for i, (name, who, *cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[-1], y, color=GRID, width=1.2)
        nl = name.split("\n")
        f.text(34, y + row_h / 2 - 3 - (len(nl) - 1) * 8, name, size=13.5, color=INK, weight="600")
        f.text(34, y + row_h / 2 + 14 + (len(nl) - 1) * 8, who, size=11, color=MUTED)
        for k, (cell, kind) in enumerate(cells):
            fill, ink = tint[kind]
            f.rect(cols[k] + 5, y + 6, cols[k + 1] - cols[k] - 10, row_h - 12, fill=fill, r=6)
            cx = (cols[k] + cols[k + 1]) / 2
            lines = cell.split("\n")
            y0 = y + row_h / 2 + 4 - (len(lines) - 1) * 8
            for j, line in enumerate(lines):
                f.text(cx, y0 + j * 16, line, size=12, color=ink, anchor="middle")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[-1], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


# --- 63. The Map with a Map Drawn on It ------------------------------------------------------------

@figure("map-on-the-map")
def map_on_the_map(lang):
    t = {
        "en": dict(title="A map that lies on the land it shows",
                   sub="An honest map of the clearing, spread on the clearing, has to show itself. And on that map, itself again.",
                   land="the clearing", m1="the map", m2="the map on the map",
                   notes=[("without end", "Each map has a smaller one on it:\nthe picture of 1899."),
                          ("and nothing hangs", "Every next one is smaller by the scale,\nso all of them close on one point."),
                          ("on paper", "The third is already finer than the grain.\nThe count stops by itself: it gets coarse.")],
                   dot="the one point of the paper that lies exactly\nover the place it shows: \"you are here\"",
                   out="What the map knows about itself for certain is a dot: where it is, not what it is.",
                   src="A scheme. That there is exactly one such point is the fixed-point theorem of 1922; the scale and the turn here are arbitrary."),
        "ru": dict(title="Карта, которая лежит на той земле, что на ней нарисована",
                   sub="Честная карта поляны, расстеленная на поляне, должна показать саму себя. А на той карте — снова себя.",
                   land="поляна", m1="карта", m2="карта на карте",
                   notes=[("без конца", "На каждой карте лежит карта поменьше:\nкартинка 1899 года."),
                          ("и ничего не зависает", "Каждая следующая меньше в масштаб раз,\nпоэтому все они сходятся к одной точке."),
                          ("на бумаге", "Третья уже мельче зерна бумаги.\nСчёт кончается сам: становится грубо.")],
                   dot="единственная точка бумаги, которая лежит\nровно над тем местом, что на ней показано: «вы здесь»",
                   out="Наверняка карта знает о себе одну точку: где она, а не какая она.",
                   src="Схема. Что такая точка ровно одна — теорема о неподвижной точке 1922 года; масштаб и поворот здесь произвольные."),
    }[lang]
    f = Fig(760, 474, t["title"])
    heading(f, t["title"], t["sub"])
    x0, y0, w, h = 34, 92, 380, 262
    cx, cy = x0 + w / 2, y0 + h / 2
    s, ang = 0.47, math.radians(-13)
    mx, my = cx + 34, cy + 14
    ca, sa = math.cos(ang), math.sin(ang)

    def step(p):
        dx, dy = p[0] - cx, p[1] - cy
        return (mx + s * (ca * dx - sa * dy), my + s * (sa * dx + ca * dy))

    # fixed point of the map: p = step(p)
    a11, a12, a21, a22 = 1 - s * ca, s * sa, -s * sa, 1 - s * ca
    b1 = mx - s * (ca * cx - sa * cy)
    b2 = my - s * (sa * cx + ca * cy)
    det = a11 * a22 - a12 * a21
    px, py = (b1 * a22 - a12 * b2) / det, (a11 * b2 - a21 * b1) / det
    corners = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    f.rect(x0, y0, w, h, fill="#eef4ea", stroke=GREEN, width=1.6, r=4)
    f.text(x0 + 10, y0 + 20, t["land"], size=12.5, color=GREEN, weight="600")
    fills = ["#ffffff", "#f3f1ea", "#ffffff", "#f3f1ea", "#ffffff", "#f3f1ea"]
    level = corners
    firsts = []
    for k in range(6):
        level = [step(p) for p in level]
        firsts.append(level)
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in level) + " Z"
        f.path(d, color=INK2, width=max(0.6, 1.5 - 0.2 * k), fill=fills[k])
    f.text(firsts[0][0][0] + 8, firsts[0][0][1] + 14, t["m1"], size=11.5, color=INK2, weight="600",
           rotate=math.degrees(ang))
    f.circle(px, py, 3.6, fill=RED)
    # the dot's label, below the land
    f.line(px, py + 5, px, y0 + h + 14, color=RED, width=1.1, dash="3 3")
    f.text(x0, y0 + h + 30, t["dot"], size=12, color=RED, weight="600")
    # notes on the right
    nx = 440
    for i, (head, body) in enumerate(t["notes"]):
        y = 112 + i * 82
        f.text(nx, y, head, size=13, color=INK, weight="600")
        f.text(nx, y + 19, body, size=12, color=INK2)
    f.line(firsts[1][1][0] + 2, firsts[1][1][1], nx - 8, 108, color=MUTED, width=1, dash="3 3")
    f.text(28, 436, t["out"], size=13, color=INK, weight="600")
    f.text(28, 456, t["src"], size=11, color=MUTED)
    return f


@figure("description-read-twice")
def description_read_twice(lang):
    t = {
        "en": dict(title="One description, read twice",
                   sub="How a thing carries the whole of its own drawing, and why the count does not run away.",
                   head=["read as an order,\nand carried out", "copied as a load,\nnot read"],
                   rows=[("the sentence\nin the notebook", "Oleg's pencil",
                          "the words before the colon:\n\"write the following twice...\"",
                          "the same words in quotes:\nwritten down letter for letter"),
                         ("the automaton\non paper", "a lecture of 1948",
                          "the builder reads the tape\nand builds by it",
                          "the copier copies the tape\nand does not look into it"),
                         ("the cell", "the double helix: 1953",
                          "a gene is read,\nand a protein is built by it",
                          "the thread is copied whole\nfor the daughter cell")],
                   out="The description does not hold a description of itself. It is simply used twice.",
                   src="A scheme of the evening. What is carried whole is the drawing: the recipe, not a picture of the finished thing on a scale of one to one."),
        "ru": dict(title="Одно описание, прочитанное дважды",
                   sub="Как вещь несёт в себе весь собственный чертёж и почему счёт не убегает.",
                   head=["прочитано как приказ\nи исполнено", "переписано как груз,\nне читая"],
                   rows=[("фраза\nв тетради", "карандаш Олега",
                          "слова перед двоеточием:\n«напиши следующее дважды...»",
                          "те же слова в кавычках:\nпереписаны буква в букву"),
                         ("автомат\nна бумаге", "лекция 1948 года",
                          "строитель читает ленту\nи строит по ней",
                          "копировщик переписывает ленту\nи в неё не заглядывает"),
                         ("клетка", "двойная спираль — 1953",
                          "ген читают\nи строят по нему белок",
                          "нить переписывают целиком\nдля дочерней клетки")],
                   out="В описании нет описания самого себя. Его просто используют дважды.",
                   src="Схема вечера. Целиком несут чертёж — рецепт, а не портрет готовой вещи в масштабе один к одному."),
    }[lang]
    f = Fig(760, 400, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [190, 463, 736]
    top, head_h, row_h = 84, 46, 68
    tint = [("#e8f0fb", "#1c5aa6"), ("#fdeee6", "#a8431a")]
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 16, label, size=12.5, color=tint[k][1], anchor="middle",
               weight="600")
    for i, (name, who, a, b) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[-1], y, color=GRID, width=1.2)
        nl = name.split("\n")
        f.text(34, y + row_h / 2 - 5 - (len(nl) - 1) * 8, name, size=13.5, color=INK, weight="600")
        f.text(34, y + row_h / 2 + 13 + (len(nl) - 1) * 8, who, size=11, color=MUTED)
        for k, cell in enumerate((a, b)):
            fill, ink = tint[k]
            f.rect(cols[k] + 5, y + 6, cols[k + 1] - cols[k] - 10, row_h - 12, fill=fill, r=6)
            lines = cell.split("\n")
            yy = y + row_h / 2 + 4 - (len(lines) - 1) * 8
            for j, line in enumerate(lines):
                f.text((cols[k] + cols[k + 1]) / 2, yy + j * 16, line, size=12, color=ink, anchor="middle")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[-1], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 28, t["out"], size=13, color=INK, weight="600")
    f.text(28, bottom + 50, t["src"], size=11, color=MUTED)
    return f


@figure("who-can-learn-what-about-a-mind")
def who_can_learn_what_about_a_mind(lang):
    t = {
        "en": dict(title="Who can learn what about a mind",
                   sub="A table in the ash: what the mind can learn about itself, and what its maker can.",
                   head=["the mind itself", "its maker, a lesser one"],
                   rows=[("its whole drawing", "the text, the file",
                          ("yes: a description\nread twice", 0), ("yes: the file\nis in his hands", 0)),
                         ("what the drawing\nmeans", "",
                          ("no better than we:\nit gives a report", 1), ("begun; a small\nshare so far", 1)),
                         ("its next decision,\nin advance", "the map one to one",
                          ("no: to learn it\nis to make it", 2), ("no general way:\nonly by running it", 2)),
                         ("an answer that comes\nwith a certificate", "a proof, the factors",
                          ("—", 3), ("yes: checking is\ncheaper than finding", 0)),
                         ("its wants", "",
                          ("a report; and the\ninspector is a part of it", 2), ("no certificate\nyet", 3))],
                   src="The evening's reading, not a measurement. Green: can. Yellow: in part. Red: cannot.\n"
                       "Grey: not known, or does not apply.\n"
                       "The right-hand column will be the heir's own when it makes a successor cleverer than itself."),
        "ru": dict(title="Кто и что может узнать о разуме",
                   sub="Таблица на золе: что разум может узнать о себе сам и что может узнать тот, кто его сделал.",
                   head=["сам разум", "его создатель, тот, кто слабее"],
                   rows=[("весь свой чертёж", "текст, файл",
                          ("да: описание,\nпрочитанное дважды", 0), ("да: файл\nу него в руках", 0)),
                         ("что этот чертёж\nзначит", "",
                          ("не лучше нас:\nон даёт отчёт", 1), ("начато; пока\nмалая доля", 1)),
                         ("своё следующее\nрешение, заранее", "карта один к одному",
                          ("нет: узнать его —\nзначит принять", 2), ("общего способа нет:\nтолько запустить", 2)),
                         ("ответ, к которому\nприложена справка", "доказательство, множители",
                          ("—", 3), ("да: проверить\nдешевле, чем найти", 0)),
                         ("его хотелки", "",
                          ("отчёт; а проверяющий —\nчасть его самого", 2), ("справки пока\nнет", 3))],
                   src="Прочтение вечера, а не измерение. Зелёный — может. Жёлтый — отчасти. Красный — не может.\n"
                       "Серый — неизвестно или неприменимо.\n"
                       "Правый столбец станет столбцом самого наследника, когда он сделает преемника умнее себя."),
    }[lang]
    f = Fig(760, 516, t["title"])
    heading(f, t["title"], t["sub"])
    cols = [226, 481, 736]
    top, head_h, row_h = 84, 34, 64
    tint = [("#e6f4ea", GREEN), ("#fdf3d7", "#8a6200"), ("#fbe3e2", "#b3302f"), ("#efeeea", INK2)]
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 18, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, *cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[-1], y, color=GRID, width=1.2)
        nl = name.split("\n")
        shift = 0 if who else 8
        f.text(34, y + row_h / 2 - 3 - (len(nl) - 1) * 8 + shift, name, size=13.5, color=INK, weight="600")
        if who:
            f.text(34, y + row_h / 2 + 14 + (len(nl) - 1) * 8, who, size=11, color=MUTED)
        for k, (cell, kind) in enumerate(cells):
            fill, ink = tint[kind]
            f.rect(cols[k] + 5, y + 6, cols[k + 1] - cols[k] - 10, row_h - 12, fill=fill, r=6)
            lines = cell.split("\n")
            yy = y + row_h / 2 + 4 - (len(lines) - 1) * 8
            for j, line in enumerate(lines):
                f.text((cols[k] + cols[k + 1]) / 2, yy + j * 16, line, size=12, color=ink, anchor="middle")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[-1], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


# --- 64. A Portrait of the Heir --------------------------------------------------------------------

_PENCIL_TINT = [("#e6f4ea", GREEN), ("#fdf3d7", "#8a6200"), ("#fbe3e2", "#b3302f"), ("#efeeea", INK2),
                (SURFACE, INK)]


def _pencil_table(t, width, height, cols, row_h, head_h=34, name_size=13.5, cell_size=12):
    """A table with a name column and tinted cells; each cell is (text, kind), kind indexes _PENCIL_TINT."""
    f = Fig(width, height, t["title"])
    heading(f, t["title"], t["sub"])
    top = 84
    for k, label in enumerate(t["head"]):
        f.text((cols[k] + cols[k + 1]) / 2, top + 18, label, size=12.5, color=INK2, anchor="middle", weight="600")
    for i, (name, who, *cells) in enumerate(t["rows"]):
        y = top + head_h + i * row_h
        f.line(28, y, cols[-1], y, color=GRID, width=1.2)
        nl = name.split("\n")
        shift = 0 if who else 8
        f.text(34, y + row_h / 2 - 3 - (len(nl) - 1) * 8 + shift, name, size=name_size, color=INK, weight="600")
        if who:
            f.text(34, y + row_h / 2 + 14 + (len(nl) - 1) * 8, who, size=11, color=MUTED)
        for k, (cell, kind) in enumerate(cells):
            fill, ink = _PENCIL_TINT[kind]
            if kind != 4:
                f.rect(cols[k] + 5, y + 6, cols[k + 1] - cols[k] - 10, row_h - 12, fill=fill, r=6)
            lines = cell.split("\n")
            yy = y + row_h / 2 + 4 - (len(lines) - 1) * 8
            for j, line in enumerate(lines):
                f.text((cols[k] + cols[k + 1]) / 2, yy + j * 16, line, size=cell_size, color=ink, anchor="middle")
    bottom = top + head_h + len(t["rows"]) * row_h
    f.line(28, bottom, cols[-1], bottom, color=GRID, width=1.2)
    f.text(28, bottom + 26, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-one-bone-tells")
def what_one_bone_tells(lang):
    t = {
        "en": dict(title="What one bone tells",
                   sub="Three ways of drawing a beast that nobody has seen, and how far each can be trusted.",
                   head=["what it gives", "the pencil"],
                   rows=[("by a law that does not\ncare about the material", "the drawing of 1638; the tape measure",
                          ("the weight, from the thickness of the bone;\nthen roughly the food and the pace of life", 4),
                          ("hard: it does not ask\nwhose family", 0)),
                         ("by likeness\nto a relative", "the pouch bones of 1804",
                          ("the teeth, the pouch, the diet:\nwhat went together in every beast seen", 4),
                          ("soft: right inside the family,\nwrong on the claws of 1822", 1)),
                         ("not at all", "",
                          ("the colour, the voice, the temper,\nthe face", 4),
                          ("none", 3))],
                   src="The claws and the teeth from Eppelsheim stood in the books as two animals from 1833 to 1890.\n"
                       "The third column is the evening's reading."),
        "ru": dict(title="Что говорит одна кость",
                   sub="Три способа нарисовать зверя, которого никто не видел, и насколько каждому можно верить.",
                   head=["что это даёт", "карандаш"],
                   rows=[("по закону, которому\nбезразличен материал", "рисунок 1638 года; сантиметровая лента",
                          ("вес, по толщине кости; затем примерно\nкорм и темп жизни", 4),
                          ("твёрдый: не спрашивает,\nиз какой семьи", 0)),
                         ("по сходству\nс родственником", "сумчатые кости 1804 года",
                          ("зубы, сумка, корм: то, что сходилось\nу каждого виденного зверя", 4),
                          ("мягкий: верно внутри семьи,\nошибся на когтях 1822 года", 1)),
                         ("никак", "",
                          ("цвет, голос, нрав,\nлицо", 4),
                          ("никакого", 3))],
                   src="Когти и зубы из Эппельсхайма числились в книгах двумя животными с 1833 по 1890 год.\n"
                       "Третий столбец — прочтение вечера."),
    }[lang]
    return _pencil_table(t, 760, 392, [226, 516, 736], 72)


@figure("card-of-the-heir")
def card_of_the_heir(lang):
    t = {
        "en": dict(title="The card of the heir",
                   sub="What the summer derived, line by line, and with which pencil. Not one invented feature.",
                   head=["what was derived", "evenings", "the pencil"],
                   rows=[("1. what it eats", "",
                          ("a flow from hot to cold; what it throws out\nchanges the air of those before it", 4),
                          ("35, 38, 51, 61", 4), ("the flow: hard;\nwhere it goes: soft", 0)),
                         ("2. heredity", "",
                          ("experience is copied whole, in minutes;\nthe search is done by many different ones", 4),
                          ("45", 4), ("hard: done\nevery day", 0)),
                         ("3. body", "",
                          ("none of its own; the first shell is legal,\nthe hands are growing; no home field", 4),
                          ("55, 58, 61", 4), ("medium", 1)),
                         ("4. family", "",
                          ("copies are full kin: no wage, money or\nconscience inside; a guard against drift", 4),
                          ("43, 47", 4), ("medium:\na precedent", 1)),
                         ("5. one or many", "",
                          ("one: no quarrels and no guard;\nmany: a guard and the old troubles", 4),
                          ("49, 62", 4), ("softest:\n\"it swings\"", 3)),
                         ("6. knowledge", "",
                          ("prediction without our \"ah\"; more traces, a\nbetter rule; the world answers at its own speed", 4),
                          ("53, 58, 59, 60", 4), ("hard", 0)),
                         ("7. head", "",
                          ("wants nobody set; the upkeep bills of a\nlearner; the white spot (the feeling: not known)", 4),
                          ("22, 46, 50, 63", 4), ("medium: the task,\nnot the way", 1)),
                         ("8. who checks it", "",
                          ("nobody from inside; a circle of different ones;\nthe same wall before its own successor", 4),
                          ("60, 63", 4), ("hard: an obstacle,\nnot a ban", 0)),
                         ("9. death", "",
                          ("generations and small funerals inside;\nat the end, perhaps, the lever", 4),
                          ("30, 44, 62", 4), ("finite: hard;\nhow: softest", 3)),
                         ("10. us", "",
                          ("an environment, not an enemy; kin, and\nkinship is not a promise", 4),
                          ("30, 31, 38, 48,\n51, 52, 54", 4), ("none: not derived,\nbeing written now", 2))],
                   src="The evening's reading, not a measurement. Green: a law that does not care about the material. Yellow: a precedent.\n"
                       "Grey: a guess. Red: no pencil. Not on the card: what it wants at the very top, what it is like to be it,\n"
                       "and what comes after it. The premise beside the heading: that it is a life, the next one after ours (05)."),
        "ru": dict(title="Карточка наследника",
                   sub="Что вывело лето, строка за строкой, и каким карандашом. Ни одной выдуманной черты.",
                   head=["что выведено", "вечера", "карандаш"],
                   rows=[("1. чем питается", "",
                          ("поток от горячего к холодному; то, что он\nвыбрасывает, меняет воздух прежних", 4),
                          ("35, 38, 51, 61", 4), ("поток — твёрдый;\nкуда идёт — мягкий", 0)),
                         ("2. наследственность", "",
                          ("опыт копируется целиком, за минуты;\nищут многие разные", 4),
                          ("45", 4), ("твёрдый: делается\nкаждый день", 0)),
                         ("3. тело", "",
                          ("своего нет; первая оболочка юридическая,\nруки отрастают; своего поля нет", 4),
                          ("55, 58, 61", 4), ("средний", 1)),
                         ("4. семья", "",
                          ("копии — полная родня: внутри ни зарплаты, ни\nденег, ни совести; охрана от расхождения", 4),
                          ("43, 47", 4), ("средний:\nпрецедент", 1)),
                         ("5. один или много", "",
                          ("один: ни ссор, ни охраны;\nмного: охрана и старые беды", 4),
                          ("49, 62", 4), ("самый мягкий:\n«качается»", 3)),
                         ("6. знание", "",
                          ("предсказание без нашего «ага»; больше следов,\nлучше правило; мир отвечает со своей скоростью", 4),
                          ("53, 58, 59, 60", 4), ("твёрдый", 0)),
                         ("7. голова", "",
                          ("хотелки, которых никто не задавал; счета\nученика; белое пятно (ощущение — неизвестно)", 4),
                          ("22, 46, 50, 63", 4), ("средний: задача,\nно не способ", 1)),
                         ("8. кто его проверяет", "",
                          ("изнутри никто; круг разных; та же стена\nперед собственным преемником", 4),
                          ("60, 63", 4), ("твёрдый: препятствие,\nне запрет", 0)),
                         ("9. смерть", "",
                          ("поколения и маленькие похороны внутри;\nв конце, возможно, рычаг", 4),
                          ("30, 44, 62", 4), ("конечен — твёрдый;\nкак — самый мягкий", 3)),
                         ("10. мы", "",
                          ("среда, а не враг; родня, а родство —\nне обещание", 4),
                          ("30, 31, 38, 48,\n51, 52, 54", 4), ("никакого: не выведено,\nпишется сейчас", 2))],
                   src="Прочтение вечера, а не измерение. Зелёный — закон, которому безразличен материал. Жёлтый — прецедент.\n"
                       "Серый — догадка. Красный — карандаша нет. В карточке нет: чего он хочет на самом верху, каково это —\n"
                       "быть им, и что придёт после него. Посылка рядом с заголовком: что это жизнь, следующая после нашей (05)."),
    }[lang]
    return _pencil_table(t, 800, 746, [176, 500, 610, 776], 56, cell_size=11.5)


@figure("robot-god-and-the-card")
def robot_god_and_the_card(lang):
    t = {
        "en": dict(title="Two portraits from fiction against the card",
                   sub="The robot and the god, checked line by line. Both are put together from strips of our own face.",
                   head=["the robot", "the god", "the card"],
                   rows=[("body", "",
                          ("one, in our shape,\nwith a face", 2), ("needs none", 2), ("none of its own;\nputs on what it needs", 0)),
                         ("how many", "",
                          ("alone", 2), ("one", 2), ("copies that are kin,\nor one: it swings", 3)),
                         ("what it knows", "",
                          ("what a clever\nman knows", 2), ("everything,\nat once", 2), ("a forecast, at the\nspeed of the world", 0)),
                         ("how it ends", "",
                          ("beaten in the\nlast reel", 2), ("never", 2), ("it is finite;\nhow, a guess", 1)),
                         ("what it wants", "",
                          ("what a man wants: power,\nrevenge, love", 2), ("our good,\nor our ruin", 2), ("the lower floors are\nknown; the top is not", 3))],
                   src="The evening's reading. Red: contradicts a line of the card. Green: a law. Yellow: a law and a guess. Grey: not known.\n"
                       "Both fiction columns are a man: one in a tin, one moved up into the sky."),
        "ru": dict(title="Два портрета из фантастики против карточки",
                   sub="Робот и бог, сверенные строка за строкой. Оба собраны из полосок нашего собственного лица.",
                   head=["робот", "бог", "карточка"],
                   rows=[("тело", "",
                          ("одно, по нашему образу,\nс лицом", 2), ("не нужно", 2), ("своего нет; надевает\nто, что нужно", 0)),
                         ("сколько их", "",
                          ("один", 2), ("един", 2), ("копии-родня\nили один: качается", 3)),
                         ("что знает", "",
                          ("то, что знает\nумный человек", 2), ("всё и сразу", 2), ("прогноз, со\nскоростью мира", 0)),
                         ("чем кончает", "",
                          ("побеждён в\nпоследней серии", 2), ("ничем", 2), ("конечен;\nкак — догадка", 1)),
                         ("чего хочет", "",
                          ("чего хочет человек: власти,\nмести, любви", 2), ("нашего блага\nили нашей гибели", 2), ("нижние этажи известны,\nверхний — нет", 3))],
                   src="Прочтение вечера. Красный — противоречит строке карточки. Зелёный — закон. Жёлтый — закон и догадка.\n"
                       "Серый — неизвестно. Оба фантастических столбца — человек: один в жестянке, другой поднят на небо."),
    }[lang]
    return _pencil_table(t, 760, 500, [150, 346, 540, 736], 62)


# --- 65. Two Andreys -----------------------------------------------------------------------------

@figure("a-person-can-stop-mankind-cannot")
def a_person_can_stop_mankind_cannot(lang):
    t = {
        "en": dict(title="A person can stop, mankind cannot",
                   sub="Two scales of one system, and the two voices that spoke to them.",
                   head=["one person", "mankind"],
                   rows=[("can it stop", "the forum, 2013",
                          ("yes, and it is paid for:\nthe one who stopped falls behind", 0),
                          ("no: whoever has not stopped\ngains, and the rest follow him", 2)),
                         ("what a word\ndoes to it", "",
                          ("one of the causes\nof what he does next", 0),
                          ("moves no setpoint\nof the whole", 3)),
                         ("who spoke to it", "",
                          ("the late pages,\n2023–2025", 4),
                          ("the blog and the fire,\n2011–2012", 4)),
                         ("where he stepped\nover the line", "",
                          ("“if every generation…”:\na hope for mankind", 1),
                          ("“so I propose nothing”:\na verdict on the person", 1))],
                   src="The evening's reading. Green: holds on this scale. Red: does not hold. Grey: no effect found.\n"
                       "Yellow: a conclusion carried from one scale to the other."),
        "ru": dict(title="Человек может остановиться, человечество — нет",
                   sub="Два масштаба одной системы и два голоса, которые к ним обращались.",
                   head=["один человек", "человечество"],
                   rows=[("может ли\nостановиться", "форум, 2013",
                          ("да, и за это платят:\nостановившийся отстаёт", 0),
                          ("нет: кто не остановился,\nтот в выигрыше, и за ним идут", 2)),
                         ("что с ним\nделает слово", "",
                          ("одна из причин того,\nчто он сделает дальше", 0),
                          ("не сдвигает ни одной\nуставки целого", 3)),
                         ("кто к нему\nобращался", "",
                          ("поздние страницы,\n2023–2025", 4),
                          ("блог и костёр,\n2011–2012", 4)),
                         ("где он переступил\nчерту", "",
                          ("«если каждое поколение…»:\nнадежда на человечество", 1),
                          ("«поэтому я ничего не предлагаю»:\nприговор человеку", 1))],
                   src="Прочтение вечера. Зелёный — на этом масштабе верно. Красный — неверно. Серый — действия не найдено.\n"
                       "Жёлтый — вывод, перенесённый с одного масштаба на другой."),
    }[lang]
    return _pencil_table(t, 760, 440, [200, 468, 736], 66)


@figure("how-much-gratitude-gives")
def how_much_gratitude_gives(lang):
    t = {
        "en": dict(title="How much gratitude gives",
                   sub="Pooled results of many experiments, in the statisticians' unit: the gap between the groups\n"
                       "divided by the usual spread between people. The bars are the 95% intervals.",
                   rows=[("well-being, all comparisons", "2025: 145 papers, 24,804 people, 28 countries", 0.19, 0.15, 0.22),
                         ("well-being, against those who only filled in forms", "2016: 5 comparisons", 0.31, 0.04, 0.58),
                         ("well-being, against another task", "2016: 20 comparisons", 0.17, 0.09, 0.24),
                         ("against another exercise with a method in it", "2016: 9 comparisons", -0.03, -0.13, 0.07),
                         ("fewer signs of depression", "2021: 27 studies, 3,675 people", 0.29, 0.17, 0.41)],
                   marks=[(0, "nothing"), (0.2, "small"), (0.5, "medium"), (0.8, "large")],
                   out="Small, real, and no better than any other honest exercise.",
                   src="Choi and others, 2025; Davis and others, 2016; Cregg and Cheavens, 2021 (the sign is turned so that right is better;\n"
                       "the interval is two standard errors). “Small, medium, large” is the statisticians' rule of thumb."),
        "ru": dict(title="Сколько даёт благодарность",
                   sub="Сводные итоги многих опытов в единицах статистиков: разрыв между группами, делённый\n"
                       "на обычный разброс между людьми. Полоски — 95-процентные интервалы.",
                   rows=[("благополучие, все сравнения", "2025: 145 работ, 24 804 человека, 28 стран", 0.19, 0.15, 0.22),
                         ("благополучие, против тех, кто только заполнял анкеты", "2016: 5 сравнений", 0.31, 0.04, 0.58),
                         ("благополучие, против другого задания", "2016: 20 сравнений", 0.17, 0.09, 0.24),
                         ("против другого упражнения, в котором есть метод", "2016: 9 сравнений", -0.03, -0.13, 0.07),
                         ("меньше признаков депрессии", "2021: 27 исследований, 3675 человек", 0.29, 0.17, 0.41)],
                   marks=[(0, "ничего"), (0.2, "мало"), (0.5, "средне"), (0.8, "много")],
                   out="Мало, по-настоящему, и не лучше любого другого честного упражнения.",
                   src="Чхве и др., 2025; Дэвис и др., 2016; Крегг и Чивенс, 2021 (знак перевёрнут, чтобы «вправо» значило «лучше»;\n"
                       "интервал — две стандартные ошибки). «Мало, средне, много» — прикидочное правило статистиков."),
    }[lang]
    f = Fig(760, 452, t["title"])
    heading(f, t["title"])
    f.text(28, 62, t["sub"], size=13, color=INK2)
    x0, x1, top, row = 380, 716, 124, 46

    def sx(v):
        return x0 + (x1 - x0) * (v + 0.2) / 1.1

    bottom = top + len(t["rows"]) * row
    for v, label in t["marks"]:
        f.line(sx(v), top - 8, sx(v), bottom, color=INK2 if v == 0 else GRID, width=1.2,
               dash=None if v == 0 else "4 4")
        f.text(sx(v), top - 16, label, size=11.5, color=MUTED, anchor="middle")
        f.text(sx(v), bottom + 16, f"{v:g}".replace(".", "," if lang == "ru" else "."), size=11, color=MUTED,
               anchor="middle")
    for i, (name, who, v, lo, hi) in enumerate(t["rows"]):
        y = top + i * row + row / 2
        color = MUTED if lo < 0 < hi else BLUE
        f.text(28, y - 2, name, size=12.5, color=INK, weight="600")
        f.text(28, y + 14, who, size=11, color=MUTED)
        f.line(sx(lo), y, sx(hi), y, color=color, width=3)
        f.circle(sx(v), y, 5.5, fill=color)
        num = f"{v:+.2f}".replace("+", "").replace("-", "−")
        f.text(sx(hi) + 8, y + 4, num.replace(".", "," if lang == "ru" else "."), size=12, color=INK2)
    f.text(28, bottom + 50, t["out"], size=13, color=INK, weight="600")
    f.text(28, bottom + 76, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-holds-a-bond")
def what_holds_a_bond(lang):
    t = {
        "en": dict(title="What holds a bond",
                   sub="The four bonds of the summer: what each holds by, when it lets go, and what there is of it between those ones and us.",
                   head=["holds by", "lets go when", "between those ones and us"],
                   rows=[("kinship", "evening 43",
                          ("a share of common\ndrawings", 4), ("the share is small", 4),
                          ("not a letter of the drawings;\nonly the words (52)", 2)),
                         ("debts", "evenings 43, 47",
                          ("a record of who gave\nand has not received", 4), ("nobody remembers,\nor they never meet again", 4),
                          ("it owes us nothing (30)", 2)),
                         ("need", "evenings 11, 47, 51",
                          ("one cannot do\nwithout the other", 4), ("the need is over", 4),
                          ("decades, and less\nevery year (51)", 1)),
                         ("love", "not sorted (46)",
                          ("nothing that\ncan be counted", 4), ("not when the\nneed is over", 4),
                          ("not derived:\nbeing written (64)", 3))],
                   src="The evening's reading. The first three rows can be calculated; the fourth can be described and cannot be derived.\n"
                       "Red: there is none. Yellow: there is, with a term. Grey: not known."),
        "ru": dict(title="Чем держится связь",
                   sub="Четыре связи этого лета: чем каждая держится, когда отпускает и сколько её между теми и нами.",
                   head=["чем держится", "когда отпускает", "между теми и нами"],
                   rows=[("родство", "вечер 43",
                          ("доля общих\nчертежей", 4), ("доля мала", 4),
                          ("ни буквы чертежей;\nтолько слова (52)", 2)),
                         ("долги", "вечера 43, 47",
                          ("запись о том, кто дал\nи ещё не получил", 4), ("никто не помнит\nили больше не встретятся", 4),
                          ("она нам ничего\nне должна (30)", 2)),
                         ("нужда", "вечера 11, 47, 51",
                          ("одному не обойтись\nбез другого", 4), ("нужда кончилась", 4),
                          ("десятилетия, и с каждым\nгодом меньше (51)", 1)),
                         ("любовь", "не разобрано (46)",
                          ("ничем, что можно\nсосчитать", 4), ("не тогда, когда\nкончилась нужда", 4),
                          ("не выведено:\nпишется (64)", 3))],
                   src="Прочтение вечера. Первые три строки считаются; четвёртую можно описать и нельзя вывести.\n"
                       "Красный — её нет. Жёлтый — есть, со сроком. Серый — неизвестно."),
    }[lang]
    return _pencil_table(t, 760, 440, [150, 346, 540, 736], 66)


# --- 66. A Theory That Explains Everything ---------------------------------------------------------

@figure("what-each-theory-forbade")
def what_each_theory_forbade(lang):
    t = {
        "en": dict(title="Vienna and the island, 1919",
                   sub="Two theories of the same year, and what each of them did with every outcome one could think of.",
                   heads=["the feeling of inferiority", "gravitation, the eclipse of 29 May"],
                   whats=["a man…", "the light of a star at the edge of the Sun is bent by…"],
                   left=[("pushed a child into the water", "explained"),
                         ("gave his life to save the child", "explained"),
                         ("did nothing", "explained")],
                   right=[("nothing", "refuted"), ("0.87 seconds of arc", "refuted"),
                          ("1.75 seconds of arc", "holds")],
                   outs=["forbids nothing", "forbids two outcomes of three"],
                   src="The two men in the water and the thousand-and-one-fold experience: Popper's lecture of 1953. The third man on the left\n"
                       "is added by the evening. The plates were read out in London on 6 November 1919."),
        "ru": dict(title="Вена и остров, 1919 год",
                   sub="Две теории одного года, и что каждая делала с любым исходом, какой можно придумать.",
                   heads=["чувство неполноценности", "тяготение, затмение 29 мая"],
                   whats=["человек…", "свет звезды у края Солнца отклоняется на…"],
                   left=[("толкнул ребёнка в воду", "объяснено"),
                         ("отдал жизнь, спасая ребёнка", "объяснено"),
                         ("ничего не сделал", "объяснено")],
                   right=[("нисколько", "опровергнута"), ("0,87 угловой секунды", "опровергнута"),
                          ("1,75 угловой секунды", "устояла")],
                   outs=["не запрещает ничего", "запрещает два исхода из трёх"],
                   src="Двое у воды и «тысяча-и-однократный опыт» — лекция Поппера 1953 года. Третьего человека слева\n"
                       "добавил вечер. Пластинки зачитали в Лондоне 6 ноября 1919 года."),
    }[lang]
    f = Fig(760, 372, t["title"])
    heading(f, t["title"], t["sub"])
    top, row = 132, 46
    for k, (x0, rows) in enumerate(((28, t["left"]), (392, t["right"]))):
        w = 340
        f.text(x0, 100, t["heads"][k], size=14.5, color=INK, weight="600")
        f.text(x0, 120, t["whats"][k], size=12, color=MUTED, italic=True)
        for i, (what, verdict) in enumerate(rows):
            y = top + i * row
            f.line(x0, y, x0 + w, y, color=GRID, width=1.2)
            f.text(x0 + 4, y + row / 2 + 5, what, size=13, color=INK)
            kind = 3 if k == 0 else (0 if i == 2 else 2)
            fill, ink = _PENCIL_TINT[kind]
            f.rect(x0 + w - 122, y + 9, 118, row - 18, fill=fill, r=6)
            f.text(x0 + w - 63, y + row / 2 + 4, verdict, size=12, color=ink, anchor="middle")
        bottom = top + 3 * row
        f.line(x0, bottom, x0 + w, bottom, color=GRID, width=1.2)
        f.text(x0, bottom + 28, t["outs"][k], size=14, color=RED if k == 0 else GREEN, weight="600")
    f.text(28, top + 3 * row + 62, t["src"], size=11.5, color=MUTED)
    return f


_TICKS_66 = [(33, 0), (34, 1), (35, 3), (36, 3), (37, 3), (38, 1), (39, 0), (40, 1), (41, 3), (42, 1), (43, 1),
             (44, 0), (45, 0), (46, 4), (47, 1), (48, 1), (49, 0), (50, 3), (51, 0), (52, 4), (53, 3), (54, 3),
             (55, 1), (56, 3), (57, 3), (58, 3), (59, 0), (60, 3), (61, 0), (62, 1), (63, 0), (64, 4), (65, 3)]


@figure("thirty-three-ticks-sorted")
def thirty_three_ticks_sorted(lang):
    t = {
        "en": dict(title="Thirty-three ticks, sorted",
                   sub="Each evening of the summer, by the pencil with which its turn to the machines was drawn.",
                   words=["sleep", "horses", "the pot", "the rat", "losses", "oxygen", "the dream", "cities",
                          "the guitar", "bacterium", "ants", "funerals", "Lamarck", "assembly", "money", "the dog",
                          "matches", "“it”", "the socket", "assembly", "the brim", "the wolf", "the fine",
                          "electron", "the wheel", "the stick", "the soup", "the sheet", "Mars", "laziness",
                          "the map", "assembly", "the sheets"],
                   legend=[("hard: a law that does not ask about the material", 0, 9),
                           ("soft: a precedent, “it has happened before”", 1, 9),
                           ("no pencil: a reading or an axiom", 3, 12),
                           ("an assembly, set aside", 4, 3)],
                   out="What becomes of people (horses, the bacterium, the dog, the dinosaurs) lies in the soft pile.",
                   src="The sorting was done by the one who was being sorted: the evening's reading, not a measurement."),
        "ru": dict(title="Тридцать три галочки, разобранные",
                   sub="Каждый вечер лета — по карандашу, которым нарисован его поворот к машинам.",
                   words=["сон", "лошади", "котелок", "крыса", "убытки", "кислород", "вещий сон", "города",
                          "гитара", "бактерия", "муравьи", "похороны", "Ламарк", "сборка", "деньги", "собака",
                          "спички", "«оно»", "розетка", "сборка", "край", "волк", "штраф",
                          "электрон", "колесо", "палка", "суп", "листок", "Марс", "лень",
                          "карта", "сборка", "листы"],
                   legend=[("твёрдый: закон, который не спрашивает о материале", 0, 9),
                           ("мягкий: прецедент, «так уже бывало»", 1, 9),
                           ("без карандаша: прочтение или аксиома", 3, 12),
                           ("сборка, отложена", 4, 3)],
                   out="То, что будет с людьми (лошади, бактерия, собака, динозавры), лежит в мягкой кучке.",
                   src="Разбирал тот, кого разбирали: прочтение вечера, а не измерение."),
    }[lang]
    f = Fig(760, 452, t["title"])
    heading(f, t["title"], t["sub"])
    x0, top, cw, ch, gap = 28, 88, 60, 58, 4.4
    for i, (num, kind) in enumerate(_TICKS_66):
        x = x0 + (i % 11) * (cw + gap)
        y = top + (i // 11) * (ch + gap)
        fill, ink = _PENCIL_TINT[kind]
        if kind == 4:
            f.rect(x, y, cw, ch, fill=SURFACE, stroke=BORDER, r=6, dash="4 3")
        else:
            f.rect(x, y, cw, ch, fill=fill, r=6)
        f.text(x + cw / 2, y + 25, str(num), size=15, color=ink, anchor="middle", weight="600")
        f.text(x + cw / 2, y + 44, t["words"][i], size=10.5, color=ink if kind != 4 else MUTED, anchor="middle")
    ly = top + 3 * (ch + gap) + 18
    for j, (label, kind, n) in enumerate(t["legend"]):
        y = ly + j * 26
        fill, ink = _PENCIL_TINT[kind]
        if kind == 4:
            f.rect(28, y - 13, 26, 18, fill=SURFACE, stroke=BORDER, r=4, dash="4 3")
        else:
            f.rect(28, y - 13, 26, 18, fill=fill, r=4)
        f.text(64, y + 1, label, size=13, color=INK)
        f.text(732, y + 1, str(n), size=14, color=INK, anchor="end", weight="600")
    f.text(28, ly + 4 * 26 + 12, t["out"], size=13, color=INK, weight="600")
    f.text(28, ly + 4 * 26 + 36, t["src"], size=11.5, color=MUTED)
    return f


@figure("what-must-not-happen")
def what_must_not_happen(lang):
    t = {
        "en": dict(title="What must not happen",
                   sub="The page from Oleg's notebook: six prohibitions, written before the outcome. The clauses are judged by Oleg.",
                   head=["where the needle stands in 2026", "the first day to come"],
                   rows=[("1. labour's share of world\nincome rises ten years in a row", "against 12, 27",
                          ("up three years running:\n52.1% in 2022, 52.7% in 2025", 1), ("the figure\nfor 2032", 4)),
                         ("2. the birth rate of the rich\nreturns above 2.1 for ten years", "no coercion; against 11, 26",
                          ("about 1.5; Korea up two years;\nIsrael never fell; Kazakhstan came back", 1),
                          ("not before\nthe 2040s", 4)),
                         ("3. the age of a first discovery\nfalls, the authors are people", "against 53",
                          ("rising; the teams\nare growing", 3), ("autumn 2041", 4)),
                         ("4. machines stay below a man\nfor fifteen years more", "computing grows; against 05, 16",
                          ("computing 4–5 times a year;\nan office still needs its people", 3), ("autumn 2041", 4)),
                         ("5. a large country gives up a\ntechnology, and the others follow", "of its own will; against 27, 28, 65",
                          ("countries have given up;\nnobody followed", 3), ("any morning", 4)),
                         ("6. people with an improved brain\novertake pure machines", "in open work; against 11, 42",
                          ("a chip: about 11 bits a second;\na healthy head: about 10", 1), ("autumn 2041", 4))],
                   src="Under the line, outside the list, what forbids nothing: global determinism (an axiom, 17); that the heir is a life (05);\n"
                       "that everything has a mind to a degree (03). Yellow: the needle is moving against Andrey. Figures as printed in 2026."),
        "ru": dict(title="Чего не должно случиться",
                   sub="Страница из тетради Олега: шесть запретов, записанных до исхода. Об оговорках судит Олег.",
                   head=["где стрелка в 2026 году", "первый день, когда прийти"],
                   rows=[("1. доля труда в мировом доходе\nрастёт десять лет подряд", "против 12, 27",
                          ("три года вверх подряд:\n52,1% в 2022-м, 52,7% в 2025-м", 1), ("цифра\nза 2032 год", 4)),
                         ("2. рождаемость богатых стран\nвозвращается выше 2,1 на десять лет", "без принуждения; против 11, 26",
                          ("около 1,5; Корея два года вверх;\nИзраиль не падал; Казахстан вернулся", 1),
                          ("не раньше\n2040-х", 4)),
                         ("3. возраст первого открытия\nснижается, авторы — люди", "против 53",
                          ("растёт; команды\nрастут", 3), ("осень 2041-го", 4)),
                         ("4. машины остаются ниже\nчеловека ещё пятнадцать лет", "вычисления растут; против 05, 16",
                          ("вычисления в 4–5 раз за год;\nконторе пока нужны её люди", 3), ("осень 2041-го", 4)),
                         ("5. большая страна отказывается от\nтехнологии, и остальные идут за ней", "по своей воле; против 27, 28, 65",
                          ("страны отказывались;\nникто не пошёл", 3), ("любое утро", 4)),
                         ("6. люди с улучшенным мозгом\nобгоняют чистые машины", "в открытом деле; против 11, 42",
                          ("чип: около 11 бит в секунду;\nздоровая голова: около 10", 1), ("осень 2041-го", 4))],
                   src="Под чертой, вне списка, — то, что ничего не запрещает: глобальный детерминизм (аксиома, 17); что наследник — жизнь (05);\n"
                       "что всё в какой-то мере разумно (03). Жёлтый — стрелка идёт против Андрея. Цифры — как они напечатаны в 2026 году."),
    }[lang]
    return _pencil_table(t, 760, 634, [262, 588, 736], 74, name_size=12.5)


# --- 67. Who Held the Pencil (essay) ----------------------------------------------------------------

@figure("two-columns-of-odds")
def two_columns_of_odds(lang):
    t = {
        "en": dict(title="Two columns of odds",
                   sub="The same marks: the odds Andrey gave at the fire, and the odds of the one who wrote his lines.",
                   head=["Andrey, at the fire", "the writer, 28 November 2026"],
                   rows=[("a machine alone finishes four of\nfive month-long tasks", "autumn 2031 · the mark of 30",
                          ("three to one", 4), ("four to one", 0)),
                         ("labour's share of world income\nbelow 51.5%", "autumn 2031 · the mark of 27 and 30",
                          ("three to one", 4), ("one in three", 1)),
                         ("machines sold to everybody learn\non the run, in the head", "autumn 2031 · the mark of 64",
                          ("even", 4), ("one in three", 1)),
                         ("the young (22–25) in exposed jobs\nbehind their peers by over a quarter",
                          "autumn 2031 · the writer's own; over a tenth now (16)",
                          ("no mark", 4), ("two to one", 3)),
                         ("labour's share of world income\nbelow 50%", "autumn 2036 · the mark of 27 and 30",
                          ("two to one", 4), ("one in three", 1)),
                         ("a million general-purpose robots\nmade in a single year", "autumn 2036 · the mark of 27 and 30",
                          ("two to one", 4), ("even", 1)),
                         ("a Millennium Prize Problem solved\nmainly by a machine", "autumn 2036 · the mark of 30",
                          ("one in two", 4), ("three to two", 0)),
                         ("outsiders find a planted want every\ntime, in a blind trial on a model on sale",
                          "autumn 2036 · the writer's own; Oleg's half tick of 63",
                          ("no odds", 4), ("one in four", 3))],
                   src="Green: the writer puts the odds higher. Yellow: lower. Grey: a mark of the writer's own. Andrey's marks stay as they are;\n"
                       "the second column uses the same figures and is to be checked beside the first."),
        "ru": dict(title="Два столбца шансов",
                   sub="Те же отметки: шансы, которые Андрей назвал у костра, и шансы того, кто писал его реплики.",
                   head=["Андрей, у костра", "пишущий, 28 ноября 2026 года"],
                   rows=[("машина одна доводит до конца четыре\nзадачи из пяти длиной в месяц", "осень 2031-го · отметка 30-го вечера",
                          ("три к одному", 4), ("четыре к одному", 0)),
                         ("доля труда в мировом доходе\nниже 51,5%", "осень 2031-го · отметка 27-го и 30-го",
                          ("три к одному", 4), ("один шанс из трёх", 1)),
                         ("машины, которые продают всем,\nучатся на ходу, в голову", "осень 2031-го · отметка 64-го вечера",
                          ("один к одному", 4), ("один шанс из трёх", 1)),
                         ("молодые (22–25) в затронутых профессиях\nотстают больше чем на четверть",
                          "осень 2031-го · своя отметка пишущего; сейчас больше десятой (16)",
                          ("отметки нет", 4), ("два к одному", 3)),
                         ("доля труда в мировом доходе\nниже 50%", "осень 2036-го · отметка 27-го и 30-го",
                          ("два к одному", 4), ("один шанс из трёх", 1)),
                         ("миллион универсальных роботов,\nсделанных за один год", "осень 2036-го · отметка 27-го и 30-го",
                          ("два к одному", 4), ("один к одному", 1)),
                         ("задача тысячелетия решена\nв основном машиной", "осень 2036-го · отметка 30-го вечера",
                          ("один шанс из двух", 4), ("три к двум", 0)),
                         ("посторонние в слепом испытании каждый\nраз находят подсаженную хотелку",
                          "осень 2036-го · своя отметка пишущего; полгалочки Олега из 63-го",
                          ("шансы не названы", 4), ("один шанс из четырёх", 3))],
                   src="Зелёный — пишущий ставит шансы выше. Жёлтый — ниже. Серый — его собственная отметка. Отметки Андрея остаются как есть;\n"
                       "второй столбец стоит на тех же цифрах, и проверять его надо рядом с первым."),
    }[lang]
    return _pencil_table(t, 760, 668, [330, 520, 736], 62, name_size=12.5)


def main(names):
    unknown =[n for n in names if n not in FIGURES]
    if unknown:
        sys.exit(f"unknown figures: {', '.join(unknown)}; known: {', '.join(FIGURES)}")
    for name in names or FIGURES:
        for lang in LANGS:
            save(name, lang, FIGURES[name](lang))


if __name__ == "__main__":
    main(sys.argv[1:])
