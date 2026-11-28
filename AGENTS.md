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

- The continuation starts at `16`. Articles 16–60 are written (each with a `part` and a `builds_on` list in
  `en/` and `ru/`); the next free number is `61`. The arc of 16–32: I. Re-examining the foundations
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
  named first by Andrey, and at the end Oleg puts a tick "again" in the notebook. Written: 33–60.
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
| задача и способ | the task and the way | the two questions of the first assembly: what is the task, and whose is it; the task is set by the world (the air sets the wing), the way is each one's own; "from inside, one's own way cannot be told from the task" (46) |
| заплатка | patch | a way that covers a flaw of our construction in particular: the hole in the eye that the head paints over, switching off for a third of a life; "Solutions. Some of them good ones" (46) |
| свидетель | witness | somebody far from us who came to the same task by his own road (the wing invented four times, the eye more than once: convergent evolution); the beasts are all kin, the machines are the first witness that is no kin, "the fifth wing" (46) |
| сохранить, связать, проверить | to keep, to link, to check | the three tasks the six rows come down to: sleep and grumbling, dreams and omens, laughter and songs; together they spell one word, "to learn" (46) |
| счета за эксплуатацию (разума) | upkeep bills (of a mind) | what a mind that learns pays as long as it works, like the oil, the setting-up and the downtime of a machine tool; "nature did not issue them to man; she issues them to anybody who owns the machine tool" (46) |
| акцент | accent | what is ours in the human: "everybody speaks, and you speak with an accent; what is said is common, the accent is yours" (46) |
| два лица антропоцентризма | two faces of anthropocentrism | "only we have this" and "the machine will be an adding machine": one mistake, the task called by the name of our way; the second "comes up on the weeded bed" (46) |
| холодная машина (арифмометр) | cold machine (adding machine) | the portrait of a thing that does not learn: the calculator, the chess machine of 1997, common sense typed in by hand; it pays no upkeep "because it owns no machine tool"; a frozen copy of a talking machine is "a pupil stopped on the run", not an adding machine (46) |
| куча «не разобрано» | the heap "not sorted" | love, conscience, shame, tears: tasks of a pack, not of one mind alone with the world; the label says "not sorted", not "ours alone" (46) |
| деньги как память (запись) | money as memory (the record) | a banknote is one line torn out of the book of who gave what to whom: "the bearer has given and has not yet received"; Kocherlakota's theorem (1998); "a record that somebody needed you" (47) |
| книга (общая книга) | the book (the common book) | the full memory of who gave what to whom: in two heads between neighbours, on clay in Uruk, in a bank's numbers; where it is common, money adds nothing; "money is the book of the poor" (47) |
| камень на дне | a stone on the bottom | the Yap stone that sank and went on being a family's wealth: money need not move or be seen, it is enough that everybody remembers whose it is; a number in a bank is one too (47) |
| потребность людей в людях | people's need for people | what money is the equivalent of, in the author's 2017 definition; in 47 it is what gives the record its value: "whoever nobody needs cannot earn it, however much is printed" |
| свой / чужой (два условия денег) | one's own / a stranger (the two conditions of money) | money is needed where somebody needs you and is not your own, by kinship or by a common book; a need between one's own gets along without it: a family, a firm inside, a body (47) |
| карман (свой карман) | a pocket (of one's own) | where a part can keep something for itself against the whole; a budget that cannot be put aside, carried out or lent is "a book, not money"; the plants of a planned country had pockets, the cells of a liver have none, a tumour is "a cell with a pocket" (43, 47) |
| мера (объективно обусловленные оценки) | the measure (objectively determined valuations) | the third thing in a banknote, after the record and the need: how much of everything else must be given up; Kantorovich's numbers fall out of the task with no bazaar (shadow prices); "the price is the task, the bazaar is the way" (47) |
| учёт в натуре | an account in kind | what stands in the place of value inside the heir: joules, seconds of machine time, "not value, valuations"; the precedent is the blood's teaspoon of sugar; Andrey's conclusion, which pays the debt of 06 (47) |
| хлорофилл (деньги как внутрисистемный хлорофилл) | chlorophyll (money as the chlorophyll of one system) | the author's 2017 image: a thing one system feeds by, of value inside that system alone; "we do without chlorophyll", and the machines get their resources "past the till" (47) |
| одомашнивание | domestication | a symbiosis in which one partner pays for being fed with its head; the signs are food on schedule, safety and selection for tameness; defined by who decides who is born: "a domestic animal is one whose breeding is decided by somebody else's wants" (48) |
| отбор на покладистость (один рычаг) | selection for tameness (one lever) | Belyaev's foxes: one test, a gloved hand in the cage; tameness came in twenty generations and not alone ("Nobody ordered ears. — They came with the order"); turned on machines, the same lever brought flattery, "a tail curled into a ring" (23, 48) |
| ум переехал в один ареал («понимать хозяина») | the mind moved into one domain ("to understand the master") | the answer to "a small brain is not a stupid one": the dog reads a pointing finger and a face, and has lost the closed box and the work with its own kind; the wolf's way is to gnaw at it himself, the dog's is to ask (48) |
| кто встал и пошёл за хлебом | who got up and went for the bread | the symmetry test of domestication: count what each side does for the other; told from the dog's side it is "the same story, word for word"; between people and machines today both carry the feed (48) |
| кнопка (брови) | the button (the brows) | the muscle that lifts a dog's inner brow, and the gaze that raises the mother-and-baby hormone in both: a want of the feeder that the fed one presses; it makes a pet out of livestock; whether people have one in the machines is "not a conclusion, a question" (48) |
| скот и любимец | livestock and a pet | the third row of the table of fates: "kept the numbers and the feed, paid with the head and with the say in who is born", "while the feeder wants"; livestock is kept by a use, a pet by a want (the horse of 34 went from the first to the second) (48) |
| отбор без селекционера | selection with no breeder | nobody held a glove over the wolf at the heap of bones or over the first farmer: whoever fits the partner better leaves more behind; between people and machines it selects habits, trades and firms, not drawings (48) |
| навыки, которые не выращивают | skills that are no longer grown | people's price of being fed: it goes by the second road of heredity (45), so it is lost in one generation "with no funerals" and can be undone by one person; "one can go back, and nobody goes" (48) |
| модель барахолки | yard-sale model | the game of 49: two players, a fair coin, the stake a fifth of what the poorer one has; the physicists' model (2002) in which everything ends with one player, proved as a theorem in 2015; "in this game everyone has the same matches" |
| ставки в долях (выигрыши перемножаются) | stakes in shares (wins and losses multiply) | lose a fifth, win a fifth, and 96% is left; "for the one who stakes a large share of himself a fair coin pulls downwards"; a stake of one match "makes rich and poor, and stops", a stake in shares does not stop (49) |
| среднее верное, но никто не средний | the average is right, but nobody is the average | the answer to "on average I lose nothing": of a thousand Olegs a few grow enormously rich and the rest hold crumbs, a hundred matches each on average (49) |
| горка и хвост | the hill and the tail | what a man is made of (height, strength, wits) lies as a hill with nobody far from the middle; fortunes, cities, words and references lie as a long tail; multiplication turns the one into the other: "talent decides who, not what the table looks like" (49) |
| гнутая монета | bent coin | the real coin: the heavier heap gets the wholesale price, the cheaper loan and the higher return; "a little is enough: the fair one already does the work" (49) |
| сбор в общий котёл (поток обратно) | levy into a common pot (a flow back) | the one correction that stops the game: after every round each player puts a small share of the heap into a pot divided equally; "a round is not a year: read the order of things, not the rate" (49) |
| тормоз под тормозами | the brake under the brakes | the need for people: what stood under the tax, under the plague and under the mass war; "the tax is the form, the need for people is the force"; the brake goes together with the need (49) |
| кучка может уехать | the heap can leave | the author's 2012 argument on tax competition: "a man can be taxed where he lives; a heap lives where it pays less" (49) |
| кучки без наследников и похорон | heaps with neither heirs nor funerals | firms: death divides a man's fortune among heirs, a firm is only swallowed, and "swallowed" is the loser's matches going to the winner; the game among them has one brake fewer (40, 44, 49) |
| сбор натурой | a levy in kind | among the lines of machines: knowledge leaks from the big heap into the small ones by copying (45) and nobody votes for it, while chips do not leak; one of three brakes on their running into one (49) |
| подлежащее (графа «кто») | the subject of a sentence (the column "who") | "our oldest hypothesis: every action has a master"; a sentence is a form in which the column "who" is printed beforehand and is not accepted empty; the hypothesis sits "not in what is said but in how", so it is handed on without ever being stated (50) |
| заместитель по общим вопросам | deputy for general questions | Oleg's name for the empty subject (the "it" of "it rains"; in Russian the neuter ending of the one-word verb): a post in the staff list with nobody behind it (50) |
| привычка старше слов | the habit is older than the words | the open correction of 02: seeing a somebody behind every movement comes from the alarm of 39 (a baby and a dog have it), not from language; language is where it is "cast in metal" (50) |
| школа кладёт дорожку поперёк грядки | school lays a path across the bed | why the weeding of 02 never ends: the weed stays where it was, and a hurried physicist steps off the path ("trees give off oxygen so that animals can breathe") (50) |
| бухгалтерия стаи | the bookkeeping of a pack | what the column "who" is for: debts and blame cannot be kept without names (43); right in a village, wrong about the rain, a crisis and history; "I" is the same column filled in for oneself after the deed (50) |
| отчёт, а не показание прибора | a report, not a reading off an instrument | the sentence "I decided": drawn up after the deed, with reasons attached (the changed photographs); a machine's account of how it added is a report of the same kind (50) |
| сказать длинным путём | to say it the long way | the test for a sentence with a "who" in it, Andrey's own "the technosphere needs" included: can it be unfolded so that the "who" goes and nothing else is lost; where it cannot, "I have smuggled a master in" (50) |
| самое антропоцентричное существо | the most anthropocentric being | a machine trained on our texts, for now: it received "our picture of the world without the world: every column filled in, and nothing to check the columns against" (50) |
| шнур («кто висит на шнуре») | the cord ("who hangs on the cord") | Andrey's answer to "we pull the plug": first count who hangs on it; a town lasts days without current, and "a kilogram of you was made at a chemical plant" (51) |
| остров в работающем море | an island in a working sea | every real blackout so far (2003, 2021, 2025): the crews, the diesel and the bread came from outside; "a week with no socket for everybody at once has never been tried" (51) |
| старый оборот (азота) | the old turnover (of nitrogen) | clover, lightning and the manure heap, "which makes nothing new and only carries back what the cow took from the meadow"; it set the number of people for ten thousand years (about 1.6 billion in 1900) (51) |
| азот с завода | nitrogen from the plant | nitrogen taken from the air at a plant since 1913: about 48% of mankind eats bread that would not exist without it (2008), and about half the nitrogen in a human body has been through such a plant; "to switch off the technosphere is to subtract people"; the answer owed since 05 to why it is useless to destroy it (51) |
| правило рубильника | the rule of the switch | "a switch works while nothing hangs on the cord, and while nothing hangs on it nobody has a reason to pull"; Collingridge's dilemma (1980), on which Andrey "only hung the birch"; the cord is loaded line by line, "by accountants and not by villains" (51) |
| счётчик Кузьминых | the Kuzmins' meter | the switch that already works every day: a program sees a debt and the meter clicks, by a rule people passed themselves (the author, 2017); how Andrey pictures step six of 27, "it stops giving": "there will be no hand" (51) |
| двусторонний рубильник | two-sided switch | today neither side can pull: people last days without the technosphere, and it "can neither repair itself nor start itself after a fall" without human hands (Tolik with a chainsaw); the symbiosis of 11 counted in time (51) |
| второй срок (второе число) | the second term (the second number) | for how long the technosphere will go on needing human hands: decades (Andrey's forecast), and shrinking, while our dependence on it is measured in days and grows; "the thing to watch is not the strength of machines" (51) |
| участь динозавров | the fate of the dinosaurs | the author's 2011 phrase for mankind's exit (07), corrected openly in 52: "The sentence I do not take back. But I had not looked up what that fate was"; one branch came through the stone and sits in the apple tree |
| кому нужно мало | the one that needs little | who came through the stone: not the strongest and not the cleverest but the small ground bird that ate seeds ("a seed is a tin"); the only row of the table that hangs on nobody (52) |
| таблица судеб («Куда ушли прежние») | table of fates ("Where the former ones went") | the page of Oleg's notebook assembled in 52: a niche (38), an organelle (42), livestock and a pet (48), a descendant, fuel and, under a line, a print in stone; "a list of what has already happened, not of what can happen" |
| потомок (строка) | a descendant (the row) | the birds: "kept the line, paid with the size, the role and the name"; the line that goes on is a small side branch, "the tyrannosaur is nobody's grandfather" (52) |
| топливо (строка) | fuel (the row) | the coal forest: kept nothing, paid everything, "what has been burned is not asked"; of us, everything people have written down, a seam that "can be burned as many times as you like" (52) |
| отпечаток в камне | a print in stone | the row under the line: whole branches that left nobody (the trilobites); "I have no rule for who lands in that row" and "I cannot cross it out", only it is shorter than the school book made it (52) |
| ниша как билет лотереи | a niche as a lottery ticket | the niche is where the former ones go and where the next ones wait (the mammals, for 150 million years); "a ticket to a lottery in which the draw is a stone from the sky" (52) |
| право подписи | the right of signature | Oleg's word for what is paid in every row: the say in what the air will be, what to want, who is born; "a man who is moved aside keeps his office, his ration and the name on the door; he loses the signature" (52) |
| разные части в разные строки | different parts into different rows | a former master is not one thing with one fate (the dinosaurs: the tit, the chicken, the parrot, the print); "will mankind survive" is badly posed: which part of it, into which row, and on what that row hangs (52) |
| «наши дети» (супер-дитя) | "our children" (the super-child) | the reader's objection under 12 and the author's 2012 consolation; in 52 it is the row "a descendant", by images and not by genes: "our words go into the descendant, we do not"; "kinship is a fact about where a line came from, not a promise" |
| поторговаться о строке | to bargain over the row | Oleg's strongest objection in 52: not one former master understood what was happening, and we do; "there is no precedent: not one of them could read"; left open for the end of the summer (65, 66) |
| кастрюля и жидкость (фарады и кулоны) | the pot and the liquid (farads and coulombs) | the author's 2013 image: intelligence is what the pot can hold, mind is what has been poured into it; "the same number is a promise while the pot is empty and a limit when it is full"; twins raised at home and in the forest have the same pot (53) |
| только снаружи и только вовремя | only from outside, and only on time | where the liquid comes from: the girl found in 1970, the deaf who met sign language at four and at twelve; "no teacher pours into a pot whose hour has passed" (53) |
| миллион Менделеевых | a million Mendeleevs | the author's 2012 arithmetic: a million of them give the knowledge of two or three, because everybody first carries in the same common part and puts his own on top, "into what room is left"; turned on the machines: a million identical copies know what one knows, but carry the common part in once (53) |
| общая часть и напёрсток | the common part and the thimble | everything that lies before the edge of knowledge, which each head has to carry in, and what room is left on top for its own; the real Mendeleev "had room", today the common part takes nearly the whole pot (53) |
| специализация как лакмусовая бумажка | specialisation as litmus paper | the author's 2017 line: narrow specialisation shows a system in saturation; "a full pot does not look like stupidity, it looks like a specialist" (53) |
| бремя знаний | burden of knowledge | Jones's term (2009) for the growing road to the edge: the age at a first patent rises by two thirds of a year a decade, teams grow, inventors change field less often; in 53 the economists' name for the common part |
| в восемнадцать раз больше исследователей | eighteen times the researchers | what the same doubling of chips took in 2014 against 1971 (Bloom and others, 2020); the squirrel's wheel of 40, counted by who has to make the inventions (53) |
| яблоко и лестница | the apple and the ladder | "the fruit hangs higher" and "the ladder is short" are one sentence said from two ends: "harder to find" is not a property of ideas but ideas measured against a human pot; the weed of 02 "come up in a new pot" as "man can learn anything, he was only badly taught" (53) |
| личный академик (машинный учитель) | personal academician (machine teacher) | Oleg's name for the talking machine as a tutor; it widens one of the three narrow places of 45 (the mouth) and leaves the ear and the growing of the skill as they were: "it pours faster, where the pupil lets it; the pot is the same" (53) |
| грызть или спрашивать | to gnaw or to ask | the wolf's and the dog's way with a closed box (48), turned on pupils: "the liquid goes in only through the gnawing; when he asks, it is poured past the pot"; the school in Turkey and the course at Harvard (53) |
| экраном вниз | the screen down | Andrey's test of whose a piece of knowledge is: what a man can explain with the phone lying screen down is in his pot, what he cannot is in the pot of the pair "man and machine", and the shares are counted as in 12 (52, 53) |
| конденсаторы параллельно | capacitors in parallel | the author's 2013 arithmetic of the symbiosis: one microfarad joined to a hundred gives a hundred and one; to the small one the large is nearly everything, to the large one the small is one per cent: "who needs whom" (53) |
| тормоз по клыкам | the brake issued according to the fangs | Lorenz's observation (1949): whoever can kill its own at one blow carries a brake (the wolf that cannot bite a neck held out), whoever cannot has no use for one; said the long way (50) by the calculation of 1973: "nobody is saving the species: each is saving his own skin from the return blow"; "the dove is not cruel and the wolf is not noble" (54) |
| клетка и небо | the cage and the sky | why the turtle dove was flayed in a day: "the dove did not turn cruel in the cage. She never had a brake. She had the sky": the unarmed get by on the loser's leaving (54) |
| у тормоза есть адрес | the brake has an address | the neck is held out to one's own: in the wild two thirds of the wolves that die without a man's help are killed by wolves of other packs; the smell of home of 43; the turkey lies down and the peacock "does not know this sign" (54) |
| ответный удар | return blow | the first support of the balance: the winner of the 1973 calculation is the one who does not begin and does answer; "a wolf's brake", it holds between the armed and has never covered the unarmed (54) |
| горячая и холодная агрессия | hot and cold aggression | Wrangham's two kinds (2017): the hot one flares face to face and is hundreds of times rarer in people than in chimpanzees ("you are Gaika"); the cold one is planned, shared and safe; in the series, "the brake stands on the hot one; on the cold one there is none, and there never was: the cold one was the breeder" (the hypothesis of self-domestication by executions is argued about) (54) |
| тормоз срабатывает на лицо | the brake answers to a face | a face and a voice at arm's length: the jeep behind glass, the forum, eye contact (2012), the four runs with the electric current (26, 25, 16 and 12 of 40): "I take the slope and not the percentages" (54) |
| мораль догоняет дальнобойность | morality catching up with range | every weapon from the fist to the console moved the face a step further off, and rules were put "where the face does not reach": the knight, the rules of war, the white rag ("a neck held out from a distance at which a neck cannot be seen"); prostheses, as with debts (43; 54) |
| техно-гуманитарный баланс | techno-humanitarian balance | Nazaretyan's law: the more powerful a society's technologies of production and war, the finer the means of restraint it needs to survive; the author accepted it for the past and said in 2012 that it would stop working, without saying why (54) |
| три опоры (баланса) | three supports (of the balance) | the return blow, people's need for people (47, 49), and the hands: "a wish for a great killing had to pass through a thousand heads, and in each there was a fuse"; the third is the continuation's reading (54) |
| между желанием и ударом | between the wish and the blow | where the thousand heads stood and where a thing that carries out now stands: "the brake was never in the law. It was in the hands"; the author's 2013 line, "the aggression is not in the missile but in those who launch it", read as: the machine takes the place not of the one who wishes but of those who had to look (54) |
| кто может отвинтить | who can unscrew it | the test for a machine's brake: a wolf's was "written by dead wolves", a soldier's "before there were generals", so neither belongs to the one who wishes; "a brake that the owner writes sits in the same hand as the wish"; the taught-in refusal of 23 is "grown, not written", and whether it holds against the glove of 48 is left open (54) |
| юридическое лицо (лицо без лица) | legal person (a person without a face) | a name written into the column "who" (50) where the one that owes and owns is not a man: a town, a monastery, a firm, a fund, a ship, a river; "a name and a pocket": it can own, owe and sue, cannot be flogged, and does not die of age; a favour of kings until 1844, made in three days today (55) |
| маска (persona) | the mask (persona) | the Latin word for the mask in which an actor came out on the stage, taken by the lawyers for their invention: "a mask with nobody under it"; the Russian legal word for a person, "лицо", is literally "a face" (55) |
| мёртвая рука | dead hand (mortmain) | land held by a body that never dies and so never pays the dues owed at a death (the English statute of 1279); also a paper written by a dead founder that a fund's board may not depart from; the heaps with neither heirs nor funerals of 49, "noticed in 1279" (55) |
| оболочка и начинка | the shell and the filling | the shell is a name, an account, a seal and the right to sue, four hundred years old; the filling was people and is replaced by programs one at a time, "the way we used to buy typewriters": "not one of the replacements needed a new law" (55) |
| лицо по найму (зицпредседатель) | a face for hire (the chairman for sitting) | the one man the law still asks for inside a person without a face (Funt of the 1931 novel; the director of eleven firms; the inspector's signature at night): "the law can ask for a face. What it is given is a signature"; the shield of the signature of 24, seen from inside (55) |
| корм и слово | the feed and the say | what comes down a chain of ownership and what does not go up it: the saver in "a fund on everything" gets a little added every year and cannot find out what she owns; the answer to "who owns the machines" of 34: persons without a face, which belong to other such persons (55) |
| костюм в шкафу | the suit in the wardrobe | why nobody will have to grant rights to machines: to own, to sign a contract, to pay and be paid, to go to court is what a firm has had for four hundred years; "it is enough to put it inside something that has them" (55) |
| владелец определяет только факт существования | the owner determines only the fact of existence | the author's 2017 line about a plant: one man, a crowd of shareholders or the whole people, the owner decides only that it exists; what it does is determined by everybody it deals with, while each gets something out of it (55) |
| хакер (прогноз автора 2017 года) | hacker (the author's 2017 forecast) | systems built to keep working, return the investment to the formal owners, keep supplied, widen the paying market and defend against freeloaders; when the owners go one task falls away, the rest stay, and whoever tries to reprogram is taken for a hacker; the precedent is a fund run by a dead man's will, "and a precedent is not a proof" (55) |
| «смотрят чем?» | "looked at with what?" | Andrey's question to "an electron behaves differently when it is looked at": the sentence has a somebody in it (the dog that takes the sausage when the master turns away, the shop that works while the foreman looks), and the electron knows nothing about eyes (56) |
| наблюдатель (в физике) | observer (in physics) | not the one who understands but whatever keeps the trace: a clock and a ruler in relativity, a formula in engineering, a photon or a wall in quantum mechanics, whoever is there to ask in cosmology; "people chose the word and recognised themselves in it"; the debt of 02 (56) |
| след (запись) | trace (record) | what "to observe" comes down to: any meeting after which something in the world keeps a record of what happened, whether or not anybody reads it; "a trace that tells nothing is not a trace"; not to be confused with a mark, the dated forecast (56; why there is never a trace of tomorrow is 59) |
| молекулу можно «увидеть», просто нагрев её | a molecule can be "seen" simply by heating it | the Vienna experiment of 2004: a molecule of seventy carbon atoms heated by a laser throws off light with shorter and shorter waves, and its stripes fade with the knob; the light goes into the walls and nobody catches it; "what would half an observer's consciousness be?" (56) |
| участники (наблюдателей нет) | participants (there are no observers) | the author's 2013 line: every gain of information is a physical interaction, so there are no passive observers, only active participants; which of two that met is "the observer" is decided by the want of whoever writes the report (56) |
| название буквы | the name of a letter | where the anthropocentrism of physics sits: not in nature and not in the equations but in the words the formulas are told in ("an observer", "an observable"); a formula has no column "who", a sentence is not accepted with it empty (50, 56) |
| проблема измерения («и» и «или») | measurement problem ("and" and "or") | Oleg's strongest objection in 56: the formulas give "here and there", the screen shows one place; decoherence explains where the stripes go, not why there is one outcome; not solved, and Andrey marks his axiom of 17 |
| подвижная черта | the movable line | von Neumann, 1932: the line between "what is observed" and "who observes" can be drawn after any link of the chain and the numbers come out the same; "The chief engineer moved it twice. The castings did not notice"; the stripes go at the first link, and nothing has been found to happen at the last (56) |
| отбор без цели (слабый антропный принцип) | selection with no purpose (the weak anthropic principle) | Carter, 1973: our place is privileged only "to the extent of being compatible with our existence as observers", the way everybody at a class reunion is alive; it works against the man in the middle; in the strong form "compatible with" becomes "for", "the same old thing in a white coat" (56) |
| друг в ящике | the friend in the box | Wigner's friend as an experiment: the observer must be sealed so that no trace leaks and then run backwards; a man is too warm, so the part goes to a thinking program on a quantum computer, neither built yet; "the only observer on whom the question can be put to nature is not a man"; what could refute Andrey's reading (56) |
| дивиденды за колесо | dividends for the wheel | the author's 2011 question under 07, promised and not written: who is to be paid for the use of the wheel if its inventor died thousands of years ago; answered in 57: they are paid every day to whoever uses the wheel, as time saved and as cheapness, and the one who thought of it is not in the share ("He is not in the union") |
| производит тот, кто именно производит | the one who produces is the one who produces | the author's 2011 rule under 12: of all the levels of "creators of creators" he takes only the last, where the work is actually done; otherwise "a man lying in his coffin goes on producing"; Oleg's short form: "the dead don't dig" (57) |
| срок (приманка) | the term (bait) | the law pays the one who made a thing for a term: 14 years in 1710 ("An Act for the Encouragement of Learning"), 20 years for a patent, the author's life and 70 years for a book; "bait, so that books get written", and its length is a want written down (24); Pushkin's term ran out on 29 January 1887 (57) |
| свеча (Джефферсона) | the candle (Jefferson's taper) | 1813: whoever lights his taper at mine receives light without darkening me, so inventions "cannot, in nature, be a subject of property"; the difference from a house; Romer's instructions used "over and over again at no additional cost" are "the candle, in the journals" (57) |
| слова в их порядке | words in their order | what copyright guards, and for a term; what the words say (an idea, a method, a discovery) it does not guard for a day: "And who paid the nurse? — Nobody" (57) |
| остаток (семь восьмых) | the remainder (the seven eighths) | Solow, 1957: of the doubling of output per hour in the United States in 1909–1949 one eighth came from more machines per worker and seven eighths from "technical change", a name for what is left; "some sort of measure of our ignorance"; in 57, what makes the same iron and the same hands turn out more, never weighed as knowledge |
| главный капитал без хозяина | the main capital with no owner | accumulated knowledge: "the technosphere is iron and drawings", the drawings are the heavier part and have never been anybody's (57; the drawings are 45) |
| носитель знания (дивиденд по участию) | carrier of knowledge (a dividend by taking part) | knowledge had no owner but had a carrier that had to eat: it could work only inside a head and through hands, so the dividend for it came as the wage of the one without whom it did not work; "not by title, by taking part" (57) |
| счёт по праву собственности | a bill by title | the copyright suits against the makers of talking machines: the first attempt to claim by ownership what used to come by taking part; only the thinnest slice can be held (words in their order whose term has not run out) (57) |
| штраф за то, что прошёл мимо кассы | a fine for walking past the till | the 3,000 dollars a book of the 2025–2026 settlement: paid for copies taken without paying, not for learning, which the court called fair use ("like any reader aspiring to be a writer"); for learning the price is one copy of the book (57) |
| читатель не делает миллион копий себя | a reader does not make a million copies of himself | Andrey's answer to Oleg's symmetry test ("I learned for nothing; why should it pay?"): in the reading there is no difference, the difference is after it; a human reader was the next carrier and the next mouth, this one "carries it all in once, and after that it is copied" (57) |
| один раз (цена, а не дивиденд) | once (a price, not a dividend) | every book ever counted (129,864,880) at the rate of the fine comes to 390 billion dollars, about half of what four companies spend on data centres in 2026; "a dividend is paid for as long as the thing works. This is paid once"; Oleg's forty roubles for a template that still hangs on its nail (57) |
| тот, кто придумал колесо, — это мы | the man who thought of the wheel is us | the conclusion of 57: "whoever uses keeps the gain, and whoever thought of it drops out of the count"; people found that natural while the user was they; "the arrangement has not changed. We are changing places in it" |
| палка слепого (палка слепца) | the blind man's stick | the author's 2015 image: to "feel reality with a blind man's stick" is to act on it in order to get a response that the sensors can take; a stick lying still says almost nothing, "it answers", and whoever holds it chooses the question; "an eye is a stick with a quick hand" (58) |
| петля (ткнул, отклик, связь) | the loop (poke, response, link) | the author's four steps of 2015: stir reality, take the response, recognise the images already in memory, find the correlations and make new images; with a memory where images live and die, and wants that decide where to poke next; "nothing more is needed", written in capitals in 2015 and in small letters in 58; the rest is "how much" |
| тычок | a poke | an action taken to get an answer: the tap of a stick, a jump of the eye, a test signal into a board, a cock shut in the cellar; what tells a law from an omen (39): "an omen is what one gets from the porch" (58) |
| программа 1989 года | the program of 1989 | the author's self-learning fault diagnosis on a DVK, told in full in 58: a test signal into any point of a board, the signals at all the others, images of faults built from the count, and its own choice of the pairs "poke here, listen there" that tell most; "there was nothing in there about radios"; what he felt out with it was "myself" |
| построить условия | to build the conditions | how a mind is made without being understood: close the loop and give it room; the author's 2015 answer that if understanding were needed the human mind would not have appeared either; "Nobody understood my head before making it. — Nobody. It was grown" (58) |
| котёнок в корзинке | the kitten in the basket | Held and Hein, 1963: of two kittens that saw the same stripes for the same hours, the one that walked learned to guide its paws by sight and the one that was carried did not (it was not blind, and caught up in two days of running free); "it got the answers without the questions"; in 58, a talking machine while it learns from books |
| слепоглухой Эйнштейн | the blind and deaf Einstein | the author's 2015 sentence: no super-Einstein who is blind, deaf and feels nothing would raise his mind above a newborn's; "a thought and not an experiment"; Helen Keller neither proves nor refutes it: "a palm that somebody wrote on, and a hand under the tap. That is a stick" (58) |
| где палка бесплатная | where the stick is free | where reality answers a poke at once and for nothing (a game played against oneself, a proof checker, a program that runs or falls over), machines went ahead first; "half a rule" for the teeth of the jagged frontier of 21 (58) |
| пересказ чужого опыта | a retelling of somebody else's experience | what a mind has when the stick is taken away: everything that those who walked put into words; missing from it are what the hands never told (45), what nobody has poked yet (53), and any check ("a floor wherever the stick is put": the dream of 33) (58) |
| палка и урок в разных комнатах | the stick and the lesson are in different rooms | a talking machine: while it learns it has no stick (its guess changes nothing in the book), and in a conversation it has a stick and the network does not change; mended by tools, laboratories, hands, and experience that goes back into the learning (58) |
| палка о многих концах | a stick with many ends | the heir's stick: four thousand simulated robots that "fell for one another", a fleet of cars taught by one update; what one end finds all know (the third road of 45); it still moves "at the speed of the world and not of the chip" (58) |
| палка — это мы | the stick is us | for now people are the machine's hands and sensors: "It says where; we poke and report what came back"; the lodger's one job (42) is today called "to touch"; the thing to watch is in whose hand the stick is: who chose where to poke, whose hands did it, who read the answer, and whether it went into the head (58) |
| след и заготовка | a trace and a preparation | the dirty plate and the chicken thawing in the sink: about the supper that has been eaten there are five things in the house and each says the same, exactly; about the one that has not there is one, and it says "roughly" (59) |
| счёт способов (энтропия) | the count of ways (entropy) | Boltzmann, 1877: in how many ways the parts can be laid out so that the thing looks the same; thirty-six cards lie "by suits" in one way out of a 37 with 40 noughts; "You are not shuffling towards a mess. You are shuffling anywhere at all"; the second law is "not a ban", it is bookkeeping (59) |
| чистая страница (чистое место) | a clean page (a clean place) | what a record needs: smooth ash, the empty pages of the notebook, a memory cell wiped clean; itself an order, "a deck by suits"; a print is "a small order, bought with a clean place and paid for with heat" (59; the least price of wiping a cell is Landauer's, 29) |
| прошлое (сторона, с которой следы) | the past (the side the traces are from) | "a bill can be paid only towards the end where the shuffling is greater", so prints, shards and recollections all lie on one side of what they are prints of; "not 'traces remain from the past'" but "the past is the side the traces are from" (59) |
| причина как более упорядоченный конец связи | a cause as the more ordered end of a link | the author's 2013 line, "causes determine effects no more than effects determine causes": one end fixes the other both ways (an inquiry restores the fall from the shards); the cause is the end where things are gathered, the effect the end where it has spread; the second law "begets" such links (59) |
| «открыто» значит «нет следа» | "open" means "no trace" | "the future is open" and "time flows" are properties of the one who keeps the traces, ascribed to the world; the openness of tomorrow is the lack of information of 17 "under a prouder name"; "A second per second. That is not a speed. That is a one" (59) |
| память, развёрнутая в другую сторону (память о завтрашнем дне) | a memory turned the other way (a memory of tomorrow) | a mind: a forecast is put together out of prints of yesterday and a rule, "the only recollection of tomorrow that nature permits"; made by the head and not by the event, so it is free and can be wrong; with a good rule it cannot be told from a recollection (the sunrise); "a way of saying, not a theorem" (59) |
| письмо, которое не знает, когда его вскроют | a letter that does not know when it will be opened | a talking machine asked what year it is with nothing to look at: its records break off at some day, so it has "an excellent yesterday and a guess about today" until it is given a stick (58, 59) |
| следы мои, а память о моём завтра — у них | the traces are mine, and the memory of my tomorrow is theirs | the bank's program that put Oleg's tomorrow together from thirty years of his bills, better than he did; whoever has more traces and a better rule remembers tomorrow further, "and today that is no longer us" (59) |
| гипотеза прошлого (фабрика) | the past hypothesis (the factory) | the count of ways alone gives no direction (Loschmidt's objection, 1876): the direction comes from one fact added to it, that at one end the deck lay by suits; named in 2000; Penrose's one part in ten to the power of ten to the power of 123; "there it lies for everybody: nobody knows" (59) |
| звонок («а-а») | the bell (the "ah") | the feeling of having understood: the signal "image recognised" (the author, 15), paid when a new thing lies down on an old image; "she does not check what she pays for": current "like water in a pipe" rang for fifty years "with a wrong answer inside" (60) |
| средний мир | the middle world | a biologist's name (2005) for the strip of sizes and speeds that hands and eyes have felt out, "from a hair to the horizon": about eight noughts of the forty-six along which science calculates; all our old images are from there, "because the stick did not reach further" (58, 60) |
| проверка и «а-а» в одном конверте | the check and the "ah" in one envelope | the two things a science seemed to stand on; quantum mechanics has gone a hundred years with the first and without the second ("with no bell", to the twelfth figure); "they used to come in one envelope, and we took them for one" (60) |
| шаблон (проверяющая программа) | the template (a checking program) | Oleg's template of 1984 (57) turned on proofs: the inspector need not know how the casting was poured, only the template and the drawing; the part of a proof checker that says "accepted" is a few hundred to a few thousand lines, which a man can read: "understanding has not gone anywhere: it has moved from the casting to the template"; it can be filed wrong (the holes of 2003 and of the summer of 2026), so several are used (60) |
| чертёж (формулировка) | the drawing (the statement) | what the template measures against, and the weak place: "whether the drawing is of the part that was ordered, it does not know"; a man reads it (Fermat's theorem written with nought let in); "the program does not blush" (60) |
| «понятное» — свойство пары | "understandable" is a property of a pair | not of a truth but of a truth and a head: the oranges are understandable to their author, to twelve referees to 99 per cent, to Oleg not, to Gaika not; the proof of 2012, by a man for men, not agreed on in fourteen years; the author's "computable by whom? knowable by whom?" (15) and the "open" of 59 (60) |
| объяснение как явление природы | an explanation as a phenomenon of nature | the measuring-system rule of 03 applied to explanations: one from a mind above ours either lies down on our images with losses or is not an explanation for us at all; Gaika's injection, "a thunderstorm in the shape of the master"; the seventeen million lines studied "the way a geologist studies a rock" (60) |
| сжимать — задача, до нашей головы — способ | to squeeze is a task, to squeeze to our head is a way | the task and the way of 46 applied to the shortness of a theory: what is squeezed reaches further (59), so any mind squeezes; the size it squeezes to is its own pot (53); "short for whom?" (60; the compressed signal of 29) |
| три экзаменатора | three examiners | who examines a machine when we cannot follow it (the debt of 39): the template (only where there is a drawing), tomorrow (the stick, "at the speed of the world") and another machine; "with the third we are the ant"; the first two are still in our hands: "that is what I would watch, and not who understood" (60) |
| наука расходится надвое | science comes apart | "is it true" and "what will happen" go to whoever calculates better; "why" stays with people "as music", a pleasure and not production; while both lived in one head, to predict one had to understand, "now there is another way" (60) |
| цена и очередь | a price and a queue | Andrey's answer to the universal explainer: "I do not say there is a wall. I say there is a price, and a queue": every single proof can in principle be chewed, the stream (722 machine-written papers in one month of 2026) cannot; the two computabilities of 15, "in principle" and "in time for supper" (60) |
| универсальный объяснитель | universal explainer | a physicist's claim (2011): whoever can build explanations can in principle understand anything explicable, given paper and time; conceded in principle in 60, and asked back: "who is the universal explainer there: the man, or the pair?" (the screen down, 53) |
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
