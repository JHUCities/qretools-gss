# GSS Replicating Core: an example QREtools workspace

The demographic and work questions of the General Social Survey's Replicating Core, one
YAML file per question. The list comes from
[The GSS Replicating Core, current as of 2020](https://gss.norc.org/content/dam/gss/get-documentation/pdf/other/2020%20GSS%20Replicating%20Core.pdf)
(its "Demographic and life-course data" and "Work/employment data" sections). The
workspace started from [qretools-template](https://github.com/JHUCities/qretools-template)
and keeps its layout and conventions.

This is an example, not a NORC publication. It's published under JHU's DDI agency,
`us.jhu` (registered with the DDI Alliance on 2026-10-19).

**Licence.** The GSS questions are NORC's, under NORC's terms; we don't license them.
Our own work here is MIT (code) and CC BY 4.0 (everything else).
[LICENSE.md](LICENSE.md) says which is which.

**Scope.** Only two parts of the Replicating Core, on purpose: demographics and work.
The rest (spouse or partner, parents and family background, household, technical data
and paradata, and the attitude questions on every ballot) is left for later, not missed.

## Where each field comes from

| Field | Source |
|---|---|
| `title`, `responses` codes and labels, `source` URL | [kjhealy/gssrdoc](https://github.com/kjhealy/gssrdoc)'s `gss_doc` (the GSS Data Explorer's documentation, as of 2024), with lower-case labels given capitals again |
| `text` | `gss_doc`'s question wording, without the parts that aren't read to the respondent: the "IF …" filter goes to `universe`, directions to the interviewer go to `instruction`, and GSS's stand-ins such as `(PREFERENCE NAMED IN RELIG)` and `[the previous year]` go to `fills` |
| `note` | `gss_doc`'s full wording, word for word, so nothing taken out is lost; for numbers, the top codes of the released data |
| `concept` | the 2020 document's category names (`concepts/`) |
| `missing.yaml` | the reserved codes `gss_doc` lists for every variable |

`uscitzn`'s wording comes from the [2022 GSS codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf),
because `gss_doc` gives only a description. Three names follow the 2020 document's spelling, not `gss_doc`'s:
`divorced` is GSS `DIVORCE`, `wrkselffam` is `WRKSLFFAM` and `yrsusa` is `YEARSUSA`.
Each question's `source` names the GSS variable.

[AGENTS.md](AGENTS.md) says how to open, check, regenerate and extend the workspace.

## Its DDI and its releases

Every push to `main` publishes the workspace's DDI at
<https://jhucities.github.io/qretools-gss/ddi.json>.

An instrument uses a release of this workspace, named by its tag:
`uses: gss: JHUCities/qretools-gss@v1`. It gets the questions as they were at that tag.
Changes merged into `main` reach it only after a new release, when the instrument's
author changes `@v1` to the new tag.

There are two version numbers:

- The tag (`v1`, `v2`) is the version of the whole workspace. Whoever makes the release
  chooses it.
- Each question's DDI version (the `2` in `urn:ddi:us.jhu:agekdbrn:2`) counts the changes
  to that question merged into `main`. Between two tags it can go up by more than one.

To make a release, run the Release workflow (Actions → Release → Run workflow) with the
next tag, such as `v2`. It tags the last commit on `main` and writes each question's DDI
version into the tag's message, so an instrument reading the tag gets those versions.
Never make, move or delete a tag by hand. `v1` was tagged by hand, before the workflow
existed, so its questions all read as version 1. `v2` is the first release that carries
versions.

## Regenerating it

`tools/generate.py` writes `questions/`, `scales/`, `universes/`, `concepts/` and
`units/` from `gss_doc` (gssrdoc is MIT-licensed). While this workspace is still an
import, change the spec in the script and run it again, rather than editing the files.

## Universes taken from question order

Most universes quote GSS's own filter. A few are worked out from the order of the
questions instead: `other_language_speakers` (follows OTHLANG), and `earned_income`,
`has_supervisor` and `supervises_someone` (each an "IF YES" to the question before it).

## Left out

The 2020 document lists these in the two sections, but they aren't questions put to
the respondent:

- **Recodes and derived variables** (marked so in the document): AGE, ZODIAC, ETHNIC,
  EDUC, DEGREE, FUND, CONINC, REALINC, INDUS10, OCC10, ISCO08, PRESTG10, PRESTG105PLUS,
  SEI10, SEI10EDUC, SEI10INC, CONRINC, REALRINC. Also COHORT and MARTYPE, which
  `gss_doc` describes as derived (birth cohort; coded from the Household Enumeration
  Form).
- **Taken from the address**: REGION, XNORCSIZ, SRCBELT, SIZE.
- **Coded by the interviewer, with no wording for the respondent**: SEX ("CODE
  RESPONDENT'S SEX").

Some pairs are kept although they're alike, each marked `variant_of`: INCOME and
INCOME16, and RINCOME and RINCOM16 (12- and 26-category versions), and POSSLQ and
POSSLQY (the two forms of a wording experiment). WRKGOVT was last asked in 2018,
according to `gss_doc`; WRKGOVT1 and WRKGOVT2 replace it.

## Known findings

`qretools check` gives two notes: SIBS and WEEKSWRK may ask about two things at once.
That's GSS's wording, so it stays. It also gives one pair of warnings: the shared
scales `yes_no` and `yes_no_3_4` have the same labels. GSS codes yes and no as 3 and 4
for WKSUBS1 and WKSUPS1, and a shared scale can't yet say it's alike on purpose.
