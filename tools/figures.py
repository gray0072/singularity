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


def main(names):
    unknown =[n for n in names if n not in FIGURES]
    if unknown:
        sys.exit(f"unknown figures: {', '.join(unknown)}; known: {', '.join(FIGURES)}")
    for name in names or FIGURES:
        for lang in LANGS:
            save(name, lang, FIGURES[name](lang))


if __name__ == "__main__":
    main(sys.argv[1:])
