# GSS Replicating Core: an example QREtools workspace

The demographic and work questions of the General Social Survey's Replicating Core, one
YAML file per question. Which questions to include follows the "Demographic and
life-course data" and "Work/employment data" sections of "The GSS Replicating Core,
current as of 2020". Everything NORC wrote here (wording, codes, labels, filters) comes
from the [GSS 1972-2018 cumulative codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS_Codebook_mainbody.pdf)
(main body, December 2019), except the reserved codes in `missing.yaml`, which come from
the [GSS 2022 codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf).

**This is the GSS of 2012.** The workspace replays the GSS's history, one survey year in
each pull request: 2008, 2010, 2012, 2014, 2016, 2018, then 2022 and 2024 (2021 is
skipped). Each year's workspace holds every question the cumulative codebook shows answers
for in that year or an earlier year of the replay. A question comes in with the first year
that asks it and stays, as it would in a question bank, even when a later year doesn't ask
it. 2010 adds VETYEARS. It also replaces INCOME and RINCOME, which are recodes, with the
questions they are recoded from, INCOME06 and RINCOM06 (see "Left out"). 2012 adds
POSSLQ, POSSLQY, MAJOR1 and MAJOR2 (see "The questions of 2012").
The cumulative codebook prints one wording for each variable, for all years: a question
whose wording changed is a new variable. So a question here has the codebook's wording,
which may not be word for word what the interviewer read in a given year.

The workspace started from [qretools-template](https://github.com/JHUCities/qretools-template)
and keeps its layout and conventions.

This is an example, not a NORC publication. It's published under JHU's DDI agency,
`us.jhu` (registered with the DDI Alliance on 2026-10-19).

**Licence.** The GSS material is NORC's, used under the 2022 codebook's permission
notice, which every copy must keep. The cumulative codebook has no notice of its own;
the owner decided on 2026-11-12 to apply the 2022 notice to it. Our own work here is MIT
(code) and CC BY 4.0 (everything else). [LICENSE.md](LICENSE.md) says which is which.

**Scope.** Only two parts of the Replicating Core, on purpose: demographics and work.
The rest (spouse or partner, parents and family background, household, technical data
and paradata, and the attitude questions on every ballot) is left for later, not missed.

## Where each field comes from

| Field | Source |
|---|---|
| `text` | the codebook's wording for the variable (or the question it falls under, for a sub-item such as "B. Second mention"), word for word, without the parts that aren't read to the respondent: the "IF …" filter goes to `universe`, directions to the interviewer go to `instruction`, routing inside the label ("IF YES:") is cut, and stand-ins such as "(Are/Were)" become `fills` |
| `responses`, `scales/` | the codebook's punch codes and labels, without routing ("(ASK HRS1)") or cross-references ("[See REMARKS]"), and with capitals made ordinary where a label is all capitals. Only substantive codes: rows such as "Not applicable", "Don't know", "No answer" and "Refused" are left out. Where the codebook shows ranges of values ("collapsed for convenience of display"), there are no codes, and the question is a number |
| `number` | `min` is 0. `max` is the bound that the question sets: 168 hours in a week (HRS1, HRS2), 52 weeks in a year (WEEKSWRK). For SIBS and AGEKDBRN it is 97, the largest answer that the codebook's two-digit field holds below "Don't know" (98) and "No answer" (99) (pages 174 and 176). CHILDS takes 97 from SIBS: the codebook codes CHILDS in one digit, with "Eight or more" as a top code (page 175). NUMEMPS's 99999 is our choice: the codebook's "97 or more" (page 1625) is a top code, and no source gives a bound. From 2018, MNTHSUSA takes 11 (it asks for months only below a year) and YRSUSA 97 (page 2955). A top code is never a `max`, because respondents answer above it |
| `missing.yaml` | the 2022 codebook's reserved codes, as letters |
| `universe` | the codebook's "IF …" filter, quoted; five are ours (below) |
| `note` | the codebook's full wording (and the question it falls under, as "stem"), word for word, so nothing taken out is lost. The codebook's remarks stay in `sources/`, because some of them hold counts |
| `source` | the GSS variable, the codebook's printed page, and the first survey year of the replay that asked it. It doesn't change when a later year asks the question again, so neither does the question's version |
| `title`, `intent`, `concept` | ours |

`tools/generate.py` checks that every text and instruction is a span of the codebook's
wording, so no wording is retyped or paraphrased. Counts and percentages are left out:
they come from the data, not the questionnaire. The extractor reads the codebook's counts
only to find the years a question was asked.

**Codes.** Each source codes missing values its own way: the cumulative codebook with
punch codes (0 for "Not applicable", 8 or 98 for "Don't know", 9 or 99 for "No
answer"), the released data with negative codes, and the 2022 codebook with letters.
`missing.yaml` keeps the letters. The GSS column map in `maps/` translates the data's
codes to them (see "Maps and datasets").

One name here differs from the GSS variable: `divorced` is GSS `DIVORCE`. (From 2018,
`wrkselffam` is `WRKSLFFAM` and `yrsusa` is `YEARSUSA`.) Each question's `source` names the GSS variable.

[AGENTS.md](AGENTS.md) says how to open, check, regenerate and extend the workspace.

## Its DDI and its releases

Every push to `main` publishes the workspace's DDI at
<https://jhucities.github.io/qretools-gss/ddi.json>. Beside it, in `instruments/`, it
publishes the DDI of each instrument (`gss_2008.json`), its Qualtrics survey
(`gss_2008.qsf`), and a copy of each column map in `maps/` (see "Maps and datasets").

Each release is also published in a folder named for its tag, and it stays there: for
example <https://jhucities.github.io/qretools-gss/v3/ddi.json> holds the questions of
2008, and `v4/instruments/gss_2008.json` the 2008 instrument. Each release is built with
the qretools that it pins. `v1` and `v2` are not published (`.github/pages-skip`): they
hold material from NORC's website, which this repository may not republish.

An instrument uses a release of this workspace, named by its tag:
`uses: gss: JHUCities/qretools-gss@v3`. It gets the questions as they were at that tag.
Changes merged into `main` reach it only after a new release, when the instrument's
author changes the tag.

There are two version numbers:

- The tag (`v1`, `v2`, `v3`) is the version of the whole workspace. Whoever makes the
  release chooses it.
- Each question's DDI version (the `2` in `urn:ddi:us.jhu:agekdbrn:2`) counts the changes
  to that question merged into `main`. Between two tags it can go up by more than one.

To make a release, run the Release workflow (Actions → Release → Run workflow) with the
next tag, such as `v4`. It tags the last commit on `main` and writes each question's DDI
version into the tag's message, so an instrument reading the tag gets those versions.
Never make, move or delete a tag by hand. `v1` was tagged by hand, before the workflow
existed, so its questions all read as version 1.

`v1` and `v2` were made from an earlier import, which took its material from the GSS
Data Explorer's documentation, and held an instrument, `replicating_core`. An import
from the 2022 codebook followed, but the replay replaced it before any release. From
`v3`, the tags follow the replay, in the order of the survey years: `v3` holds the
questions of 2008, `v4` adds the 2008 instrument, and `v5` holds the questions of 2010.
`v6` adds the 2010 instrument, and corrects the 2008 instrument to read `v5`. `v7`
removes the notice comment from each file and corrects PARTFULL in the 2008 instrument.
`v8` holds the questions of 2012. `v9` adds the 2012 instrument, and changes the 2008
and 2010 instruments to read `v8`. `v12` adds a maximum to each number question, and `v13`
changes the 2008, 2010 and 2012 instruments to read `v12`. The instrument for each GSS year comes in the pull
request after that year's questions.

## The 2008 instrument

`instruments/gss_2008.yaml` asks the 2008 questions. It reads this workspace at `v12`
(`uses: gss: JHUCities/qretools-gss@v12`), and `workspace.yaml` locks that tag to its
commit. Until `v9`, it read `v5`, and until `v13`, `v8`. Between `v5` and `v8`, no question
or shared file that it names changes in substance: only the notice comment is removed.
Between `v8` and `v12`, the only change is a maximum on each number question, which is a
correction. Each comment in the
file names the codebook page that a condition comes from.

**The 2008 data.** Where the codebook is unclear or contradicts itself, the owner settled
who was asked from the GSS 1972-2024 cumulative data file (release 3a), read locally: in 2008, a question counts
as asked of a respondent unless the value is "iap" (inapplicable). No figure from the data
is published here, because the data is not licensed for publication.

**INCOME06 and RINCOM06.** The 2008 instrument in release `v4` read `v3` and asked
INCOME and RINCOME. These are recodes, not the questions that the respondents answered
(see "Left out"). From `v6`, it reads `v5` and asks INCOME06 and RINCOM06 in their place.
A release never changes, so `v4` keeps the recodes.

RINCOM06's entry (page 230) doesn't print the question before it, "Did you earn any
income from (OCCUPATION DESCRIBED IN OCC-INDUSTRY) in [the previous year]?". RINCOME's
entry (page 217) prints it, with "Yes (ASK RINCOME)". The 2008 data shows RINCOM06 "iap"
for the same respondents as RINCOME, and asked at every value of WRKSTAT. So the input
`earned_income` stays, and RINCOM06 is asked after its "Yes". The data can't tell a "No"
to that question from a respondent who wasn't asked it: both are "iap".

**Order.** The cumulative codebook's question numbers, which follow its pages. They are
the codebook's order, not known to be the order of the 2008 interview: for example,
BETRLANG (755 B) comes after SPKLANG (748 E), and the questions on work come first.

**Routing.** What the codebook states, from three places, checked against the 2008 data:

- the "IF …" filter of a question (its `universe`);
- a routing note in a response label, such as "(ASK HRS1)" or "(Go to MARITAL)";
- a remark or a "Not applicable" label that says who was asked.

A question with none of these is asked of everyone, unless the 2008 data shows a skip
(AGEKDBRN). The codebook shows no form or
ballot split for these questions in 2008, so the instrument has none.

| Question | Asked when | Codebook |
|---|---|---|
| HRS1 | WRKSTAT is 1 or 2 | pages 122, 123 |
| HRS2 | WRKSTAT is 3 | pages 122, 124 |
| EVWORK | WRKSTAT is 5, 6, 7 or 8 | pages 122, 124 |
| WRKGOVT | EVWORK isn't "No" ("Go to MARITAL"; "Not applicable (never worked)") | pages 124, 127 |
| DIVORCE (`divorced`) | MARITAL is 1 or 2 | pages 135, 136 |
| WIDOWED | MARITAL is 1, 3 or 4 | page 137 |
| AGEKDBRN | CHILDS isn't 0 (the 2008 data) | page 176 |
| RINCOM06 | the question before it is "Yes" (input `earned_income`; the 2008 data) | pages 217, 230 |
| DENOM | RELIG is 1 or 11 (Christian; the 2008 data) | page 312 |
| JEW | RELIG is 3 | page 314 |
| RELITEN | RELIG isn't Don't know | page 318 |
| PARTFULL | WEEKSWRK has a value that isn't 0 (the 2008 data) | page 438 |
| OTHLANG1, SPKLANG, BETRLANG | OTHLANG is 1 ("No (GO TO PARLANG)") | page 1284 |
| NUMEMPS | the part before it is "Self-employed" (input `self_employed`; the 2008 data) | page 1625 |
| LOCALNUM | WRKSTAT is 1, 2 or 3 (the remarks, "Beginning in 1994") | page 2437 |
| USCITZN | BORN is "No" (input `born_in_us`; the 2008 data) | pages 210, 2954 |
| FUCITZN | USCITZN is 2 or Refused | page 2954 |

**Inputs.** Each one is a value that the routing or the wording needs and this workspace
doesn't hold:

- `self_employed`: the first part of the NUMEMPS question, GSS WRKSLF.
- `earned_income`: the question before RINCOM06, printed only in RINCOME's entry.
- `born_in_us`: GSS BORN, outside this workspace's scope.
- `last_year`: the year that "[the previous year]" means in WEEKSWRK, PARTFULL and
  RINCOM06.
- `occupation`: the occupation that RINCOM06 names, from questions this workspace doesn't
  hold.
- `are` and `do`: the codebook writes "(Are/Were)" in WRKGOVT and "Do/did" in NUMEMPS,
  and doesn't say which word is read to whom.

RELITEN names the religion from RELIG's answer (`label(gss.relig)`), which the workspace
holds.

A question that not everyone reaches has a universe. Where the workspace's question has
none, the instrument gives it one, in our own words.

**Not asked.** Ten of the 40 questions in `v8`:

- `vetyears`: the codebook shows no answers for it in 2008.
- `posslq`, `posslqy`, `major1` and `major2`: the codebook shows no answers for them in
  2008.
- `race` isn't in `v5` or a later tag. Its remarks say RACE was asked from 1972 to 2000,
  and replaced by RACECEN1-3 and imputed from 2002. The cumulative codebook shows values
  for it in 2008, so `v3` holds it, but nobody was asked it. It left the workspace in
  2010 (below, "Left out").
- `racecen2`, `racecen3`, `eth2`, `eth3` and `othlang2`: the second and third mentions
  in answer to the question that `racecen1`, `eth1` and `othlang1` ask. They are further
  answers to one question, not further questions, and an instrument can't yet record
  more than one mention of an answer.

**What the codebook doesn't settle, and how the 2008 data settled it.** PARTFULL is
under the 2010 instrument below: the 2008 and 2010 data agree on it.

- **USCITZN.** Its "Not applicable" label reads "Not Punch 1 in BORN", which would mean
  that only people born in the country were asked. The question's own answers, and the
  workspace's universe `born_outside_us`, say the opposite. The 2008 data confirms the
  opposite: it was asked after BORN "No", and never after "Yes". The instrument asks it
  after BORN "No".
- **WIDOWED.** Its "Not applicable" label reads "Punches 3-5 in MARITAL", which disagrees
  with its own filter (married, separated or divorced). The instrument follows the filter.
- **LOCALNUM.** Its heading says it is for those whose employer has more than one
  location, but the codebook shows answers to that screener (NUMSITES) only in 1988-91. The
  instrument follows the remark for 1994 on.
- **NUMEMPS.** Its remarks limit it to WRKSTAT 1-3, and its wording skips it after "No"
  to "Do/did you have any employees?". The 2008 data shows neither: it was asked of
  everyone self-employed, whatever WRKSTAT was, and "0" employees is an answer. The
  instrument asks it after "Self-employed" only.
- **JEW.** Its remark for 2008 says that OTHJEW "Yes" or "Half or part" also led to JEW.
  The 2008 data shows JEW skipped for those respondents. The instrument asks it after
  RELIG "Jewish" only.
- **RELITEN.** "ASK EVERYONE WITH ANY RELIGIOUS PREFERENCE NAMED IN RELIG" could leave out
  "None", but RELITEN has the answer "No religion", and its "Not applicable" names only
  Don't know. The 2008 data shows no skip for the other religions. The instrument asks
  everyone except Don't know.
- **AGEKDBRN.** The codebook gives no filter, although it asks about a first child. The
  2008 data shows it skipped after CHILDS "None". The instrument asks it unless CHILDS
  is 0.
- **BETRLANG.** It is printed under another question (755 B), after PARLANG, where OTHLANG
  "No" goes, and it has no filter. The condition, OTHLANG "Yes", is the workspace's own
  universe for it (`other_language_speakers`). SPKLANG's direction, to ask about the most
  fluent language, suggests that BETRLANG came before SPKLANG in the interview.
- **DENOM.** Its "Not applicable" label says that RELIG 5 and 11 were "often" or
  "sometimes" asked it too. The 2008 data shows it asked after 11 (Christian) every time,
  and never after 5. The instrument asks it after RELIG 1 or 11.
- **Codes for missing values.** The conditions on RELITEN and FUCITZN name the codebook's
  "Don't know" (98) and "Refused" (9) by the letters in `missing.yaml`, `D` and `R`,
  matched by label.
- **Who is asked the questions before RINCOM06 and NUMEMPS** (inputs here) is not in the
  codebook's entries for those questions.

Measured with QREtools 2.0.0-alpha.8: `qretools instrument check` gives 0 findings, and
`qretools paths` counts 5,760 ways through the routing, 13 to 27 questions on each
(median 20). Each of the 30 questions asked is reachable. QREtools 2.0.0-alpha.9 gives
the same results, before and after the change to INCOME06 and RINCOM06, and at `v8`.

## The 2010 instrument

`instruments/gss_2010.yaml` asks the 2010 questions. It reads this workspace at `v12`
(until `v9`, at `v5`, and until `v13`, at `v8`; as for 2008, nothing that it asks changes
in substance). It is a
copy of the 2008 instrument, with the changes below. Each condition was checked again
against the 2010 data, in the same way as for 2008.

**What it asks.** The 2008 questions, and VETYEARS, last (page 2956): 31 of the 40
questions in `v8`. The second and third mentions are not asked, as in 2008, and the
codebook shows no answers in 2010 for POSSLQ, POSSLQY, MAJOR1 and MAJOR2. The codebook
shows values for RACE in 2010 too, but its remarks say that nobody was asked it from
2002, and the workspace doesn't hold it from `v5`.

**Routing.** The same as in 2008 (the table above), with these changes:

| Question | Asked when | Codebook |
|---|---|---|
| RELITEN | always (the 2010 data) | page 318 |
| JEW | RELIG is 3 (its remark about OTHJEW is for 2008 only) | page 314 |
| VETYEARS | always | page 2956 |

The inputs are the same as in 2008.

**What the 2010 data settled.**

- **RELITEN.** Its "Not applicable" label says that RELIG "Don't know" was not asked it.
  The 2010 data shows it asked after RELIG "Don't know" too. The instrument asks
  everyone.
- **VETYEARS.** Its wording has two parts: "Have you ever been on active duty ...?",
  then "IF YES: What was your total time on active duty?". It is one variable: "No active
  duty" answers the first part, and the lengths of time answer the second. The codebook
  gives no filter, and the 2010 data shows everyone asked. The instrument asks it of
  everyone, as one question.
- **RINCOM06.** As in 2008: the 2010 data shows it "iap" for the same respondents as
  RINCOME, at every value of WRKSTAT.
- **AGEKDBRN, DENOM, NUMEMPS, USCITZN.** The 2010 data shows the same as the 2008 data.
- **PARTFULL.** In the 2008 and 2010 data, PARTFULL is "iap" after WEEKSWRK "Don't
  know". The codebook gives only "Punch 0 in WKSWRK". In QREtools 2.0.0-alpha.9 a number
  question's "Don't know" has no value in a condition, so both instruments ask PARTFULL
  when WEEKSWRK has a value that isn't 0. This also skips WEEKSWRK "No answer", which
  shows nothing about who was asked (below). Until release `v7`, the 2008 instrument
  asked PARTFULL after a WEEKSWRK with no value.
- **HRS2.** In the 2010 data, a few respondents with WRKSTAT 3 are "iap" for HRS2.
  Nothing in the codebook says why. The instrument follows HRS2's filter.
- **No answer.** Where a respondent gave no answer to a filter question (WRKSTAT, RELIG),
  the 2010 data codes the follow-up questions "No answer", not "iap". This
  doesn't show who was asked. The instruments treat them as in 2008.

Measured with QREtools 2.0.0-alpha.9: `qretools instrument check` gives 0 findings, and
`qretools paths` counts 5,760 ways through the routing, 14 to 28 questions on each
(median 21). Each of the 31 questions asked is reachable. The results are the same at
`v8`.

## The questions of 2012

The cumulative codebook shows answers in 2012, and in no earlier year of the replay, for
four questions: POSSLQ, POSSLQY, MAJOR1 and MAJOR2. The 2012 data agrees: each has
answers in 2012, and none has answers in 2008 or 2010. Each question that the codebook
shows as asked in 2012 has answers in the 2012 data, and each question that waits for a
later year has none. None of the four is derived from another variable: each holds the
respondent's answer.

- **POSSLQ and POSSLQY** are the two forms of one wording experiment, on cards A1.2a and
  A1.2b. In the 2012 data each respondent answered one form, never both. POSSLQ's codes
  have the codebook's short labels ("Married, together"); its card's statements are in
  its `note`. Both have the direction "CODE ONE ONLY." as their instruction.
- **MAJOR1 and MAJOR2** are the first and second mentions of one question, whose wording
  ends "[COUNT UP TO 2 MENTIONS]". The codebook prints the wording under MAJOR1 only,
  and MAJOR2's table follows MAJOR1's with no wording. So MAJOR2's text is MAJOR1's, and its `note` says that
  the wording is printed under MAJOR1. Its `source` is its own page.
- **MAJOR1 and MAJOR2's codes.** By the owner's decision, the workspace keeps the
  codebook's detailed codes (the shared scale `college_major`). In the GSS data release
  used here, MAJOR1 and MAJOR2 hold a shorter list of broad fields, not the codebook's
  codes. These broad fields are a grouping of the detailed codes, and the GSS column map
  will translate between them, as it translates the codes for missing values.

Two labels of the shared scale `college_major` were wrong in the extract, and the
extractor now reads them correctly. A label that wraps after "/" no longer gets a space
after the "/". MAJOR1's code 71 has a stray number after the second line of its label.
The extractor drops it and records the problem; MAJOR2 and another table of the
codebook print the same label without it.

## The 2012 instrument

`instruments/gss_2012.yaml` asks the 2012 questions. It reads this workspace at `v12`
(until `v13`, at `v8`). It
is a copy of the 2010 instrument, with the changes below. Each condition was checked
again against the 2012 data, in the same way as for 2008 and 2010.

**What it asks.** The 31 questions of 2010, and MAJOR1 (32, page 184, after AGEKDBRN),
POSSLQ and POSSLQY (1394 and 1395, page 2182, after NUMEMPS): 34 of the 40 questions in
`v8`. Each respondent gets one of POSSLQ and POSSLQY. Not asked: the second and third
mentions (RACECEN2-3, ETH2-3, OTHLANG2), and MAJOR2, the second mention of MAJOR1's
question ("[COUNT UP TO 2 MENTIONS]").

**Routing.** The same as in 2010 (the tables above), with these changes:

| Question | Asked when | Codebook |
|---|---|---|
| RELITEN | RELIG isn't Don't know (as in 2008; the 2012 data) | page 318 |
| MAJOR1 | DEGREE is 2, 3 or 4 (input `degree`; the 2012 data) | pages 182, 184, 192 |
| POSSLQ | Form 1 (input `form`; the 2012 data) | pages 513, 2182 |
| POSSLQY | Form 2 (input `form`; the 2012 data) | pages 513, 2182 |

**Inputs.** The inputs of 2010, and two more:

- `degree`: GSS DEGREE (page 182), the respondent's highest degree. It is a recode (see
  "Left out"), so the workspace doesn't hold it. It is the filter on MAJOR1, and MAJOR1
  reads its label aloud where the codebook writes "(RESPONDENT'S COLLEGE DEGREE)"
  (`label(degree)`, as RELITEN reads RELIG's).
- `form`: GSS FORM (page 513), the form of the split questionnaire that the respondent
  gets. The workspace doesn't hold it, because it isn't a question.

**What the 2012 data settled.**

- **POSSLQ and POSSLQY.** FORM's entry says that the variant or "Y" wordings are on Form 2,
  and the standard wordings on Form 1. The entries for POSSLQ and POSSLQY don't say which
  form each is on. In the 2012 data, every respondent on Form 1 answered POSSLQ and no
  respondent on Form 2 did, and POSSLQY is the reverse. BALLOT and MARITAL don't decide
  it. The instrument asks POSSLQ on Form 1, and POSSLQY on Form 2.
- **MAJOR1.** It has no filter of its own. WHENCOL's remark (page 192) says that WHENCOL
  was asked "when DEGREE=2-4". In the 2012 data, MAJOR1 was asked after every DEGREE of 2,
  3 or 4, never after 0, and after 1 for an isolated respondent only. The instrument asks
  it after DEGREE 2, 3 or 4.
- **RELITEN.** The 2012 data shows it not asked after RELIG "Don't know", as its "Not
  applicable" label says. The 2010 data showed it asked. The 2012 instrument follows the
  2012 data, and uses the condition of 2008. The 2010 instrument doesn't change.
- **Isolated skips.** The 2012 data shows a few respondents asked or skipped against the
  codebook, with no pattern that a condition can show: EVWORK asked after WRKSTAT 2,
  WRKGOVT asked after EVWORK "No", DENOM asked after RELIG "None", BETRLANG skipped after
  OTHLANG "Yes", and, as in 2010, HRS2 skipped after WRKSTAT 3. The instrument keeps the
  codebook's filter for each.
- **The other conditions.** The 2012 data agrees with each other condition of 2010:
  HRS1, DIVORCE, WIDOWED, AGEKDBRN, RINCOM06, JEW, PARTFULL, OTHLANG1, SPKLANG, NUMEMPS,
  LOCALNUM, USCITZN, FUCITZN and VETYEARS.

Measured with QREtools 2.0.0-alpha.9: `qretools instrument check` gives 0 findings, and
`qretools paths` counts 23,040 ways through the routing, 15 to 30 questions on each
(median 23). Each of the 34 questions asked is reachable.

## Maps and datasets

A column map tells `qretools responses` which DDI variable each column of a data file
records. With a map, `qretools responses` reads NORC's GSS data and the export of a
Qualtrics survey into one form: a dataset, with the URN of the DDI variable of each value.
Thus, NORC's answers and the answers of a Qualtrics survey are answers to one DDI.

### The folders `maps/` and `tools/`

- `maps/` holds only column maps. A map has the name
  `<instrument>-ddi-<source>.columns.json`. Its `source` field gives the same source.
- `maps/gss_2010-ddi-gss.columns.json` is the map of the 2010 instrument for the GSS
  data. `tools/columns.py` writes it.
- `maps/<instrument>-ddi-qsf.columns.json` is the map of a fielded Qualtrics survey.
  `tools/qsf-columns.sh` writes it.
- Do not edit a map that a script writes. Change the script, then run it again.
- `qretools build` copies each map to `dist/instruments/`, beside the DDI of its
  instrument. It does not make a map. If a map was made from a different DDI, `build`
  gives a `build-map-ddi` warning, and copies the map.
- A map holds no answers. A dataset holds the answers, so a dataset never goes into this
  repository.

**Caution: do not commit the GSS data, a CSV that `tools/columns.py` writes, a Qualtrics
export, a dataset, or a CSV view of a dataset. They hold answers. The GSS data is not
licensed for publication.**

### The scripts

**`tools/columns.py`** writes the GSS map.

- It reads the GSS cumulative data file (`gss7224_r3a.sav`) and the DDI of one
  instrument.
- It writes `maps/<instrument>-ddi-gss.columns.json`. It also writes the year's rows of
  the data to `<folder>/<instrument>-<year>.csv`, in the folder that `-o` names.
- Run it again when the DDI of the instrument changes, and when NORC publishes a new
  release of the data file.
- Commit the map. Do not commit the CSV: it holds the GSS data.
- It prints the names of variables and codes. It never prints a value or a count.
- Its tests use no data: `python3 -I -m unittest discover -s tools`.

**`tools/qsf-columns.sh`** writes the Qualtrics map of a survey from a release.

- It reads the instrument at a release tag of this repository. It needs git.
- It writes `maps/<instrument>-ddi-qsf.columns.json`.
- It runs `qretools qsf-map` with the version of QREtools that the tag's `mise.toml`
  pins, through `npx`. That version made the release, so it makes the same DDI.
- Run it one time for each fielded survey. Do not run it again for the same survey. If
  the map exists, the script stops.
- Commit the map.

### Put a survey in Qualtrics

1. Find the release that holds the instrument, for example `v15`.
2. Record the tag of the release.
3. Download the survey of the instrument from the release, for example
   <https://jhucities.github.io/qretools-gss/v15/instruments/gss_2010.qsf>.
4. Import the QSF file into Qualtrics.
5. Field the survey.

The survey holds the URN of its instrument and the digest of its DDI, in `qretools_*`
fields. Each response in the export holds these fields.

### Make the Qualtrics map

Do this procedure after you field the survey.

1. Run `tools/qsf-columns.sh <instrument> <tag>`, for example
   `tools/qsf-columns.sh gss_2010 v15`. Use the tag that you recorded.
2. Read each `qsf-unmapped` warning. The map has no column for the item that the warning
   names.
3. Commit `maps/<instrument>-ddi-qsf.columns.json`.

If the release was made before QREtools 2.0.0-alpha.12, the script cannot read its tag.
Then make the map from the DDI of the release:

1. Download the DDI of the instrument from the release, for example
   <https://jhucities.github.io/qretools-gss/v14/instruments/gss_2010.json>. Keep the
   name of the file: the name of the map comes from it.
2. Run `npx qretools@2.0.0-alpha.12 qsf-map <the DDI> -o maps/`. This map does not
   record the release. An earlier QREtools has no `qsf-map` command.
3. Commit the map.

If you do not know the release of the survey, make the map from an export of the survey
and a DDI of the instrument:

1. Run `qretools qsf-map --export <export.csv> --ddi <instrument DDI .json> -o maps/`.
2. Read each `qsf-map-matched` finding. It tells how the command matched a question of the
   export to a question of the DDI.
3. If a match is wrong, correct the map.
4. Read each `qsf-map-absent` warning.
5. Commit the map.

### Make the GSS map

**Caution: put the data file and the CSV outside this repository. Do not commit them.**

1. Get the GSS cumulative data file in SPSS format (release 3a, `gss7224_r3a.sav`).
2. Make an environment with pyreadstat:
   `python3 -m venv .venv && .venv/bin/pip install pyreadstat`
3. Make a branch from `main`.
4. Run `qretools build . -o dist`.
5. Run the tool:
   `.venv/bin/python -I tools/columns.py <gss7224_r3a.sav> dist/instruments/gss_2010.json 2010 -o <folder>`
6. Read the lines that the tool writes. Each line names a variable that the map leaves
   out or marks `filtered`, codes that the data labels and the workspace does not hold,
   or a label of a number that the tool cannot read as a range or as the number.
7. Run `git status`. If the map changed, examine the diff.
8. Commit the map on the branch.
9. Open a pull request.

### Change an instrument

The DDI of an instrument gets its version and its date from the history of `main`. Thus,
the new DDI of a changed instrument exists only after the merge. Use two pull requests.

1. Merge the change to the instrument. After the merge, `build` gives a `build-map-ddi`
   warning for the GSS map. The map holds the digest of the old DDI.
2. Do the procedure "Make the GSS map". It makes the second pull request.
3. Merge the second pull request.

Do not make the Qualtrics map of a fielded survey again. That map names the release of the
survey that you fielded. If you have not fielded the survey, no Qualtrics map exists yet.

### Make a dataset

`qretools responses` makes a dataset from the data and its map. The dataset holds each
answer, the time of each interview, the metadata columns of the map, and the provenance.

**Caution: write the dataset outside this repository. It holds the answers.**

To make a dataset of the GSS data:

1. Do the procedure "Make the GSS map". Keep `dist/` and the CSV.
2. Run `qretools responses <folder>/gss_2010-2010.csv --map maps/gss_2010-ddi-gss.columns.json --ddi dist/instruments/gss_2010.json -o <folder>/gss2010.json`.
   Use only letters, digits, `-` and `_` in the name of the dataset file.
3. Read the findings. A finding never shows a value.

The map gives the facts of the collection, so the command needs no other option: who
answered, the citation of the data file, the date of each interview, the mode of each
interview and the weights.

To make a dataset of a Qualtrics export:

1. Export the responses from Qualtrics (QREtools' README, "Export from Qualtrics").
2. Run `qretools responses <export.csv> --map maps/<instrument>-ddi-qsf.columns.json -o <folder>/qualtrics.json`.
   If the map records a release, the command gets the DDI from that release.
3. If the map records no release, add `--ddi <the DDI of the release>`.
4. If the command asks for `--answered-by`, add it. Real responses need it.

### Export a view

`qretools dataset export` writes a view of a dataset. Give it the DDI that the dataset was
made from.

- `--csv` writes the answers as long CSV, for analysis tools.
- `--provenance` writes the dataset without its answers.

This workspace declares no access levels. Thus, do not give `--access`.

**Caution: do not publish a CSV view of real data. Publish only the provenance view, and
publish `LICENSE.md` with it: the view quotes the GSS 2024 codebook.
Open a CSV view as data (in R, Python or the import of a spreadsheet). Do not open it with
a double click: a text answer can hold a formula, and a spreadsheet can run it.**

1. Run `qretools dataset export <folder>/gss2010.json --provenance --ddi dist/instruments/gss_2010.json -o <folder>/gss2010-provenance.json`.
2. Run `qretools dataset export <folder>/gss2010.json --csv --ddi dist/instruments/gss_2010.json -o <folder>/gss2010.csv`.

### What the GSS map holds

- Each question that the 2010 instrument asks, by its GSS variable (from its `source`).
  DENOM and NUMEMPS are marked `filtered` (below).
- The inputs that are GSS variables: `born_in_us` (BORN) and `self_employed` (WRKSLF).
  The other inputs have no GSS variable: `earned_income`, `last_year`, `occupation`, `are`
  and `do`. `display_label_1` is computed by the instrument, and is not data.
- The reserved codes, translated by label to the letters of `missing.yaml`: "don't know"
  to D, "no answer" to N, "refused" to R, "skipped on web" to S. "iap" (inapplicable) is
  no answer: the respondent was not asked, so there is no value. It is not I. The other
  reserved codes ("see codebook", "uncodeable" and so on) have no letter. If one occurs,
  `qretools responses` gives a finding.
- The top and bottom codes of the questions that are numbers (below), marked `censored`.
  The tool reads them from the data's value labels ("6 or more", "17 and younger", "89+").
  It writes a note for a label that it cannot read as a range or as the number.
- Who answered (`answered_by`): `ResearchData.Published`, a term of the DDI vocabulary
  DataSourceType. The answers come from a published data file.
- The citation of the data file (`citation`).
- The date of each interview (`interview_date`): DATEINTV holds the month and the day, and
  YEAR holds the year. If a cell of DATEINTV is a reserved code, that respondent gets no
  date, and `qretools responses` gives one `responses-date` warning.
- The columns that no respondent is asked, in `metadata`: MODE (the mode of each
  interview), PHASE (the phase of the sample), BALLOT and FORM (the version of the
  questionnaire), and the weights. The tool writes each weight that has values in the
  year. A weight with no values in the year is not in the map. The tool does not choose
  a weight. The labels and codes of these columns are the data's. In a weight, each
  reserved code is no value. OVERSAMP is not in the map: it is coded, not a number, and
  the codebook says that WTSSPS and WTSSNRPS include its adjustment.
- The modes: MODE's code "in-person" gives the term `Interview.FaceToFace.CAPIorCAMI`.
  Its code "by phone" gives the term `Interview.Telephone`. The codes "multimode" and
  "web" have no term yet. If a mode of the year has no term, the tool writes a note on
  MODE. Then add a term for that mode to `DESIGN` in `tools/columns.py`, and run the
  tool again. Without a term, the respondent gets no mode.
- `weighting`: what NORC advises about the weights, word for word, from the GSS 2024
  Codebook, Release 3a, page 40. The codebook's permission notice is in `LICENSE.md`.
- The digest of the DDI that the map was made from.

The map does not give the variance strata and units (VSTRAT and VPSU). Thus, a dataset
from the map does not support estimates of variance for the complex sample design.

**Where the data and the workspace disagree.** The map does not hide these.
`qretools responses` writes a note for each of them, and no error.

- **Filtered: NUMEMPS and DENOM.** A variable is filtered from a data file when the data
  file does not hold its values at the level of access that you have (QREtools' README,
  "Read a data file", defines the word). The data release holds these two in a form that
  the questions do not record. It groups NUMEMPS (0, 1-9, 10 or more employees), and the
  question asks for a number. It holds DENOM as broad groups (Baptist, Methodist and so
  on), and the workspace keeps the codebook's detailed codes, as it does for MAJOR1. So
  the map marks both `filtered`, and no value is read from them.
- **Top and bottom codes.** The data release labels SIBS 6 "6 or more", CHILDS 8 "8 or
  more", AGEKDBRN 17 "17 and younger" and 45 "45 and older", and HRS1 and HRS2 89 "89+
  hours". Such a value is a range, not a number, so it gives no answer. The codebook
  agrees on CHILDS (its code 8 is "Eight or more") and on HRS1 and HRS2 (their remarks:
  "Responses greater than 89 were coded 89"). For SIBS and AGEKDBRN, the codebook gives no
  top or bottom code: their remarks say only that the categories are collapsed for
  display. These caps are the data release's.
- **Inputs and reserved codes.** If the data gives a reserved code for an input (BORN or
  WRKSLF), the input accepts it as a missing value.

## Universes we wrote

Most universes quote the codebook's filter. Three in 2008 are ours, worked out from the
order of the questions: `born_outside_us` and `other_language_speakers` (each follows the
question that decides it), and `self_employed`. One in 2012 is ours: `college_degree`, for
MAJOR1 and MAJOR2. The wording names "(RESPONDENT'S COLLEGE DEGREE)", and in the 2012 data
the respondents with a junior college degree or higher answered MAJOR1, with an isolated
exception (see "The 2012 instrument").

## Left out

The 2020 document lists these in the two sections, but they aren't questions put to
the respondent:

- **Recodes and derived variables**: AGE, ZODIAC, ETHNIC, EDUC, DEGREE, FUND, CONINC,
  REALINC, INDUS10, OCC10, ISCO08, PRESTG10, PRESTG105PLUS, SEI10, SEI10EDUC, SEI10INC,
  CONRINC, REALRINC. Also COHORT ("Birth cohort of respondent", in ranges) and MARTYPE,
  which the 2022 codebook says is coded from the interviewer's information and the
  Household Enumeration Form. And RACE: its remarks say that from 2002 RACECEN1-3
  replaced it and RACE was imputed from them and other variables, so from 2002 nobody was
  asked it. It was in the workspace for 2008 (`v3`). And INCOME and RINCOME: in the GSS
  data for 2006 to 2012, RINCOME is RINCOM06 regrouped into fewer groups, and INCOME is
  nearly always INCOME06 regrouped. INCOME's remarks also say that it was recoded from
  other questions up to 2006.
  The respondents answered INCOME06 and RINCOM06, which the workspace holds. INCOME and
  RINCOME were in the workspace for 2008 (`v3`).
- **Taken from the address**: REGION, XNORCSIZ, SRCBELT, SIZE.
- **Coded by the interviewer, with no wording for the respondent**: SEX.

**Not yet asked by 2012**, so not yet in the workspace. Each comes in with the first
later year the cumulative codebook shows answers for: INCOME16, RINCOM16, WKSUB1,
WKSUBS1, WKSUP1 and WKSUPS1 (2016); WRKSLFFAM, YEARSUSA and MNTHSUSA (2018).

**Not in the cumulative codebook**, so they wait for the 2022 pull request: OTHER (the
codebook says DENOM's "Other" was recoded into it, but has no entry for it), WHATSLF2,
WRKGOVT1 and WRKGOVT2. WRKGOVT1 and WRKGOVT2 replace WRKGOVT, which is here for 2008.

Some pairs are kept although they're alike, each marked `variant_of`: the second and
third mentions of one question (RACECEN, ETH, OTHLANG, MAJOR), and the two forms of
POSSLQ's wording experiment (POSSLQ, POSSLQY). OTHLANG1 and OTHLANG2 don't
share a scale: the cumulative codebook numbers their languages differently from code 119
on. ETH1 doesn't share the ancestry scale with ETH2 and ETH3: its 98 is "No ethnicity
mentioned", an answer, where theirs is "Don't know".

## Known findings

`qretools check` gives two notes: SIBS and WEEKSWRK may ask about two things at once.
That's GSS's wording, so it stays.
