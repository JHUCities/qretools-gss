# GSS Replicating Core: an example QREtools workspace

The demographic and work questions of the General Social Survey's Replicating Core, one
YAML file per question. Which questions to include follows the "Demographic and
life-course data" and "Work/employment data" sections of "The GSS Replicating Core,
current as of 2020". Everything NORC wrote here (wording, codes, labels, filters) comes
from the [GSS 2022 codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf).
The workspace started from [qretools-template](https://github.com/JHUCities/qretools-template)
and keeps its layout and conventions.

This is an example, not a NORC publication. It's published under JHU's DDI agency,
`us.jhu` (registered with the DDI Alliance on 2026-10-19).

**Licence.** The GSS material is NORC's, used under the 2022 codebook's permission
notice, which every copy must keep. Our own work here is MIT (code) and CC BY 4.0
(everything else). [LICENSE.md](LICENSE.md) says which is which.

**Scope.** Only two parts of the Replicating Core, on purpose: demographics and work.
The rest (spouse or partner, parents and family background, household, technical data
and paradata, and the attitude questions on every ballot) is left for later, not missed.

## Where each field comes from

| Field | Source |
|---|---|
| `text` | the codebook's label for the variable, word for word, without the parts that aren't read to the respondent: the "IF …" filter goes to `universe`, directions to the interviewer go to `instruction`, routing inside the label ("IF YES:") is cut, and stand-ins such as "(Are/Were)" become `fills` |
| `responses`, `scales/` | the codebook's codes and labels, with the capitals made ordinary. These are only the codes the 2022 codebook prints, which can be far fewer than the GSS's full list: OTHER has 37 here. A code missing here may still be a GSS code |
| `missing.yaml` | the codebook's reserved codes |
| `universe` | the codebook's "IF …" filter, quoted; five are ours (below) |
| `note` | the codebook's full label and notes, word for word, so nothing taken out is lost |
| `source` | the GSS variable and the codebook's page |
| `title`, `intent`, `concept` | ours |

`tools/generate.py` checks that every text and instruction is a span of the codebook's
label, so no wording is retyped or paraphrased. Counts and percentages are left out:
they come from the data, not the questionnaire.

Three names differ from the GSS variable: `divorced` is GSS `DIVORCE`, `wrkselffam` is
`WRKSLFFAM` and `yrsusa` is `YEARSUSA`. Each question's `source` names the GSS variable.

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
Data Explorer's documentation, and held an instrument, `replicating_core`. From `v3` the
material comes from the 2022 codebook alone, and there is no instrument here. An
instrument for each GSS year is planned.

## Universes we wrote

Most universes quote the codebook's filter. Five are ours, worked out from the order of
the questions: `born_outside_us` and `other_language_speakers` (each follows the question
that decides it), `self_employed`, and `has_supervisor` and `supervises_someone` (each an
"IF YES" to the question before it).

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

These two are left out because the 2022 codebook can't source them:

- **WRKGOVT** isn't in it; WRKGOVT1 and WRKGOVT2 replace it.
- **RINCOME**'s label there is the wording of the question before it ("Did you earn any
  income from …"), while its codes are 12 groups of earnings, so it has no wording to
  copy for those codes. RINCOM16 asks about earnings in 26 groups.

Some pairs are kept although they're alike, each marked `variant_of`: INCOME and
INCOME16 (12 and 26 groups), POSSLQ and POSSLQY (the two forms of a wording experiment),
and the second and third mentions of one question (RACECEN, ETH, OTHLANG, MAJOR).

## Known findings

`qretools check` gives two notes: SIBS and WEEKSWRK may ask about two things at once.
That's GSS's wording, so it stays. It also gives one pair of warnings: the shared
scales `yes_no` and `yes_no_3_4` have the same labels. GSS codes yes and no as 3 and 4
for WKSUBS1 and WKSUPS1, and a shared scale can't yet say it's alike on purpose.
