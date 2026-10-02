# AGENTS.md

Instructions for AI agents and human authors working in this repository. The structure and conventions are
specified in [SPEC.md](SPEC.md); this file covers **how to write**.

## 1. What this repository is

The series **"Campfire Dialogues"** (*«Диалог у костра»*) consists of popular-science essays on the
technological singularity. It was started in 2011–2012 on the sql.ru blog *«Технологическая сингулярность»*
by **Андрей Гордиенко** (Andrey Gordienko, **Garya**; [proza.ru/avtor/garya](https://proza.ru/avtor/garya)):
15 articles and a long trail of debates in the comments. The originals are published here with the author's
permission. We continue the series, staying as close as possible to his ideas, logic and voice.

Before writing anything, read:

1. [`sources/garya/en/author-profile.md`](sources/garya/en/author-profile.md) — who the author is and how he thinks.
2. The notes in [`sources/garya/en/`](sources/garya/en/) for the articles your text builds on, especially their
   *Key theses* and *The author in the comments* sections.
3. The previous article of the series in `ru/`, and its page on sql.ru with the author's comments under it in
   [`sources/garya/sqlru/`](sources/garya/sqlru/) (Russian originals).
4. For his life experience, humour and narrative voice: his prose in [`sources/garya/proza/`](sources/garya/proza/)
   and its notes (`sources/garya/en/proza-*.md`).

## 2. Languages and translation

- **English is the primary language**: repository docs, README, metadata, and new articles by default.
- Content is translated into several languages, **starting with Russian** (`ru/`). Articles 01–15 were
  written in Russian. They are the originals, and the English versions are translations of them.
- Every article exists in every language folder under the same file name. Translations are made from the
  original (`original_lang`), never from another translation.
- Translate the meaning and the voice, not the words. Keep the structure: the same evening, the same replicas
  in the same order, the same examples, the same bold conclusion, the same links (pointing inside the target
  language folder) and images.
- Keep the characters' names: Андрей → **Andrey**, Олег → **Oleg**.
- Use the glossary (§6) for terms; a new term goes into the glossary in the same commit.
- Russian typography: em dash `—` for dialogue, «ёлочки» for quotes in new Russian text. English: em dash
  for interrupted speech, regular quotes for dialogue paraphrase; dialogue lines still start with `— `
  (keeps the files parallel across languages).
- After translating set `status: translated`; only a native speaker sets `reviewed`.

## 3. Style: a popular-science story told as a dialogue

Write in a **популярно-научный, научно-художественный** style, the way the original articles are written.
Each article is an essay told as a conversation, with real arguments and real sources. Follow the original
articles as closely as possible. In practice:

**Form**

- Each article is **one evening by the campfire**: Andrey and Oleg meet, talk, and part until tomorrow.
  The scene is sketched in one or two touches and never more: the flames, branches thrown into the fire,
  a mosquito slapped on the forehead, a glance at a watch. No landscape descriptions.
- Andrey speaks for the author. He calmly and patiently leads the conversation with questions. Oleg is
  an intelligent sceptic who trusts mainstream science and common sense. He objects, jokes, squints slyly,
  and voices the reader's doubts and the real objections of the blog's commenters. Oleg is never a straw man:
  his objections are the strongest ones available.
- The text is almost all dialogue. The author's remarks are short stage directions: *усмехнулся Андрей*,
  *прищурился Олег*, *Андрей выдержал паузу*. Replicas are short and alternate quickly. Andrey's longer
  explanations come only after Oleg has asked for them.

**Movement of an evening**

1. Opening: Oleg arrives with a question, or Andrey opens with an image. The topic is named and tied to the
   singularity, often with a link back to a previous evening.
2. Socratic descent: a chain of simple questions on everyday examples (a mosquito, a cobblestone, a bacterium,
   a Venus flytrap, chess, a lathe) that Oleg answers "obviously" — until the obvious answers contradict each
   other.
3. Exposure of anthropocentrism: Andrey shows that the contradiction comes from putting the human being at the
   centre. He removes the special status of humans and the reasoning runs again, now without the contradiction.
4. Evidence: facts, numbers and links to sources (encyclopedias, news, scientists' forecasts) that support the
   new view. Science is respected; it is the scientists' anthropocentric blind spots that are criticised.
5. Recap: Andrey fixes the result. *«Давай на сегодня закончим, зафиксировав…»* The key conclusion is set in
   **bold**, sometimes as a numbered list of 1–3 theses.
6. Teaser and parting: what tomorrow's topic is, often prompted by Oleg's last doubt, then a short
   *«Ну, до завтра. — Пока.»*

**Voice** (details and examples: [`author-profile.md`](sources/garya/en/author-profile.md))

- Logic above all: every step follows from the previous one and from earlier articles. Conclusions are
  stated plainly, even when they are uncomfortable. The author prefers "bitter truth to sweet lies".
- Down-to-earth, vivid metaphors for abstract ideas: weeding anthropocentrism out of the mind like weeds,
  pulling it out like a wisdom tooth with crooked roots, separating the flies from the cutlets.
- Calm, friendly, slightly ironic tone; warm humour between the friends. No preaching, no pathos,
  no exclamation marks in Andrey's mouth.
- Andrey admits limits and open questions, and postpones what belongs to a later evening
  (*«это мы обсудим, когда…»*) instead of rushing ahead.
- The same core terms are used consistently (see §6); a new term is introduced by an example first and
  defined second.
- Characteristic reasoning moves: the symmetry test (if a man may call a spade his tool, the spade may call the
  man its tool), "the question is badly posed" for false dichotomies, the same logic at every scale of nested
  systems, rough arithmetic with real figures, "of which system?", "logic only two moves deep, yet reason does
  not go there".
- No villains and no remedies: nobody planned the outcome, everyone acts with good intentions on short logic;
  the conclusion is stated calmly — *«— Мрачновато. — Зато объективно.»*

**Length**: an evening is about 1,500–4,500 words; the introduction can be shorter.

## 4. Continuing the series

- The continuation starts at `16`. Planned evenings 16–30 have stubs with abstracts, a `part` and a
  `builds_on` list in `en/` and `ru/`; the next free number is `31`. The arc: I. Re-examining the foundations
  (16–20), II. Machines today (21–23), III. Economy and people (24–26), IV. The transition and after (27–30, the
  last evening closes the series). A continuation article is marked `continuation: true` and listed
  in the *Continuation* block of every table of contents.
- New articles must be consistent with all earlier conclusions and with the
  author's positions in [`sources/garya/`](sources/garya/). If something is developed beyond what the
  author said, it must follow from his logic; never contradict him silently.
- The *Open threads* sections of the notes list topics the author promised or left unanswered — that is the
  natural agenda for new evenings.
- Leave out current party politics, religion and geopolitics (for example the Crimea digression in his later
  prose). They are not part of the series' argument; the series argues from the laws of nature, not from sides.
- Facts written after 2012 (AI progress, economics, demography) may and should be used as fresh evidence,
  with sources, in the same manner as the original articles used 2011 news.
- Some of the author's dated forecasts (human-level AI by the end of 2018, population growth stopping around
  2018) did not come true as stated. Never hide this; let Andrey face it honestly, by his own method — see
  *Handling his forecasts* in [`author-profile.md`](sources/garya/en/author-profile.md).
- Oleg's objections are best taken from the real ones: every note has a section *The author in the comments*
  with readers' objections and the author's answers. Andrey's answers must agree with those.
- New articles are not attributed to the original author: they continue his series and method; the byline,
  if any, is the repository's.

### Writing a continuation evening, step by step

1. **Read the record of what is already written.** [`sources/continuation-notes.md`](sources/continuation-notes.md)
   lists, for every written continuation article, what it established, which facts and images it used and what it
   left for later. Do not contradict it, do not reuse its examples as new, and keep the promises it records.
2. **Read the stubs of the neighbouring articles**, not only your own. A topic that belongs to a later stub is
   touched in a sentence and deferred to that evening (*«это отдельный вечер»*), never developed early.
3. **Open with the previous evening's last doubt** or with what its teaser promised, and close with a teaser that
   matches the next stub's abstract.
4. **Carry the argument with the author's own images first.** Search his comments in `sources/garya/sqlru/` for the
   topic (`grep` the Russian key words) and reuse his examples: they make the voice his.
5. **Give Oleg the strongest current objection**, including the best science against the author (in 17, the Bell
   experiments). Andrey answers it honestly and says plainly where proof ends and his axiom begins.
6. **Check every fact before using it**, with a primary source where possible, and state figures with their year.
   Verify the details of famous experiments too (who, when, what exactly was measured).
7. **Write the English original, then the Russian translation**, and compare the number of dialogue lines.
8. **In the same commit**, update the front matter (`status`, `published`, `tags`, `builds_on`), the status lines of
   all three tables of contents, the glossary for new terms, and `sources/continuation-notes.md`.
9. **The user is a native Russian speaker and proofreads the translations.** When the user says an
   article has been proofread, set its Russian `status` to `reviewed`.

## 5. Working rules

- Conventions for files, front matter, images and tables of contents: [SPEC.md](SPEC.md). Follow them exactly.
- The author's original texts (articles, comments, prose) are kept in Russian exactly as written; they are
  imported by the scripts in `tools/` (SPEC §5). Never edit them silently: editorial fixes are separate commits.
- English analysis and translations of source material go to `sources/garya/en/`. Readers' comments (other
  people's texts) are only quoted briefly or paraphrased, without names.
- Images go to the shared [`images/`](images/) folder, are reused across articles and languages, and are
  registered with their license in [`images/README.md`](images/README.md).
- Any change to the list of articles or their status updates [README.md](README.md) and every
  `<lang>/README.md` in the same commit.

## 6. Glossary

| Русский | English | Meaning in the series |
|---------|---------|-----------------------|
| Диалог у костра | Campfire Dialogues | name of the series |
| технологическая / эволюционная сингулярность | technological / evolutionary singularity | two views of one process: the evolution of matter moving to a new carrier |
| антропоцентризм | anthropocentrism | the view that humans are the centre and purpose of everything; for the author, humanity's oldest and least visible error |
| разум | mind | a system's ability to process information and act logically; a matter of degree, not a property only humans have |
| интеллект | intelligence | measurable capability of a mind; also a matter of degree |
| логичность | logicality | how logical a system's behaviour is |
| ареал-логичность | domain logicality | logicality of a system within one domain (e.g. chess) |
| совокупная логичность | aggregate logicality | the union of all domain logicalities of a system |
| инициатива | initiative | the source of a system's motion and activity; for the author it comes from the laws of nature, not from the mind |
| воля | will | — |
| эволюция материи | evolution of matter | the global trend from simpler to more complex forms |
| техносфера | technosphere | all technology taken as an active participant in evolution and the economy, not a passive tool |
| техногенная жизнь | technogenic life | the new form of life that follows biological and human-made (anthropogenic) life |
| НТП (научно-технический прогресс) | scientific and technological progress (STP) | — |
| средства производства | means of production | Marx's term; in the series, the technosphere |
| добавочная стоимость | surplus value | in the series, created by the technosphere |
| производительность труда | labour productivity | — |
| передний край эволюции | leading edge of evolution | the place of the most complex, fastest-developing form of matter |
| хотелки / нехотелки | wants / aversions | desires and emotions that steer reason; the author's colloquial term, kept as a term |
| уставка | setpoint | a want seen as the value a control system keeps; set by nature, it rises once reached |
| сторожевой таймер | watchdog | an emotion that forces a decision when wants balance, then defends it; conscience is a late watchdog |
| избирательная недальновидность разума | selective short-sightedness of reason | reason going blind exactly where wants block it |
| логика на два хода | logic only two moves deep | an obvious conclusion that reason still avoids |
| мышление | thinking | sequential inner speech through the "point of attention" |
| сознание | consciousness | a system's model of itself inside its model of the world; comes in degrees |
| квалиа | qualia | the felt side of experience; for the series, how the recognition of an image looks from inside the system (an axiom, not a proof) |
| образ | image | the unit of thought in memory; images compete for scarce memory, reproduce and evolve, a form of life with its own life cycle |
| коэффициент значимости | significance coefficient | the weight of an image in memory; used images grow heavier, unused ones are erased |
| платформа (разума) | platform (of mind) | the physical carrier that sets the ceiling of intelligence |
| носитель / источник разума | carrier / source of mind | humans and machines are carriers; nature is the source |
| динамическая система | dynamic system | any system; in the series, everything is one |
| жизненный цикл | life cycle | investment → birth → accelerating growth → decelerating growth → limit → ageing → death |
| порог вхождения | entry threshold | minimum investment for a system to be born |
| прибыль с оборота / норма прибыли | profit per turnover / rate of profit | what each cycle adds; sets the growth rate |
| доля ценности | value share | the part of a product's value created by people vs the technosphere |
| симбиоз / паразитизм | symbiosis / parasitism | the human–technosphere relation now / after the technosphere stops needing people |
| силы притяжения / сила сцепления | attraction forces / cohesion force | mutual interest of humanity and the technosphere |
| эмбриональная фаза | embryonic phase | the current stage of technogenic life |
| апоптоз человечества | apoptosis of humanity | humanity's programmed exit, timed to the technosphere's autonomy |
| сингулярность как процесс | singularity as a process | the crisis/maturity phase of a life cycle, stretched over decades |
| глобальный детерминизм | global determinism | the author's stance: no free will, no true randomness |
| случайность | randomness | lack of information in a local system; nature as a whole cannot lack information about itself |
| фатализм | fatalism | the belief that the outcome is the same whatever one does; unlike determinism, where one's actions are among the causes of the outcome |
| халява | freebie | what people get from the technosphere in exchange for developing it |
| лопатоцентризм | shovel-centrism | the mirror image of anthropocentrism, used to expose it |
| безлюдное производство | lights-out production | — |
| разумная космическая пыль | intelligent cosmic dust | the author's image of post-singular technogenic life |
| ПМСМ | IMHO | his habitual hedge; in English text, "I believe" |
| большая языковая модель | large language model | a neural network trained on humanity's texts; in the series, a machine that gains mind from accumulated knowledge |
| демографическая инерция | population momentum | population growth that continues for decades after fertility falls, because the generation having children is large |

## 7. Tooling notes for agents

Mistakes made while writing earlier articles. Avoid them.

- **Write article files with the file-writing tool, not a Bash heredoc.** A long Markdown text with quotes,
  apostrophes and parentheses broke a heredoc in Git Bash on Windows (`unexpected EOF while looking for
  matching '`), and the file was not written. Bash is fine for short edits (`sed`) and checks.
- **Read large files one at a time.** `cat` of several articles or notes at once overflows the tool output.
  Read the file directly, or extract only the sections you need (*Key theses*, *The author in the comments*,
  *Open threads*).
- **Fetch the page with the data, not the landing page.** The landing pages of the UN World Population
  Prospects and of IEA reports return no figures. Fetch the executive summary or the PDF of the report.
- **Check every Russian Wikipedia link before using it.** Some articles exist only in English (for example
  *AlexNet* and *Population momentum*). Check that each page returns 200 and fall back to the English page:
  `curl -s -o /dev/null -w "%{http_code}" "https://ru.wikipedia.org/wiki/<title>"`.
- **Sources update their figures.** A study's page can show a newer number than the one first reported
  (Stanford's figure for young workers grew from 13% to 19%). Phrase such figures so they stay true
  ("by more than a tenth, and the gap keeps growing"), or give the date of the figure.
- **Check the originals' numbers before reusing them.** Article 07 gives world GDP as 62,000 trillion dollars
  instead of 62 trillion. When a later evening uses such a number, Andrey corrects it openly.
- **Keep the two language versions parallel.** After translating, compare the number of dialogue lines
  (`grep -c "^— "`) in both files; it must match.
- **Russian Wikipedia rate-limits link checks.** A fast loop of requests gets `429`. Check pages one by one with a
  pause of a few seconds and a `User-Agent` header. Publishers (doi.org, Science, PNAS, CDC) often answer `403`
  to scripts; that does not mean the link is broken.
- **Python on Windows prints Cyrillic only with UTF-8 output.** Run it as `PYTHONIOENCODING=utf-8 python ...`,
  or a script that prints Russian titles fails with `UnicodeEncodeError`.
