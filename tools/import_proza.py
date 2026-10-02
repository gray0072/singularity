"""Import the author's prose from proza.ru into sources/garya/proza/ (Russian originals).

Used to understand the author's personality and voice; not part of the article series.
The texts belong to the author and are imported with his permission (SPEC.md, section 5);
the script refuses to start without --authorized.

Usage:
    python tools/import_proza.py --authorized             # write books that are not there yet
    python tools/import_proza.py --authorized --force     # overwrite
    python tools/import_proza.py --authorized --root DIR  # write the same tree under DIR (dry run)

Standard library only.
"""

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTHOR_PAGE = "https://proza.ru/avtor/garya"
AUTHOR = "Андрей Гордиенко"

# Book header on the author page -> (file slug, English title)
BOOKS = {
    "Подпольщики повесть": ("podpolshchiki", "The Underground Men"),
    "Диалоги с самим собой": ("dialogi-s-samim-soboj", "Dialogues with Myself"),
}


def get(url, attempts=5):
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read().decode("cp1251")
        except (urllib.error.URLError, TimeoutError):
            if attempt == attempts - 1:
                raise
            time.sleep(10 * (attempt + 1))


def books():
    page = get(AUTHOR_PAGE)
    result = {}
    for m in re.finditer(r'<div ID="bookheader"><a name="\d+">([^<]+)</a></div>\s*<ul[^>]*>(.*?)</ul>', page, re.S):
        items = re.findall(r'<a href="(/\d{4}/\d\d/\d\d/\d+)" class="poemlink">([^<]+)</a>\s*'
                           r'<small>- ([^,]+), ([\d.]+)', m.group(2))
        result[html.unescape(m.group(1)).strip()] = [(u, html.unescape(t), g, d) for u, t, g, d in items]
    return result


def to_markdown(body_html):
    text = re.sub(r"<br\s*/?>", "\n", body_html)
    text = re.sub(r"<b>(.*?)</b>", r"**\1**", text, flags=re.S)
    text = re.sub(r"<i>(.*?)</i>", r"*\1*", text, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).replace("\xa0", " ")
    paragraphs = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line:
            continue
        line = re.sub(r"^[-–—]\s*", "— ", line)  # dialogue, not a Markdown list
        paragraphs.append(line)
    return "\n\n".join(paragraphs)


def iso(date):
    d, m, y = date.split(".")
    return f"{y}-{m}-{d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--authorized", action="store_true", help="the author has permitted the import")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args()
    if not args.authorized:
        sys.exit("The author's texts may be imported only with his permission. See SPEC.md, section 5.")

    found = books()
    for header, (slug, title_en) in BOOKS.items():
        target = args.root / "sources" / "garya" / "proza" / f"{slug}.md"
        if target.exists() and not args.force:
            print(f"skip  {target.name} (already imported, use --force)")
            continue
        items = found[header]
        title_ru = re.sub(r"\s+повесть$", "", header)
        genre = items[0][2]
        dates = [iso(d) for *_, d in items]
        parts = []
        for url, chapter, _, date in items:
            page = get("https://proza.ru" + url)
            body = re.search(r'<div class="text">(.*?)</div>', page, re.S).group(1)
            parts.append(f"## {chapter}\n\n<https://proza.ru{url}> · {iso(date)}\n\n{to_markdown(body)}\n")
            time.sleep(1)
        sources = "\n".join(f"  - https://proza.ru{u}" for u, *_ in items)
        text = (
            "---\n"
            f'title: "{title_ru}"\n'
            f'title_en: "{title_en}"\n'
            f'author: "{AUTHOR}"\n'
            f"author_url: {AUTHOR_PAGE}\n"
            f'genre: "{genre}"\n'
            f"published: {min(dates)}..{max(dates)}\n"
            "lang: ru\n"
            f"notes: ../en/proza-{slug}.md\n"
            f"source:\n{sources}\n"
            "---\n\n"
            f"# {title_ru}\n\n"
            f"{AUTHOR}, [proza.ru]({AUTHOR_PAGE}). Опубликовано с разрешения автора.\n\n"
            + "\n".join(parts)
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {target.relative_to(args.root)} ({len(items)} parts)")


if __name__ == "__main__":
    sys.exit(main())
