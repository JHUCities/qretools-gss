# GSS Replicating Core: an example QREtools workspace

The demographic and work questions of the General Social Survey's Replicating Core, one
YAML file per question. Which questions to include follows the "Demographic and
life-course data" and "Work/employment data" sections of "The GSS Replicating Core,
current as of 2020". Everything NORC wrote here (wording, codes, labels, filters) comes
from the [GSS 1972-2018 cumulative codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS_Codebook_mainbody.pdf)
(main body, December 2019), except the reserved codes in `missing.yaml`, which come from
the [GSS 2022 codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf).

**This is the GSS of 2008.** The workspace replays the GSS's history, one survey year in
each pull request: 2008, 2010, 2012, 2014, 2016, 2018, then 2022 and 2024 (2021 is
skipped). Each year's workspace holds the questions the cumulative codebook shows answers
for in that year, and no others: a question leaves in a year that doesn't ask it and
comes back with the next year that does.
The cumulative codebook prints one wording for each variable, for all years: a question
whose wording changed is a new variable. So a question here has the codebook's wording,
which may not be word for word what the 2008 interviewer read.

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
| `missing.yaml` | the 2022 codebook's reserved codes, as letters |
| `universe` | the codebook's "IF …" filter, quoted; five are ours (below) |
| `note` | the codebook's full wording (and the question it falls under, as "stem"), word for word, so nothing taken out is lost. The codebook's remarks stay in `sources/`, because some of them hold counts |
| `source` | the GSS variable, the codebook's printed page, and the survey year that asked it |
| `title`, `intent`, `concept` | ours |

`tools/generate.py` checks that every text and instruction is a span of the codebook's
wording, so no wording is retyped or paraphrased. Counts and percentages are left out:
they come from the data, not the questionnaire. The extractor reads the codebook's counts
only to find the years a question was asked.

**Codes.** Each source codes missing values its own way: the cumulative codebook with
punch codes (0 for "Not applicable", 8 or 98 for "Don't know", 9 or 99 for "No
answer"), the released data with negative codes, and the 2022 codebook with letters.
`missing.yaml` keeps the letters. Translating each source's codes to them is the job of a
later GSS column map, not of this workspace.

One name here differs from the GSS variable: `divorced` is GSS `DIVORCE`. (From 2018,
`wrkselffam` is `WRKSLFFAM` and `yrsusa` is `YEARSUSA`.) Each question's `source` names the GSS variable.

[AGENTS.md](AGENTS.md) says how to open, check, regenerate and extend the workspace.

## Its DDI and its releases

Every push to `main` publishes the workspace's DDI at
<https://jhucities.github.io/qretools-gss/ddi.json>.

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
Data Explorer's documentation, and held an instrument, `replicating_core`. An import from
the 2022 codebook followed, but the replay replaced it before any release. From `v3`, each
tag holds one year of the replay, in the order of the survey years: `v3` is 2008. An
instrument for each GSS year comes in a later pull request.

## Universes we wrote

Most universes quote the codebook's filter. Three in 2008 are ours, worked out from the
order of the questions: `born_outside_us` and `other_language_speakers` (each follows the
question that decides it), and `self_employed`.

## Left out

The 2020 document lists these in the two sections, but they aren't questions put to
the respondent:

- **Recodes and derived variables**: AGE, ZODIAC, ETHNIC, EDUC, DEGREE, FUND, CONINC,
  REALINC, INDUS10, OCC10, ISCO08, PRESTG10, PRESTG105PLUS, SEI10, SEI10EDUC, SEI10INC,
  CONRINC, REALRINC. Also COHORT ("Birth cohort of respondent", in ranges) and MARTYPE,
  which the 2022 codebook says is coded from the interviewer's information and the
  Household Enumeration Form.
- **Taken from the address**: REGION, XNORCSIZ, SRCBELT, SIZE.
- **Coded by the interviewer, with no wording for the respondent**: SEX.

**Not asked in 2008**, so out of this year's workspace. Each comes back in the pull
request for the next year the cumulative codebook shows answers for it: VETYEARS (2010);
POSSLQ, POSSLQY, MAJOR1 and MAJOR2 (2012); INCOME16, RINCOM16, WKSUB1, WKSUBS1, WKSUP1
and WKSUPS1 (2016); WRKSLFFAM, YEARSUSA and MNTHSUSA (2018).

**Not in the cumulative codebook**, so they wait for the 2022 pull request: OTHER (the
codebook says DENOM's "Other" was recoded into it, but has no entry for it), WHATSLF2,
WRKGOVT1 and WRKGOVT2. WRKGOVT1 and WRKGOVT2 replace WRKGOVT, which is here for 2008.

Some pairs are kept although they're alike, each marked `variant_of`: the second and
third mentions of one question (RACECEN, ETH, OTHLANG). OTHLANG1 and OTHLANG2 don't
share a scale: the cumulative codebook numbers their languages differently from code 119
on. ETH1 doesn't share the ancestry scale with ETH2 and ETH3: its 98 is "No ethnicity
mentioned", an answer, where theirs is "Don't know".

## Known findings

`qretools check` gives two notes: SIBS and WEEKSWRK may ask about two things at once.
That's GSS's wording, so it stays.
