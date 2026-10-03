# Images

Shared image folder for all languages. Rules: [SPEC.md §7](../SPEC.md#7-images).
Reference images from articles as `../images/<file>`.

## Registry

| File | Shows | Used in | Source | Author | License |
|------|-------|---------|--------|--------|---------|
| `venus-flytrap-closing.gif` | Venus flytrap closing its trap (animation) | 03 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Dionaea_muscipula_closing_trap_animation.gif) | Mnolf | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0) |
| `world-population-growth.ru.png` | World population growth, UN data (Russian labels) | 10 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:World_population_(UN)_ru.svg) | Zhwachwa (derivative work) | [CC BY 3.0](https://creativecommons.org/licenses/by/3.0) |
| `dynamic-system-life-cycle.png` | Life cycle of a dynamic system (Russian labels) | 10, 13 | sql.ru attachment 11582885, via the Wayback Machine | Андрей Гордиенко | used with the author's permission |
| `singularity-vertical-asymptote.png` | Blow-up curve approaching a vertical asymptote | 13 | sql.ru attachment 11716462, via the Wayback Machine | Андрей Гордиенко | used with the author's permission |
| `skill-age-layers.svg` (+ `.ru.svg`) | How long nature polished each skill (Moravec's paradox), log scale | 16 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `growth-over-ten-years.svg` (+ `.ru.svg`) | Growth over a decade: AI training compute, Moore's law, human intelligence | 16 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `vase-and-slices.svg` (+ `.ru.svg`) | The vase and the flat creature: the block universe seen slice by slice | 17 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `forecast-reliability.svg` (+ `.ru.svg`) | What a local forecaster can foretell: trend, date, details | 17 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `wants-control-loop.svg` (+ `.ru.svg`) | A want as a control loop: setpoint, comparator, mind, motors, sensors | 18 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `near-want-wins.svg` (+ `.ru.svg`) | Hyperbolic discounting: the preference between one apple and two flips | 18 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `forgetting-curve.svg` (+ `.ru.svg`) | Ebbinghaus's forgetting curve, his 1885 data | 19 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `image-platforms.svg` (+ `.ru.svg`) | Images moving from heads to writing, print, the internet and neural networks | 19 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |
| `self-model-ladder.svg` (+ `.ru.svg`) | Ladders of self-models: the mirror test and machines | 20 | drawn by [`tools/figures.py`](../tools/figures.py) | this repository | own work of the repository |

## To do

Planned names for the remaining images of the original articles. One file per picture, even when several
articles use it.

| Planned file | Used in | Original | Status / what to do |
|--------------|---------|----------|---------------------|
| `brain-simulation-forecast.svg` | 05 | 3dnews.ru chart `3dnews.ru/_imgdata/img/2009/11/22/150643.gif` (D. Modha / IBM): Top500 supercomputer performance against the scale of brain simulations, extrapolated to a human-scale brain around 2019 | Third-party: redraw from the published data as our own SVG (+ `.ru` variant) |
| `world-population-growth.png` | 10 (en) | [World_population_(UN).svg](https://commons.wikimedia.org/wiki/File:World_population_(UN).svg) | English variant of the stored chart |
| `uneven-knowledge-causal-links.png` | 08 | sql.ru attachment `actualfile.aspx?id=11520389` | Not in the Wayback Machine; redraw from the article text |
| `kimberlite-pipe-diamond-mine.jpg` | 09 | coolplaces.ru Google Earth picture | Third-party: replace with a free photo (Wikimedia) |
| `humanity-technosphere-evolution-curves.png` | 10 | the author's chart, `actualfile.aspx?id=11584337` | Not archived; redraw from the article text |
| `humanity-technosphere-attraction-forces.png` | 11 | the author's chart, `actualfile.aspx?id=11587264` | Not archived; redraw from the article text |

Redrawn charts are SVG (`.svg`, plus `.ru.svg` when they carry text); the planned extensions above become
`.svg` when redrawn.
