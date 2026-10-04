"""Import the sql.ru forum thread the blog grew out of (via the Wayback Machine).

The thread «Вот, решил процитировать на ПТ сценарий апокалипсиса...» (forum «Просто треп», tid=695766) was
started by Garya on 15 September 2009 and ran until at least July 2017, about 14,000 messages on 568 pages.
sql.ru closed in 2022; from August 2017 the forum was closed to guests, so the Wayback Machine holds only
the pages it captured before that. The forum was public, so every surviving message, the author's and the
readers', is kept in full, with the nick of its author.

Usage:
    python tools/import_forum.py                  # write sources/garya/sqlru/<name>.md
    python tools/import_forum.py --force          # overwrite it
    python tools/import_forum.py --root DIR       # write the same file under DIR (dry run)
    python tools/import_forum.py --cache DIR      # keep the raw pages in DIR and reuse them on the next run

Writes:
    sources/garya/sqlru/2009-09-15-apocalypse-scenario-thread.md   all archived messages, grouped by page

Standard library only.
"""

import argparse
import html
import re
import sys
import time
from datetime import datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_sqlru import ARCHIVED_PAGES, AUTHOR_NICK, MONTHS, fetch_bytes, unlink_sqlru, unwrap_archive  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TID = 695766
NAME = "2009-09-15-apocalypse-scenario-thread"
FORUM = "Просто треп"
SLUG = "vot-reshil-procitirovat-na-pt-scenariy-apokalipsisa"
OLD_URL = f"http://www.sql.ru:80/forum/actualthread.aspx?tid={TID}"
NEW_URL = f"http://www.sql.ru:80/forum/{TID}-{{page}}/{SLUG}"
PER_PAGE = 25

# (page, Wayback timestamp, URL) for every page the Wayback Machine kept: for each page the largest snapshot.
# Snapshots of about 3 KB are not pages: from August 2017 sql.ru answered guests «У вас нет прав на чтение
# данного форума». Page 1 survives twice, in the 2011 (old) and the 2017 (new) URL format; the messages are
# merged by their id, the first source wins.
PAGES = [(1, "20111130034717", OLD_URL), (1, "20170604040502", NEW_URL.format(page=1))] + [
    (n, ts, NEW_URL.format(page=n)) for n, ts in [
        (2, "20161117061909"), (269, "20160915221405"), (270, "20160913051013"), (271, "20160915225029"),
        (465, "20130514050226"), (466, "20130514025810"), (467, "20130514054016"), (468, "20130514050231"),
        (496, "20140429085136"), (497, "20140429085142"), (498, "20140429085147"), (499, "20140429085357"),
        (500, "20140429085152"), (501, "20140429085158"), (502, "20140429085202"), (503, "20140429085209"),
        (504, "20140428173432"), (505, "20140427035553"),
        (540, "20161107103719"), (541, "20161107102449"), (542, "20161107103014"), (543, "20161106122344"),
        (544, "20170118161546"), (546, "20170506062018"), (547, "20170506053609"), (548, "20170122215102"),
        (556, "20170609192802"), (557, "20170609180005"), (558, "20170608095526"), (559, "20170608103617"),
        (560, "20170609114101"), (561, "20170709134041"), (562, "20170604193942"), (563, "20170604041904"),
        (564, "20170604200309"), (565, "20170607005318"), (566, "20170611212428"), (567, "20170711002648"),
        (568, "20170720182759"),
    ]]

# sql.ru forum smileys -> text.
SMILEYS = {"laugh.gif": ":-)", "cry.gif": ":-(", "smoke.gif": "*курит*", "wink.gif": ";-)", "sad.gif": ":-(",
           "smile.gif": ":-)", "shuffle.gif": "*смущается*", "crazy.gif": "*crazy*", "nervous.gif": "*нервничает*"}
MONTH_GEN = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля", 8: "августа",
             9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}


def archive_url(ts, url):
    return f"https://web.archive.org/web/{ts}/{url}"


def thread_links():
    """Links to archived pages of this thread become links to their snapshots (see unlink_sqlru)."""
    for page, ts, url in PAGES:
        if url == OLD_URL:
            continue
        for host in ("http://www.sql.ru", "https://www.sql.ru", "http://sql.ru", "https://sql.ru"):
            ARCHIVED_PAGES.setdefault(f"{host}/forum/{TID}-{page}/{SLUG}", archive_url(ts, url))
        if page == 1:
            for host in ("http://www.sql.ru", "https://www.sql.ru"):
                ARCHIVED_PAGES.setdefault(f"{host}/forum/{TID}/{SLUG}", archive_url(ts, url))


class Quote:
    """A rendered quote block, kept apart from the text so that paragraphs are not split inside it."""

    def __init__(self, text):
        self.text = text


class ForumToMarkdown(HTMLParser):
    """sql.ru forum message HTML -> Markdown. Quote tables become `>` blocks headed by the quoted nick."""

    INLINE = {"b": "**", "strong": "**", "i": "*", "em": "*", "u": "*", "strike": "~~", "s": "~~"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames = [{"head": [], "body": [], "row": 1}]  # the message itself is a frame with no header
        self.link = None
        self.skip = 0  # inside the "+" toggle of a collapsed quote
        self.tables = []  # for each open table: True for a quote, False for a table of data
        self.cell = 0

    @property
    def out(self):
        f = self.frames[-1]
        return f["head"] if f["row"] == 0 else f["body"]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "span" and "onclick" in a:
            self.skip += 1
            if self.frames[-1]["row"] == 0:  # the toggle sits in the header of a collapsed (spoiler) quote
                self.frames[-1]["spoiler"] = True
        elif self.skip and tag == "span":
            self.skip += 1
        elif tag == "table":
            quote = "quote" in a.get("class", "") or (a.get("bgcolor") or "").upper() == "#DDDDDD"
            self.tables.append(quote)
            if quote:
                self.frames.append({"head": [], "body": [], "row": -1})
        elif tag == "tr" and self.tables and self.tables[-1]:
            self.frames[-1]["row"] += 1
        elif tag == "tr" and self.tables:
            self.out.append("\n")
            self.cell = 0
        elif tag in ("td", "th") and self.tables and not self.tables[-1]:
            self.out.append(" | " if self.cell else "")
            self.cell += 1
        elif tag in ("br", "p", "div", "pre"):
            self.out.append("\n")
        elif tag == "li":
            self.out.append("\n* ")
        elif tag in self.INLINE:
            self.out.append(self.INLINE[tag])
        elif tag in ("sup", "sub"):
            self.out.append(f"<{tag}>")
        elif tag == "a":
            self.link = (unwrap_archive(a.get("href", "")), len(self.out), self.out)
        elif tag == "img":
            src = unwrap_archive(a.get("src", ""))
            name = src.rsplit("/", 1)[-1]
            if "/forum/images/" in src:
                self.out.append(f" {SMILEYS.get(name, '*' + name.rsplit('.', 1)[0] + '*')} ")
            else:
                if src.startswith("/"):
                    src = "http://www.sql.ru" + src
                self.out.append(f"\n[изображение]({src})\n" if "sql.ru" not in src else f"\nизображение: {src}\n")
        elif tag in ("iframe", "embed") and a.get("src"):
            src = unwrap_archive(a["src"])
            m = re.search(r"youtube\.com/(?:embed|v)/([\w-]+)", src)
            src = f"https://www.youtube.com/watch?v={m.group(1)}" if m else src
            self.out.append(f"\n[видео]({src})\n")

    def handle_endtag(self, tag):
        if tag == "span" and self.skip:
            self.skip -= 1
        elif tag == "table" and self.tables and not self.tables[-1]:
            self.tables.pop()
            self.out.append("\n")
        elif tag == "table" and self.tables:
            self.tables.pop()
            f = self.frames.pop()
            head = re.sub(r"\s+", " ", "".join(p for p in f["head"] if isinstance(p, str))).strip()
            body = render(f["body"])
            if f.get("spoiler"):
                head = f"[спойлер] {head}".strip()
            lines = ([f"**{head}:**", ""] if head else []) + body.split("\n")
            self.out.append(Quote("\n".join(f"> {line}" if line else ">" for line in lines)))
        elif tag in self.INLINE:
            self.out.append(self.INLINE[tag])
        elif tag in ("sup", "sub"):
            self.out.append(f"</{tag}>")
        elif tag == "pre":
            self.out.append("\n")
        elif tag == "a" and self.link:
            href, start, out = self.link
            self.link = None
            if out is not self.out:
                return
            text = "".join(p for p in out[start:] if isinstance(p, str)).strip()
            if any(isinstance(p, Quote) for p in out[start:]):
                return
            del out[start:]
            if not text:
                return
            out.append(f" {text} " if text == href or text.rstrip("/") == href.rstrip("/") else f" [{text}]({href}) ")

    def handle_data(self, data):
        if self.skip:
            return
        # A "<" that would start an HTML tag in Markdown.
        self.out.append(re.sub(r"<(?=[A-Za-z/!])", "&lt;", data))


def render(pieces):
    """Join text pieces and rendered quotes into Markdown paragraphs."""
    paragraphs, buf = [], []

    def flush():
        text = "".join(buf).replace("\xa0", " ")
        text = re.sub(r"\*\*\s*\*\*", "", text)
        for line in text.split("\n"):
            line = re.sub(r"[ \t]+", " ", line).strip()
            line = re.sub(r" ([.,:;!?)])", r"\1", line)
            if not line:
                continue
            if re.fullmatch(r"[-_=*~]{3,}", line):  # a separator line, not a Markdown rule
                paragraphs.append("\\" + line)
                continue
            line = re.sub(r"^[-–—]\s*", "— ", line)  # a leading hyphen would become a Markdown list item
            line = re.sub(r" [-–] ", " — ", line)
            line = re.sub(r"^(#|>|\+\s)", r"\\\1", line)  # not a heading, quote or list item
            paragraphs.append(line)
        buf.clear()

    for p in pieces:
        if isinstance(p, Quote):
            flush()
            paragraphs.append(p.text)
        else:
            buf.append(p)
    flush()
    return "\n\n".join(paragraphs)


def to_markdown(body_html):
    p = ForumToMarkdown()
    p.feed(body_html)
    p.close()
    while p.tables:  # an unclosed table: close it
        p.handle_endtag("table")
    return unlink_sqlru(render(p.frames[0]["body"]), "../../../ru/", "")


def parse_date(text, snapshot):
    text = html.unescape(text).replace("\xa0", " ").strip()
    m = re.match(r"(\d+) (\S+) (\d+), (\d+):(\d+)", text)
    if m:
        d, mon, y, hh, mm = m.groups()
        return datetime(2000 + int(y), MONTHS[mon[:3].lower()], int(d), int(hh), int(mm))
    m = re.match(r"(сегодня|вчера), (\d+):(\d+)", text)
    if m:
        day = datetime.strptime(snapshot[:8], "%Y%m%d").date() - timedelta(days=m.group(1) == "вчера")
        return datetime(day.year, day.month, day.day, int(m.group(2)), int(m.group(3)))
    raise ValueError(f"unknown date: {text!r}")


MESSAGE = re.compile(
    r'<a name="(\d+)"></a>\s*<table class="msgTable">.*?class="messageHeader"[^>]*>(.*?)</td>.*?'
    r'<td style="width:15%" class="msgBody">(.*?)</td>\s*<td class="msgBody">(.*?)</td>\s*</tr>\s*<tr>\s*'
    r'<td colspan="2" class="msgFooter">\s*(.*?)\[', re.S)


def parse_page(page, snapshot):
    title = html.unescape(re.search(r"<title>(.*?) / ", page, re.S).group(1)).strip()
    replies = re.search(r"Ответов: (\d+)", page)
    numbers = [int(n) for n in re.findall(rf"/forum/{TID}-(\d+)/", page)]
    messages = []
    for mid, subject, who, body, when in MESSAGE.findall(page):
        nick = re.search(r"memberinfo\.aspx\?mid=\d+[^>]*>\s*(.*?)\s*</a>", who, re.S)
        nick = nick.group(1) if nick else re.sub(r"<[^>]+>", "\n", who).strip().split("\n")[0]
        subject = re.sub(r"<!--.*?-->|<[^>]+>|\[new\]", "", subject, flags=re.S)
        subject = re.sub(r"\s+", " ", html.unescape(subject).replace("\xa0", " ")).strip()
        messages.append({"id": int(mid), "nick": html.unescape(nick).strip(), "subject": subject,
                         "date": parse_date(when, snapshot), "body": body})
    return title, int(replies.group(1)) if replies else None, max(numbers, default=1), messages


def load(ts, url, cache):
    cached = cache / f"{ts}-{re.sub(r'[^0-9A-Za-z]+', '_', url)[-80:]}.html" if cache else None
    if cached and cached.exists():
        return cached.read_bytes().decode("cp1251")
    data = fetch_bytes(f"https://web.archive.org/web/{ts}id_/{url}")[0]
    if cached:
        cache.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(data)
    time.sleep(3)  # be polite to the Wayback Machine
    return data.decode("cp1251")


def archived_runs(pages):
    """Archived page numbers as (first, last) runs."""
    runs = []
    for n in pages:
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    return runs


def missing_note(first, last):
    if first == last:
        return f"*Страница {first} в архиве не сохранилась.*"
    return f"*Страницы {first}–{last} в архиве не сохранились.*"


def build(sources):
    """sources: list of (page, ts, url, html). Returns the Markdown text."""
    title, seen, by_page, archive_of, latest = None, set(), {}, {}, None
    for page, ts, url, text in sources:
        t, replies, max_page, messages = parse_page(text, ts)
        title = title or t
        archive_of.setdefault(page, archive_url(ts, url))
        if replies is not None and (latest is None or ts > latest[0]):
            latest = (ts, replies, max(max_page, page))
        for m in messages:
            if m["id"] in seen:
                continue
            seen.add(m["id"])
            by_page.setdefault(page, []).append(m)
    for msgs in by_page.values():
        msgs.sort(key=lambda m: m["id"])
    pages = sorted(by_page)
    all_msgs = [m for p in pages for m in by_page[p]]
    first, last = all_msgs[0]["date"], all_msgs[-1]["date"]
    own = sum(1 for m in all_msgs if m["nick"] == AUTHOR_NICK)
    ts, replies, pages_total = latest
    as_of = datetime.strptime(ts[:8], "%Y%m%d").date()
    pages_total = max(pages_total, (replies + PER_PAGE) // PER_PAGE)
    page_list = ", ".join(f"{a}–{b}" if a != b else str(a) for a, b in archived_runs(pages))

    lines = [
        "---",
        f"thread: {TID}",
        f'title: "{title}"',
        f'forum: "{FORUM}"',
        f"started: {first.date()}",
        f"last_archived_message: {last.date()}",
        f"source: sql.ru/forum/{TID}",
        f"archive: {archive_of[1]}",
        f"pages_total: {pages_total}",
        f"messages_in_thread: {replies + 1}",
        f"counted_on: {as_of}",
        f"pages_archived: {len(pages)}",
        f"messages_total: {len(all_msgs)}",
        f"author_messages: {own}",
        f"notes: ../en/{NAME}.md",
        "---",
        "",
        f"# {title}",
        "",
        f"Тред форума «{FORUM}» на sql.ru (сайт закрыт в 2022 году), начатый автором блога ({AUTHOR_NICK}) "
        f"{first.day} {MONTH_GEN[first.month]} {first.year} года. Из этого треда вырос блог «Технологическая "
        f"сингулярность». К снимку от {as_of.day} {MONTH_GEN[as_of.month]} {as_of.year} года в нём было "
        f"{replies + 1} сообщений на {pages_total} страницах; с августа 2017 года форум был закрыт для гостей, "
        f"и веб-архив успел сохранить только страницы {page_list}. Здесь все сохранившиеся сообщения, автора и "
        f"читателей, приведены полностью, в хронологическом порядке, по страницам. Цитаты оформлены как "
        f"`>` с ником цитируемого; ссылки на sql.ru оставлены текстом, кроме страниц, сохранённых в архиве.",
    ]
    prev = 0
    for page in pages:
        if page > prev + 1:
            lines += ["", missing_note(prev + 1, page - 1)]
        prev = page
        snapshot = re.search(r"/web/(\d{8})", archive_of[page]).group(1)
        lines += ["", f"## Страница {page} (архив: [снимок {snapshot[:4]}-{snapshot[4:6]}-{snapshot[6:]}]({archive_of[page]}))"]
        if len(by_page[page]) < PER_PAGE and page < pages_total:
            lines += ["", f"*В снимке на странице {len(by_page[page])} сообщений из {PER_PAGE}: тогда она была "
                          f"последней, следующие сообщения в архив не попали.*"]
        for m in by_page[page]:
            header = f"**{m['nick']}** (автор)" if m["nick"] == AUTHOR_NICK else m["nick"]
            lines += ["", f"### {m['date']:%Y-%m-%d %H:%M} · {header}", ""]
            subject = m["subject"]
            if subject and not subject.startswith("Re:") and subject != title:
                lines += [f"**{subject}**", ""]
            lines.append(to_markdown(m["body"]).strip() or "*(пустое сообщение)*")
    if prev < pages_total:
        lines += ["", missing_note(prev + 1, pages_total)]
    stats = {"pages": len(pages), "messages": len(all_msgs), "own": own, "first": first, "last": last}
    return "\n".join(lines) + "\n", stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--cache", type=Path, help="folder for the raw archived pages (reused if present)")
    args = ap.parse_args()
    target = args.root / "sources" / "garya" / "sqlru" / f"{NAME}.md"
    if target.exists() and not args.force:
        print(f"skip  {target.relative_to(args.root)} (already imported, use --force)")
        return 0
    thread_links()
    sources = []
    for page, ts, url in PAGES:
        sources.append((page, ts, url, load(ts, url, args.cache)))
        print(f"page {page:3d}  {ts}")
    text, stats = build(sources)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {target.relative_to(args.root)}: {stats['pages']} pages, {stats['messages']} messages "
          f"({stats['own']} by {AUTHOR_NICK}), {stats['first']:%Y-%m-%d} – {stats['last']:%Y-%m-%d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
