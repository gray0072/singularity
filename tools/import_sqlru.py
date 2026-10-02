"""Import the original Russian articles and comments from the sql.ru blog (via the Wayback Machine).

The texts belong to their author and are imported with his permission (SPEC.md, section 5);
the script refuses to start without --authorized.

Usage:
    python tools/import_sqlru.py --authorized             # fill ru/ stubs, write sqlru/ pages and the author's images
    python tools/import_sqlru.py --authorized --force     # overwrite what was already imported
    python tools/import_sqlru.py --authorized --force --skip-articles   # rebuild sqlru/ only, keep ru/ as edited
    python tools/import_sqlru.py --authorized --root DIR  # write the same tree under DIR (dry run)

Writes:
    ru/NN-slug.md                              original article (status: original)
    sources/garya/sqlru/NN-slug.md             the blog page as published: article text + comments under it
    sources/garya/sqlru/YYYY-MM-DD-slug.md     unnumbered posts: post text + comments
    images/<name>                              the author's own charts that survive in the archive

Standard library only.
"""

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PENDING_MARKER = "<!-- import:pending -->"
SERIES = "Диалог у костра"
AUTHOR = "Андрей Гордиенко (Garya)"
AUTHOR_URL = "https://proza.ru/avtor/garya"
AUTHOR_NICK = "Garya"
CONTEXT_CHARS = 300  # readers' comments are kept as short context only

# (number, sql.ru post id, slug, Wayback timestamp of a known good snapshot)
ARTICLES = [
    (1, 1051, "introduction", "20181204120328"),
    (2, 1053, "anthropocentrism", "20181113064905"),
    (3, 1055, "mind-and-intelligence", "20181027074322"),
    (4, 1058, "source-of-initiative", "20181113070611"),
    (5, 1061, "artificial-intelligence", "20181025210541"),
    (6, 1065, "karl-marx-mistake", "20190415122212"),
    (7, 1066, "global-economic-crisis", "20181022054953"),
    (8, 1069, "human-psyche", "20181109163017"),
    (9, 1073, "unemployment-and-famine", "20181109162420"),
    (10, 1077, "life-cycle-and-death", "20180910062855"),
    (11, 1078, "symbiosis-and-parasitism", "20181024064141"),
    (12, 1079, "value-shares", "20181109162425"),
    (13, 1095, "singularity-as-process", "20181018164254"),
    (14, 1103, "apoptosis-of-humanity", "20181109163024"),
    (15, 1245, "penrose-counterarguments", "20181109163033"),
]
# Unnumbered posts (announcements): no article in ru/, only a page in sources/garya/sqlru/.
EXTRA_POSTS = [
    (1135, "2012-02-18-gf2045-congress", "20181109163027"),
    (1278, "2012-05-17-seti-talk", "20181024181550"),
]
SLUG_BY_POST = {post: f"{num:02d}-{slug}.md" for num, post, slug, _ in ARTICLES}

# The author's own charts that survive in the Wayback Machine: attachment id -> shared file name.
AUTHOR_IMAGES = {
    "11582885": "dynamic-system-life-cycle.png",
    "11716462": "singularity-vertical-asymptote.png",
}

# Original image URL fragment -> Markdown to put in its place.
IMAGES = {
    "Dionaea_muscipula_closing_trap_animation":
        "![Венерина мухоловка захлопывает ловушку](../images/venus-flytrap-closing.gif)",
    "World_population_%28UN%29_ru":
        "![Рост численности населения Земли](../images/world-population-growth.ru.png)",
    "3dnews.ru/_imgdata/img/2009/11/22/150643":
        "<!-- TODO image: brain-simulation-forecast — redraw the 3dnews.ru chart as our own SVG, see images/README.md -->",
    "actualfile.aspx?id=11582885":
        "![Жизненный цикл динамической системы](../images/dynamic-system-life-cycle.png)",
    "actualfile.aspx?id=11716462":
        "![Сингулярность: вертикальная асимптота](../images/singularity-vertical-asymptote.png)",
}
# Anything else becomes a TODO comment with the original URL; images/README.md lists the planned names.

MONTHS = {"янв": 1, "фев": 2, "мар": 3, "апр": 4, "мая": 5, "май": 5, "июн": 6,
          "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12}


def fetch_bytes(url, attempts=5):
    # The Wayback Machine refuses connections when requests come too fast: back off and retry.
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read(), r.headers.get_content_type()
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(10 * (attempt + 1))


def fetch(post, ts):
    url = f"https://web.archive.org/web/{ts}/http://www.sql.ru/blogs/garya/{post}"
    return fetch_bytes(url)[0].decode("cp1251"), url


def unwrap_archive(url):
    url = html.unescape(url)
    return re.sub(r"^(https?:)?//web\.archive\.org/web/\d+(im_|js_|cs_)?/", "", url)


class BodyToMarkdown(HTMLParser):
    INLINE = {"b": "**", "strong": "**", "i": "*", "em": "*", "u": "*"}

    def __init__(self, link_prefix=""):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.link = None
        self.link_prefix = link_prefix

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "br":
            self.out.append("\n")
        elif tag in self.INLINE:
            self.out.append(self.INLINE[tag])
        elif tag in ("sup", "sub"):
            self.out.append(f"<{tag}>")
        elif tag == "a":
            self.link = (unwrap_archive(a.get("href", "")), len(self.out))
        elif tag == "img":
            src = unwrap_archive(a.get("src", ""))
            md = next((v for k, v in IMAGES.items() if k in src), f"<!-- TODO image: {src} -->")
            if self.link_prefix:
                md = md.replace("](../images/", f"]({self.link_prefix}../images/")
            self.out.append(f"\n\n{md}\n\n")

    def handle_endtag(self, tag):
        if tag in self.INLINE:
            self.out.append(self.INLINE[tag])
        elif tag in ("sup", "sub"):
            self.out.append(f"</{tag}>")
        elif tag == "a" and self.link:
            href, start = self.link
            text = "".join(self.out[start:]).strip()
            del self.out[start:]
            m = re.search(r"sql\.ru/blogs/garya/(\d+)", href)
            if m and int(m.group(1)) in SLUG_BY_POST:
                href = self.link_prefix + SLUG_BY_POST[int(m.group(1))]
            self.out.append(f" [{text}]({href}) " if text else "")
            self.link = None

    def handle_data(self, data):
        self.out.append(data)


def to_markdown(body_html, link_prefix=""):
    p = BodyToMarkdown(link_prefix)
    p.feed(body_html)
    text = "".join(p.out).replace("\xa0", " ")
    text = re.sub(r"\*\*\s*\*\*", "", text)
    paragraphs = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        line = re.sub(r" ([.,:;!?)])", r"\1", line)
        if not line:
            continue
        # Dialogue: a leading hyphen would become a Markdown list item.
        line = re.sub(r"^[-–—]\s*", "— ", line)
        line = re.sub(r" [-–] ", " — ", line)
        paragraphs.append(line)
    return "\n\n".join(paragraphs) + "\n"


def parse(page):
    title = html.unescape(re.search(r"<h1>(.*?)</h1>", page, re.S).group(1).strip())
    m = re.match(r"(\d+)\.\s*(.*)", title)
    num, title = (int(m.group(1)), m.group(2)) if m else (None, re.sub(r"^б/н\.\s*", "", title))
    d, mon, y = re.search(r"добавлено:\s*(\d+)&nbsp;(\S+?)&nbsp;(\d+)", page).groups()
    date = f"20{y}-{MONTHS[mon[:3].lower()]:02d}-{int(d):02d}"
    tags_html = re.search(r'<ul class="taglist">(.*?)</ul>', page, re.S).group(1)
    tags = [html.unescape(t).strip() for t in re.findall(r">([^<]+)</a>", tags_html) if t.strip()]
    body = re.search(r'<p class="info">.*?</p>\s*<div>(.*?)</div>\s*</div>\s*<!--end posts-->', page, re.S).group(1)
    return num, title, date, tags, body


def parse_comments(page):
    found = re.findall(
        r'<li id="c(\d+)">\s*<div class="header[^"]*">\s*<a class="date">(.*?)</a>\s*'
        r'<b class="author">(.*?)</b>.*?<div class="post">\s*(.*?)\s*</div>\s*</li>', page, re.S)
    return [(cid, html.unescape(date).strip(), html.unescape(author).strip(), body)
            for cid, date, author, body in found]


def front_matter(num, slug, title, date, tags, post, archive_url):
    tag_list = ", ".join(f'"{t}"' for t in tags)
    return (
        "---\n"
        f"id: {num:02d}\n"
        f"slug: {slug}\n"
        f'title: "{title}"\n'
        "lang: ru\n"
        "original_lang: ru\n"
        f'series: "{SERIES}"\n'
        f'author: "{AUTHOR}"\n'
        f"author_url: {AUTHOR_URL}\n"
        f"published: {date}\n"
        f"tags: [{tag_list}]\n"
        f"source: http://www.sql.ru/blogs/garya/{post}\n"
        f"archive: {archive_url}\n"
        f"sqlru: ../sources/garya/sqlru/{num:02d}-{slug}.md\n"
        f"notes: ../sources/garya/en/{num:02d}-{slug}.md\n"
        "status: original\n"
        "---\n"
    )


def nav(num, slug):
    prev_ = next((f"[← {n:02d}](./{n:02d}-{s}.md)" for n, _, s, _ in ARTICLES if n == num - 1), "")
    next_ = next((f"[{n:02d} →](./{n:02d}-{s}.md)" for n, _, s, _ in ARTICLES if n == num + 1), "")
    links = " · ".join(p for p in (prev_, "[Оглавление](./README.md)", next_) if p)
    return (f"\n---\n\nАвтор: [{AUTHOR}]({AUTHOR_URL}) · "
            f"[Оригинал на sql.ru с комментариями](../sources/garya/sqlru/{num:02d}-{slug}.md)\n\n{links}\n")


def sqlru_md(post, name, title, date, archive_url, article, comments, post_body):
    own = sum(1 for _, _, a, _ in comments if a == AUTHOR_NICK)
    lines = [
        "---",
        f"post: {post}",
        f'title: "{title}"',
        f"article: {article or 'none'}",
        f"published: {date}",
        f"source: http://www.sql.ru/blogs/garya/{post}",
        f"archive: {archive_url}",
        f"comments_total: {len(comments)}",
        f"author_comments: {own}",
        f"notes: ../en/{name}.md",
        "---",
        "",
        f"# {title}",
        "",
        f"Блог «Технологическая сингулярность» на sql.ru, запись от {date}: текст в том виде, в каком он был "
        f"опубликован, и комментарии под ним. Комментарии автора ({AUTHOR_NICK}) приведены полностью. Реплики "
        f"читателей сокращены до {CONTEXT_CHARS} знаков и оставлены как контекст; полностью их можно прочитать в "
        f"[архиве]({archive_url}).",
    ]
    if article:
        lines += ["", f"Статья серии: [{title}]({article})"]
    lines += ["", "## Текст записи", "", to_markdown(post_body, "../../../ru/").rstrip()]
    lines += ["", "## Комментарии"]
    for cid, cdate, author, body in comments:
        text = to_markdown(body, "../../../ru/").strip()
        if author == AUTHOR_NICK:
            lines += ["", f"### {cdate} · **{author}** (автор)", "", text]
        else:
            short = re.sub(r"\s+", " ", text)
            if len(short) > CONTEXT_CHARS:
                short = short[:CONTEXT_CHARS].rsplit(" ", 1)[0] + " …"
            lines += ["", f"### {cdate} · {author}", "", f"> {short}"]
    return "\n".join(lines) + "\n"


def writable(path, force):
    return force or not path.exists() or PENDING_MARKER in path.read_text(encoding="utf-8")


def write(root, path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(root)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorized", action="store_true", help="the author has permitted the import")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--skip-articles", action="store_true", help="do not touch ru/ (it may hold editorial fixes)")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()
    if not args.authorized:
        sys.exit("The original texts may be imported only with the author's permission. See SPEC.md, section 5.")
    root = args.root

    for att, name in AUTHOR_IMAGES.items():
        target = root / "images" / name
        if target.exists() and not args.force:
            continue
        data, ctype = fetch_bytes(f"https://web.archive.org/web/2018im_/http://www.sql.ru/forum/actualfile.aspx?id={att}")
        if not ctype.startswith("image/"):
            print(f"skip  images/{name} (not in the archive)")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(f"wrote images/{name}")

    for num, post, slug, ts in ARTICLES:
        name = f"{num:02d}-{slug}"
        article = root / "ru" / f"{name}.md"
        page_file = root / "sources" / "garya" / "sqlru" / f"{name}.md"
        article_due = writable(article, args.force) and not args.skip_articles
        if not article_due and page_file.exists() and not args.force:
            print(f"skip  {name} (already imported, use --force)")
            continue
        page, archive_url = fetch(post, ts)
        n, title, date, tags, body = parse(page)
        assert n == num, f"{post}: expected article {num}, got {n}"
        if article_due:
            text = front_matter(num, slug, title, date, tags, post, archive_url)
            text += f"\n# {title}\n\n" + to_markdown(body) + nav(num, slug)
            write(root, article, text)
        if args.force or not page_file.exists():
            write(root, page_file, sqlru_md(post, name, title, date, archive_url,
                                            f"../../../ru/{name}.md", parse_comments(page), body))

    for post, name, ts in EXTRA_POSTS:
        page_file = root / "sources" / "garya" / "sqlru" / f"{name}.md"
        if page_file.exists() and not args.force:
            print(f"skip  {name} (already imported, use --force)")
            continue
        page, archive_url = fetch(post, ts)
        _, title, date, _, body = parse(page)
        write(root, page_file, sqlru_md(post, name, title, date, archive_url, None, parse_comments(page), body))


if __name__ == "__main__":
    sys.exit(main())
