# Singularity — Repository Specification

## 1. Purpose

A multilingual collection of popular-science articles about the technological (evolutionary) singularity,
written as the dialogue series **"Campfire Dialogues"** (*«Диалог у костра»*).

- The series was started in 2011–2012 on the sql.ru blog *«Технологическая сингулярность»* by
  **Андрей Гордиенко** (Andrey Gordienko, nickname **Garya**): 15 numbered articles and 2 unnumbered posts.
  The blog survives only in the Wayback Machine:
  <https://web.archive.org/web/20181022050755/http://www.sql.ru/blogs/garya/>.
  The author today: [proza.ru/avtor/garya](https://proza.ru/avtor/garya), [stihi.ru/avtor/garya](https://stihi.ru/avtor/garya).
- The original texts are published here **with the author's permission**.
- This repository continues the series in the same style and with the same ideas (see [AGENTS.md](AGENTS.md)).
  The author's views, including those he stated only in reader comments, and his later prose are collected in
  [`sources/garya/`](sources/garya/) so new articles can follow them closely.
- **English is the primary language** of the repository. Content is translated into other languages,
  starting with **Russian**.

## 2. Languages

| Code | Role | Folder |
|------|------|--------|
| `en` | Primary language: repository docs, README, metadata, new articles by default | [`en/`](en/) |
| `ru` | First translation; also the original language of articles 01–15 | [`ru/`](ru/) |
| …    | Future languages (`de`, `es`, …) — same layout | `<code>/` |

Rules:

- Language folders use ISO 639-1 codes.
- Each article has a single **original** (`original_lang` in front matter). All other language versions
  are translations of that original, not of each other. Articles 01–15: original `ru`.
  New articles: original `en` unless written in Russian first.
- Every language folder holds the same set of files with the same names. A missing text is a stub
  with `status: pending` (see §4), never an absent file — so links between languages never break.
- Repository-level files (`README.md`, `SPEC.md`, `AGENTS.md`, `images/README.md`) are in English.
  Each language folder has its own `README.md` — a table of contents in that language.
- Source material by the author (original comments, prose) stays in **Russian**, exactly as written.
  English analysis and translations of source material live in `sources/garya/en/`.

## 3. Repository layout

```
README.md                  English overview + table of contents (all languages)
SPEC.md                    this file
AGENTS.md                  instructions for AI agents and authors (style, persona, translation, conventions)
CLAUDE.md                  pointer to AGENTS.md for Claude Code
en/
  README.md                English table of contents
  01-introduction.md
  ...
ru/
  README.md                Русское оглавление
  01-introduction.md
  ...
sources/
  README.md                what the source material is and how to use it
  continuation-notes.md    record of the written continuation articles: conclusions, facts, images, deferrals
  garya/
    README.md              об авторе: ссылки, разрешение, состав материалов (ru)
    sqlru/                 source: the sql.ru blog — each post as published, article text + comments (ru)
      01-introduction.md   same NN-slug as the article
      ...
      2012-05-17-seti-talk.md   unnumbered posts (date + slug)
    proza/                 the author's later prose from proza.ru, Russian originals
      podpolshchiki.md
      dialogi-s-samim-soboj.md
    en/                    English analysis of everything above
      author-profile.md    the author: worldview, logic, voice, debating manner, life
      01-introduction.md   notes on an article + the author's comments under it
      ...
      proza-podpolshchiki.md
      proza-dialogi-s-samim-soboj.md
images/                    shared, language-neutral images used by any language version
  README.md                image registry: file, used in, source, license, author
  venus-flytrap-closing.gif
  world-population-growth.ru.png
tools/
  import_sqlru.py          blog importer: articles → ru/, posts with comments → sources/garya/sqlru/, charts → images/
  import_proza.py          prose importer: proza.ru → sources/garya/proza/
  figures.py               draws the continuation's diagrams and charts → images/<name>.svg and <name>.ru.svg
```

## 4. Articles

### 4.1 File naming

`<lang>/<NN>-<slug>.md`

- `NN` — two-digit sequence number in the series (`01`…`99`); it defines the reading order. The series is
  meant to be read sequentially: later articles build on conclusions of earlier ones.
  `01`–`15` are the author's originals; `16` onwards is the **continuation** written for this repository
  (16–30 are planned, in four parts; the next free number is `31`).
- `slug` — short English kebab-case name, **identical in every language** (`ru/02-anthropocentrism.md`
  and `en/02-anthropocentrism.md` are the same article). Slugs never change once published.
- Numbers are never reused or renumbered.

### 4.2 Front matter

```yaml
---
id: 02                          # same as NN in the file name
slug: anthropocentrism          # same as in the file name
title: "Антропоцентризм"        # title in this language
lang: ru                        # language of this file
original_lang: ru               # language of the original
series: "Диалог у костра"       # series name in this language ("Campfire Dialogues" in en)
published: 2011-10-14           # date of first publication of the original
tags: ["антропоцентризм"]       # tags in this language
source: http://www.sql.ru/blogs/garya/1053          # only for articles 01–15
archive: https://web.archive.org/web/.../1053       # only for articles 01–15
author: "Андрей Гордиенко (Garya)"                  # in the language of the file
author_url: https://proza.ru/avtor/garya
sqlru: ../sources/garya/sqlru/02-anthropocentrism.md         # the post on sql.ru with its comments
notes: ../sources/garya/en/02-anthropocentrism.md           # source notes, if any
status: pending                 # original | translated | reviewed | pending
---
```

A continuation article has no `source`/`archive`/`author` fields and adds instead:

```yaml
original_lang: en
continuation: true              # written for this repository, not by the original author
part: II                        # part of the continuation: I–IV
builds_on: [04, 08, 11, 22]     # articles whose conclusions it relies on
```

In every table of contents continuation articles are listed in a separate *Continuation* / *Продолжение* block
and marked as such.

`status`: `original` — this file is the original text; `pending` — stub, the text is not here yet;
`translated` — translated, not yet proofread by a native speaker; `reviewed` — proofread and approved.
When the original changes, its translations go back to `translated` and are re-checked.

A `pending` stub contains the front matter, the H1, a two-to-three sentence abstract in that language,
a link to the archived original (for 01–15) and the marker `<!-- import:pending -->`.

### 4.3 Body

- `# <Title>` — the only H1, equal to `title`. No number in the heading.
- Dialogue lines start with an em dash and a space: `— Текст реплики, — сказал Андрей.` (never a hyphen:
  in Markdown `- ` starts a list). One line of dialogue per paragraph, blank line between paragraphs.
- Emphasis: `*italic*`. The key conclusion of the evening: `**bold**`. `<sup>`/`<sub>` allowed.
- Links to other articles are relative and stay inside the same language: `[антропоцентризм](02-anthropocentrism.md)`.
- External links point to the original source; if it is dead, to its Wayback Machine snapshot.
- Footer — an author line (links to the author and to his comments under the article), then the navigation line:
  `[← 01](./01-introduction.md) · [Contents](./README.md) · [03 →](./03-mind-and-intelligence.md)`
  (in Russian: `Оглавление`).

## 5. Import of the originals

The author has permitted publishing his texts here. They are imported by two scripts (standard library only;
both require `--authorized` as a reminder that the texts are published by permission):

- `python tools/import_sqlru.py --authorized` imports the blog from pinned Wayback Machine snapshots:
  1. decodes `windows-1251`, takes the title, date, tags and the article body (no site chrome);
  2. converts HTML to Markdown: `<br>` → paragraphs, `<b>`/`<font>` → `**bold**`, `<i>`/`<u>` → `*italic*`,
     `<sup>`/`<sub>` kept, Wayback prefixes stripped; links to other posts of the blog become relative links;
  3. replaces images per its `IMAGES` table with shared files from `images/`, otherwise a `TODO` comment, and
     downloads the author's own charts that survive in the archive into `images/`;
  4. normalises dialogue typography only (`- ` → `— `, ` - ` → ` — `). The wording is kept as is; editorial
     fixes go in separate commits;
  5. fills the `ru/NN-slug.md` stubs (`status: original`, author line, navigation);
  6. writes `sources/garya/sqlru/<name>.md` for every post — the blog page as published: the post text, then
     the comments under it (the author's in full, readers' shortened to 300 characters as context, since they
     belong to their authors). `--skip-articles` rebuilds these pages without touching `ru/`.
- `python tools/import_proza.py --authorized` imports the books «Подпольщики» and «Диалоги с самим собой» from
  [proza.ru/avtor/garya](https://proza.ru/avtor/garya): one Markdown file per book, one `##` per chapter.

Already imported files are skipped unless `--force`; `--root DIR` writes the same tree elsewhere (dry run).

| # | Original title | Slug | Published | Post |
|---|----------------|------|-----------|------|
| 01 | Вступление | `introduction` | 2011-10-09 | [1051](https://web.archive.org/web/20181204120328/http://www.sql.ru/blogs/garya/1051) |
| 02 | Антропоцентризм | `anthropocentrism` | 2011-10-14 | [1053](https://web.archive.org/web/20181113064905/http://www.sql.ru/blogs/garya/1053) |
| 03 | Разум и интеллект | `mind-and-intelligence` | 2011-10-16 | [1055](https://web.archive.org/web/20181027074322/http://www.sql.ru/blogs/garya/1055) |
| 04 | В поисках источника инициативы | `source-of-initiative` | 2011-10-20 | [1058](https://web.archive.org/web/20181113070611/http://www.sql.ru/blogs/garya/1058) |
| 05 | Искусственный интеллект | `artificial-intelligence` | 2011-10-22 | [1061](https://web.archive.org/web/20181025210541/http://www.sql.ru/blogs/garya/1061) |
| 06 | Ошибка Карла Маркса | `karl-marx-mistake` | 2011-10-25 | [1065](https://web.archive.org/web/20190415122212/http://www.sql.ru/blogs/garya/1065) |
| 07 | Истинные причины глобального экономического кризиса | `global-economic-crisis` | 2011-10-26 | [1066](https://web.archive.org/web/20181022054953/http://www.sql.ru/blogs/garya/1066) |
| 08 | О некоторых особенностях человеческой психики | `human-psyche` | 2011-10-29 | [1069](https://web.archive.org/web/20181109163017/http://www.sql.ru/blogs/garya/1069) |
| 09 | История безработицы, причины голода в Африке и избирательность недальновидности разума | `unemployment-and-famine` | 2011-11-01 | [1073](https://web.archive.org/web/20181109162420/http://www.sql.ru/blogs/garya/1073) |
| 10 | О жизненном цикле динамических систем и о смысле смерти | `life-cycle-and-death` | 2011-11-09 | [1077](https://web.archive.org/web/20180910062855/http://www.sql.ru/blogs/garya/1077) |
| 11 | О замедлении роста численности человечества, о симбиозе и паразитизме | `symbiosis-and-parasitism` | 2011-11-12 | [1078](https://web.archive.org/web/20181024064141/http://www.sql.ru/blogs/garya/1078) |
| 12 | Доли ценности, создаваемые людьми и техносферой | `value-shares` | 2011-11-13 | [1079](https://web.archive.org/web/20181109162425/http://www.sql.ru/blogs/garya/1079) |
| 13 | Сингулярность как процесс | `singularity-as-process` | 2011-12-06 | [1095](https://web.archive.org/web/20181018164254/http://www.sql.ru/blogs/garya/1095) |
| 14 | Апоптоз человечества | `apoptosis-of-humanity` | 2011-12-18 | [1103](https://web.archive.org/web/20181109163024/http://www.sql.ru/blogs/garya/1103) |
| 15 | Контраргументы Роджера Пенроуза | `penrose-counterarguments` | 2012-04-05 | [1245](https://web.archive.org/web/20181109163033/http://www.sql.ru/blogs/garya/1245) |
| — | Международный конгресс GF2045 | notes only | 2012-02-18 | [1135](https://web.archive.org/web/20181109163027/http://www.sql.ru/blogs/garya/1135) |
| — | Доклад автора блога в НКЦ SETI ГАИШ МГУ | notes only | 2012-05-17 | [1278](https://web.archive.org/web/20181024181550/http://www.sql.ru/blogs/garya/1278) |

The two unnumbered posts are announcements, not articles of the series; they exist only as source notes
(the SETI post carries the largest comment discussion of the blog).

## 6. Source material (`sources/`)

Material for writing and translating, not published content of the series.

- `sources/garya/sqlru/` (the source: the blog on sql.ru, posts with comments) and `sources/garya/proza/` hold
  the author's original texts in Russian, untouched. `ru/` holds the same articles as the edition of the series:
  editorial fixes go there, while `sqlru/` stays as published.
- `sources/garya/en/` holds the English analysis. One file per post: `NN-slug.md` (same name as the article),
  or `YYYY-MM-DD-slug.md` for unnumbered posts. One `proza-<book>.md` per book. A post file has: metadata, summary,
  key theses, staging and devices, terms, sources and images, **the author in the comments** (objection → his
  answer, grouped by topic), voice and personality, open threads.
- [`sources/garya/en/author-profile.md`](sources/garya/en/author-profile.md) is the synthesis: worldview, chain of
  conclusions, logic, voice, debating manner, life experience. [AGENTS.md](AGENTS.md) relies on it.
- Notes are written in our own words with short quotes. Readers' comments are paraphrased, without names.
- [`sources/continuation-notes.md`](sources/continuation-notes.md) records every written continuation article: what
  it established, the facts and images it used, and the topics it deferred to later articles. It is updated in the
  same commit as the article (see AGENTS.md §4).

## 7. Images

- All images live in one shared folder, [`images/`](images/), and are referenced from any language as
  `../images/<name>`. An image is stored once, however many articles or languages use it
  (the original blog itself reused one chart in articles 10 and 13).
- Names describe the content, not the article: `venus-flytrap-closing.gif`, `brain-simulation-forecast.svg`
  (not `article-05-image-1.png`). English kebab-case.
- Images without text are language-neutral. If an image contains text, keep the source neutral where possible
  (SVG with text layers) and add localized variants with a language suffix: `world-population-growth.png` (en),
  `world-population-growth.ru.png`. An article uses the variant for its language, falling back to the neutral one.
- Our own diagrams and charts are drawn by [`tools/figures.py`](tools/figures.py) (standard library only):
  one function per figure, labels for every language in one place, `python tools/figures.py [NAME ...]`
  rewrites the SVG files. Edit the script, not the SVG.
- Formats: SVG for charts and diagrams, PNG for illustrations, JPEG for photos, GIF only for animations.
  Keep files under ~500 KB.
- Only images we may redistribute: our own work, public domain, or free licenses (CC BY / CC BY-SA, …).
  Every image is registered in [`images/README.md`](images/README.md) with source, author and license.
  Third-party images that cannot be redistributed are redrawn as our own (e.g. a chart re-plotted from the
  cited data) or replaced by a link to the source. The author's own pictures are stored with his permission.
- Alt text is written in the language of the article.

## 8. README and tables of contents

- [`README.md`](README.md) (English): short description, how to read the series, the table of contents with
  links to every language version, the status of each.
- `<lang>/README.md`: the same table of contents in that language.
- Adding, renaming or changing the status of an article updates all tables of contents in the same commit.

## 9. Workflow

1. **New article.** Read [`sources/garya/en/author-profile.md`](sources/garya/en/author-profile.md) and the notes of
   the articles it builds on. Write the original (default `en/`), take the next number and a slug, follow the
   style in [AGENTS.md](AGENTS.md). Create `pending` stubs for the other languages. Update all tables of contents.
   For a continuation article, follow the step-by-step list in AGENTS.md §4 and update
   [`sources/continuation-notes.md`](sources/continuation-notes.md).
2. **Translation.** Replace the stub with the translation, set `status: translated`, keep the slug, the
   structure, links and images. Use the glossary in [AGENTS.md](AGENTS.md).
3. **Review.** A native speaker proofreads and sets `status: reviewed`.

## 10. Roadmap

1. Repository skeleton, spec, agent instructions, stubs — **done**.
2. English notes on all 17 posts and the author's prose; the author profile — **done**.
3. Import the originals: `tools/import_sqlru.py --authorized` and `tools/import_proza.py --authorized` — **done**.
4. Redraw the remaining charts (articles 05, 08, 10, 11) as SVG; replace the third-party picture of 09.
5. Translate 01–15 into English (`en/`).
6. Write the continuation 16–30 in four parts: I. Re-examining the foundations (16–20), II. Machines today (21–23), III. Economy and people (24–26), IV. The transition and after (27–30). Stubs with abstracts are in place. Written: 16–28.
7. Further languages.
