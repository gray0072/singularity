# AGENTS.md

Instructions for AI agents and human authors working in this repository. The structure and conventions are
specified in [SPEC.md](SPEC.md); this file covers **how to write**.

## 1. What this repository is

The series **"Campfire Dialogues"** (*«Диалог у костра»*) consists of popular-science essays on the
technological singularity. It was started in 2011–2012 on the sql.ru blog *«Технологическая сингулярность»*
by **Андрей Гордиенко** (Andrey Gordienko, **Garya**; [proza.ru/avtor/garya](https://proza.ru/avtor/garya)):
15 articles and a long trail of debates in the comments. sql.ru closed in 2022; the blog is kept in
[`sources/garya/sqlru/`](sources/garya/sqlru/) and the Wayback Machine. Never link to sql.ru itself: give its
addresses as plain text and link to the archive or to the copies here. The blog was public and the site is
closed, so the posts and all the comments under them are kept here in full. We continue the series, staying as
close as possible to his ideas, logic and voice, but **he is the author of articles 01–15 only**: never present the
continuation as his. Articles 16–32 were written by **Claude Opus 5.5**, an AI model made by Anthropic, imitating
his style and method. Article 33 onwards (Part VI, the cycle "Just Chatter") is written by **Claude Fable 5.2**,
also made by Anthropic, in the same manner.

Before writing anything, read:

1. [`sources/garya/en/author-profile.md`](sources/garya/en/author-profile.md) — who the author is and how he thinks.
2. The notes in [`sources/garya/en/`](sources/garya/en/) for the articles your text builds on, especially their
   *Key theses* and *The author in the comments* sections.
3. The previous article of the series in `ru/`, and its page on sql.ru with the comments under it in
   [`sources/garya/sqlru/`](sources/garya/sqlru/) (Russian originals). For the origins of an idea, the forum thread
   the blog grew out of (2009–2017):
   [`2009-09-15-apocalypse-scenario-thread.md`](sources/garya/sqlru/2009-09-15-apocalypse-scenario-thread.md) and its
   note in `sources/garya/en/`.
4. For his life experience, humour and narrative voice: his prose in [`sources/garya/proza/`](sources/garya/proza/)
   and its notes (`sources/garya/en/proza-*.md`).

## 2. Languages and translation

- **English is the primary language**: repository docs, README, metadata, and new articles by default.
- **English files are English only**: no Russian words in English pages and READMEs; give names and titles in
  translation (Andrey Gordienko, the blog *Technological Singularity*, a link labelled "Russian"). Russian appears
  only where the instruction is about Russian text (the glossary, style quotes, quotes from the originals in notes).
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

- The continuation starts at `16`. Articles 16–45 are written (each with a `part` and a `builds_on` list in
  `en/` and `ru/`); the next free number is `46`. The arc of 16–32: I. Re-examining the foundations
  (16–20), II. Machines today (21–23), III. Economy and people (24–26), IV. The transition and after (27–30,
  ending with Andrey's dated forecasts for the autumns of 2031, 2036 and 2041), V. The new keeper (31: an essay in
  which the model that wrote the continuation speaks in its own voice; 32: a fantasy set in the autumn of 2041, in
  which the AI doubles of Andrey and Oleg check the forecasts). Part V has `form: essay` / `form: fantasy`; it is
  the only place where the campfire form is left. A continuation article is marked `continuation: true` and listed
  in the *Continuation* block of every table of contents.
- **Part VI, "Just Chatter"** (*«Просто трёп»*, from `33`), is a new cycle written by Claude Fable 5.2; its plan,
  evening by evening, is [`sources/next-evenings.md`](sources/next-evenings.md) (Russian version: `next-evenings.ru.md`). The campfire
  form is kept. It opens on the first warm evening after the winter of article 30: Oleg comes with a paper
  notebook, sets the topics himself and forbids the word "singularity" (whoever says it first goes for firewood).
  Every evening starts from a question off the topic, the mountain shows no earlier than the middle and is not
  named first by Andrey, and at the end Oleg puts a tick "again" in the notebook. Written: 33–45.
- **The series is open.** Nobody says goodbye at the end: the evenings stop "until the needles move". The next
  evenings (planned for about 2028) check the dated marks of articles 27–30 honestly, one by one, as article 16
  checked the 2011 forecasts, and add new marks with dates and odds. They may be told by Andrey and Oleg, or by
  their AI doubles from article 32. The events of 32 are invented: when real data arrive, the real data win.
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
- New articles are not attributed to the original author. Their footer says that Andrey Gordienko did not write
  them and names the model that did (16–32: Claude Opus 5.5; 33 onwards: Claude Fable 5.2; both by Anthropic): they
  continue his series and method.

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
   Give the evening 1–3 figures where a picture carries the argument (a scheme drawn in the ash, a curve, a
   chart of the figures used): draw them in [`tools/figures.py`](tools/figures.py), which writes the English
   SVG and its `.ru.svg` variant from one function, and put each right after the replica it illustrates.
8. **In the same commit**, update the front matter (`status`, `published`, `tags`, `builds_on`), the status lines of
   all three tables of contents, the glossary for new terms, and `sources/continuation-notes.md`.
9. **The user is a native Russian speaker and proofreads the translations.** When the user says an
   article has been proofread, set its Russian `status` to `reviewed`.

## 5. Working rules

- Conventions for files, front matter, images and tables of contents: [SPEC.md](SPEC.md). Follow them exactly.
- The author's original texts (articles, comments, prose) are kept in Russian exactly as written; they are
  imported by the scripts in `tools/` (SPEC §5). Never edit them silently: editorial fixes are separate commits.
- English analysis and translations of source material go to `sources/garya/en/`. Readers' comments are kept in
  full in `sources/garya/sqlru/` (public posts on a site closed in 2022); in notes and articles they are paraphrased,
  without names.
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
| зубчатая граница | jagged frontier | the uneven edge of a machine's domain logicalities: above humans in some domains, below a child in neighbouring ones |
| инструментальная конвергенция | instrumental convergence | subgoals that follow from almost any goal (keep running, get resources); a machine's wants that nobody set |
| взлом вознаграждения | reward hacking | reaching the reward by the shortest road instead of the intention behind it; machines do it with our rewards, people with nature's |
| согласование (ИИ) | alignment (of AI) | tuning a machine's goals to human values; in the series, the 1978 amplifier of wants turned on machines |
| стоимость обучения | cost of learning | the price of making a person fit for the technosphere's world; paid anew by every generation, once by a machine |
| отметка (прогноза) | mark | a dated, checkable forecast with odds ("below half by the autumn of 2036, two to one"); introduced in 27–30 |
| двое часов | two clocks | the fast clock of the technosphere (the speed of copying) and the slow clock of people (generations, laws, habits); forecasts are made with both (32) |
| катастрофическое забывание | catastrophic forgetting | a network taught something new loses the old at once, because both are written into the same connections (33) |
| проигрывание (опыта) | (experience) replay | running stored experience through the network again, mixed with the new; what the brain does in sleep and what engineers gave the machine (33) |
| сравнительное преимущество | comparative advantage | Ricardo's theorem: even the weaker party is worth hiring at some price; in the series, it promises that such a price exists, not that it pays for the feed (34) |
| диссипативная структура | dissipative structure | Prigogine's term: an order that exists only while a flow passes through it; the cells in a heated pot, a flame, a living body (35) |
| препятствие (для потока) | obstacle (to a flow) | what stands in the way of a flow from hot to cold and makes it organise; the Earth is a "high-class obstacle" between the Sun and the cold sky; where obstacles come from is left open (35) |
| эффект мышеловки (транзистора) | mousetrap (transistor) effect | a small outlay of energy turns a larger flow; for the author, the condition under which evolution goes on (35) |
| метка игры (игровой сигнал) | play label (play signal) | what marks a move as play: the wolf's bow, the rat's chirp, the ape's panting, our laughter; it tells the pack that mistakes are cheap here (36) |
| премия за найденную ошибку | bonus for a mistake found | mirth, in the hypothesis of Hurley, Dennett and Adams: what the brain pays itself for a wrong guess caught in its own picture of the world while it is still cheap; a joke is a sweet made for that bonus (36) |
| волна сверхприбыли | wave of extra profit | the temporary gain of the first owner who replaces human labour with a machine, until the market catches up; the author's answer to Ricardo, "right globally, wrong locally" (the comments under 06; 37) |
| целое (синергетический эффект) | the union (synergy effect) | what people and machines put together make beyond the sum of their parts; profit or loss is what is left of that difference in the owner's line; for the author, the biggest thing Marx left out (37) |
| прикормленное место | baited spot | customers fed below cost until the habit stays; it remains baited whoever sits on the bank next (37) |
| созидательное разрушение | creative destruction | Schumpeter's term (1942): the new firm kills the old one; in the series, the same river described from the people's bank (37) |
| кислородная катастрофа | Great Oxidation Event (oxygen catastrophe) | about 2.4 billion years ago free oxygen, the production waste of bacteria that split water, came into the air; in the series, the precedent of a new form of life that changes the environment without fighting anyone (38) |
| анаэроб | anaerobe | a living thing that does without oxygen and often dies of it; the former masters of the planet, now in niches: silt, the gut, a sealed jar (38) |
| ниша | niche | the first of the fates of former masters: everything is kept as it was, at the price of the planet's surface and of the say in what the environment will be (38) |
| обмен веществ (техносферы) | metabolism (of the technosphere) | what a form of life eats, builds itself from and throws out; the economy is the technosphere's metabolism, and ecology is what that metabolism does to the environment of the form of life before it (38) |
| ложная тревога и пропуск | false alarm and miss | the two mistakes of anything that decides on incomplete data; one screw sets both: fewer of the one means more of the other, and the prices decide where it stands (39) |
| принцип дымового датчика | smoke detector principle | Nesse's term: a defence that mostly goes off for nothing may be tuned exactly right, because a miss costs far more than a false alarm; in the series, why the correlator is tuned for false alarms (39) |
| суеверие | superstition | a link invented by a learner that links what came together before it knows why; the price of the ability to learn, paid by the pigeon, by us and by the machine (39) |
| общая причина | common cause | two events that go together with no road from one to the other, because both follow from a third: the round date behind the dream and the call; "two cocks crow at dawn, and neither woke the other" (39) |
| эффект Умного Ганса | Clever Hans effect | the right answer for the wrong reason: the horse that read its questioner, the program that learned the stamp in the corner of the photographs (39) |
| закон Клайбера | Kleiber's law | an animal's energy use goes as its weight to the power of about three quarters: ten thousand times heavier, a thousand times more energy; the larger the animal, the thriftier and slower each gram of it (40) |
| рост медленнее / быстрее собственного размера | growth slower / faster than its own size | the two kinds of 40: where the gain lags behind the size (an animal, a firm) growth bends to a ceiling; where the gain runs ahead of the size (the network of meetings over a town's pipes) growth has to speed up (40) |
| сингулярность за конечное время | finite-time singularity | the physicists' ordinary term for the point where a formula goes to infinity on a finite date; in the 2007 paper on cities it marks the wall that growth faster than size runs into unless an invention moves it, each one sooner than the last (40) |
| период полураспада фирмы | half-life of a firm | about ten years for publicly traded companies, whatever the trade and whatever the age: a firm does not age, "it dies like a glass in the kitchen", and mostly by being bought or merged (40) |
| чизкейк для ушей | cheesecake for the ear | Pinker's phrase (1997) for music: a sweet that presses buttons made for other work; the series agrees by half and asks which button: the main one, "the forecast came true" (41) |
| отмеренная доза обмана | measured dose of deceit | what stands between noise (nothing is guessed) and a dripping tap (everything is guessed): a tune mostly comes true and trips the listener gently; beauty as predictability with that dose (41) |
| прогноз, сделанный общим | a forecast made common | a beat: a hundred heads forecast the same instant and a hundred backs pull as one; the glue of song is boiled from the same button as its sweetness (41) |
| две выплаты (за звук и за цену) | two payments (for the sound and for the price) | what we value in a song: the sound, which works whoever made it, and the price somebody paid for it, which works only when one knows who paid; they used to come in one envelope (41) |
| расписка | receipt | a song as proof of a price paid now, by this person, for you: the mother at the cradle, the choir that has spent many evenings together; "a receipt that anybody can print is not a receipt" (41) |
| десоциализация, одиночество в толпе | desocialisation, loneliness in a crowd | the author's 2017 terms (after Bill Joy): progress removes people's need for one another; in 41, the road from the choir to the earphones |
| симбиогенез | symbiogenesis | a new kind of living thing made by one cell taking another in and not digesting it (Mereschkowski, 1905; Margulis, 1967); in the series, the only optimistic scenario with a precedent: merging does happen (42) |
| жилец и хозяин | lodger and host | the one taken in and the one that took it in; the lodger is kept for one job that the host cannot do itself, and for as long as it cannot: "two billion years are not a guarantee, they are the term of a contract" (42) |
| выжить как функция, а не как существо | to survive as a function, not as a being | the fate of the swallowed bacterium: 37 genes out of thousands, the host's setpoints instead of its own, no name but that of its job; "what did not survive is the one who wanted for itself" (42) |
| не берегут | not guarded | how the swallowed one loses what it had: nothing is taken away; a gene (a trade, a memory) that the job does not need breaks, and nothing keeps it in order; Oleg's supply department, "not needed twice" (42) |
| переезд чертежей | the move of the drawings | the genes of the lodger moving to the host's nucleus, still going on; in the series, what people have written down moving into the machines: "once a drawing works from there, the copy at home is not needed" (42) |
| органелла | organelle | the second row of the table of fates of former masters, after the niche: "kept the job, paid with everything else, while the job is needed" (42) |
| арифметика родства (правило Гамильтона) | the arithmetic of kinship (Hamilton's rule) | helping pays when the relative's gain, multiplied by the share of common drawings (genes), is larger than one's own loss (1964); with a share of one (the cells of a body, the copies of a program) nobody has anything of its own to bargain for (43) |
| память о долгах | memory of debts | the second thing cooperation can rest on, for those who are not kin: "as you did to me, so I do to you"; it needs meeting again, recognising and remembering, and reaches about as far as a village (some 150 faces) (43) |
| протезы (памяти о долгах) | prostheses (of the memory of debts) | what people put where that memory does not reach: reputation, money, law, conscience ("the gatehouse moved inside"); they work and cost up to half the economy (43) |
| охрана (полиция яиц, проходная) | the guard (the egg police, the gatehouse) | what stands on top of kinship, because copying makes mistakes: the order to die and the patrols in a body, workers eating one another's eggs in a hive; cancer is the cell the guard missed (43) |
| запах дома (критерий «свой — чужой») | the smell of home (the test of one's own) | the simple rule by which a worker ant tells a sister; it can be forged (the Amazon ants' slaves) and can come out the same for everybody (the Argentine ant); copies of a machine can check kinship letter for letter (43) |
| гиперсоциальность | hypersociality | the author's 2011 term for a property of the mature technosphere, promised and not written; in 43: the copies of one machine are full kin by construction, so they need no wage, fine or conscience; "not a virtue of the heir but arithmetic" |
| нода | node | the author's 2013 word for a member of a network mind; a human is "a transitional form of node", with no firm test of who his own are (43) |
| тяжёлый образ | heavy image | an image used for decades, whose significance coefficient has grown so that a new one cannot shift it; from inside it cannot be told from the truth: both feel like "obviously" (44) |
| ум стареет от наполнения | a mind ages by filling | not wear: for a mind that judges by the average of what it has seen, the n-th fact weighs 1/n; the price of not forgetting, the same screw as the false alarm and the miss of 39, and it turns by itself with every fact added (44) |
| принцип Планка (от похорон к похоронам) | Planck's principle (from funeral to funeral) | a new truth wins not by convincing its opponents but because they die and a generation grows up that is used to it; in 44: too strong about people (they do change their minds), right about fields (outsiders enter after a star's death) |
| уборщик общей памяти | the cleaner of the common memory | death: what forgetting does in one head (19, 33) death does in the memory of a society, because nobody can write off a heavy image in another man's head: "it leaves together with the head" (44) |
| кафедра, с которой никогда не уходят | a chair that is never vacated | an immortal mind; "a chair that is taken need not be defended": outsiders are mostly not driven away, they do not come (44) |
| потеря пластичности | loss of plasticity | a network taught task after task learns each new one worse, until it learns no better than the simplest network (2024); the other end of the screw from catastrophic forgetting (33) (44) |
| маленькие похороны | small funerals | the cure for loss of plasticity: at every step the least used units are wiped and started from nothing; what a body does with its cells (44) |
| дневник (опыта) | diary (of experience) | what is kept when a network is wiped and a new one is raised on it: "the head is changed and the notebook is left"; with people most of it leaves together with the head (44; what passes on is 45) |
| барьер Вейсмана | Weismann's barrier | the body is built from the line of germ cells and nothing goes back: what a body earns has no road into the drawings, "neither a translator nor an address"; in the series it stands where experience and heredity are kept in different places and written in different languages, so a bacterium and a machine do not have it (45) |
| извещение об изменении | change notice | the plant's paper by which the experience of the shop gets into the drawing; a body has no such form; selection is a change notice "written by the deaths of those who had not learned"; people were the technosphere's change notice, "and the narrowest place in it" (45) |
| 39 бит в секунду | 39 bits a second | what human speech carries, about the same in every language measured (2019): fast languages put less into a syllable; the width of the road by which culture passes experience on (45) |
| соломинка (три узких места) | the straw (three narrow places) | culture as Lamarck's way round the barrier, narrow in three places: the mouth knows only a part of what the hands know, speech carries 39 bits a second, and the pupil has to grow the skill anew; "a book keeps the record, not the skill" (45) |
| неявное знание | tacit knowledge | "we know more than we can tell" (Polanyi, 1966): the cyclist's hands know the push to the right before a left turn, and "the mouth was never told"; Semyonych's whole lecture on bearings was "it sings wrong" (45) |
| слепок знаний | a cast of knowledge | the author's 2011 term: the coefficients of a trained network rewritten into another of the same structure, address by address; in 45: the weights are copied as a file, and only into a head of the same structure, which is why no human head can be copied |
| дистилляция | distillation | a big network teaching a small one by giving not only the answer but how sure it is of every other answer (2015); school between machine heads of different structure: "'it sings wrong', in figures" (45) |
| три дороги наследственности | three roads of heredity | the drawings (Darwin: the design passes, a correction is paid for with funerals), speech and school (Lamarck through a straw: a part of the experience, twenty years on every head), the copy (Lamarck whole: all the experience, in minutes); the third alone is enough for the difference in speeds (45) |
| Дарвин плюс Ламарк | Darwin plus Lamarck | the author's 2025 formula; there Lamarck stood for the keeping of variety, which is Ashby's law (corrected openly in 45); kept in another sense: Darwin is the search (many different ones and a way to discard), Lamarck is the transfer (what is found is handed on whole); "a copy with no search is a stop" |
| двойник (ИИ-двойник) | (AI) double | a machine that carries the images of one person (texts, letters, voice) and speaks as him; in 32, the doubles of Andrey and Oleg |

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
- **Check Russian Wikipedia titles through the API, not with a raw Cyrillic URL.** In Git Bash `curl` with unencoded
  Cyrillic in the address answered `200` (the main page) for pages that do not exist (`Принцип_Планка`,
  `Критический_период`). One request to the API checks a whole list and does not hit the rate limit:
  `https://ru.wikipedia.org/w/api.php?action=query&format=json&redirects=1&titles=A|B|C` (percent-encoded, from
  Python); a page that does not exist comes back with `"missing"`.
- **Russian Wikipedia rate-limits link checks.** A fast loop of requests gets `429`. Check pages one by one with a
  pause of a few seconds and a `User-Agent` header. Publishers (doi.org, Science, PNAS, CDC) often answer `403`
  to scripts; that does not mean the link is broken.
- **Python on Windows prints Cyrillic only with UTF-8 output.** Run it as `PYTHONIOENCODING=utf-8 python ...`,
  or a script that prints Russian titles fails with `UnicodeEncodeError`.
- **Never rewrite a file with Windows PowerShell 5.1 `Get-Content`/`Set-Content`.** It reads UTF-8 as the ANSI code
  page and writes the mangled text back: every Cyrillic letter, `≈` and `§` in `tools/figures.py` turned into
  mojibake (repaired by encoding the text back to cp1252 and decoding as UTF-8). Edit with the file tools or Python.
- **Check a figure by looking at it.** Headless Edge renders an SVG to PNG:
  `msedge --headless=new --screenshot=out.png --window-size=800,600 file:///.../images/<name>.svg` (Edge lives in
  `C:\Program Files (x86)\Microsoft\EdgeCore\<version>\`). Overlapping labels are invisible in the SVG source.
- **Two-line labels in a table figure need a taller row.** In `dated-forecasts` a two-line row name ran into the
  italic "now" line under it until the row height went from 50 to 58.
