# GSS Replicating Core: an example QREtools workspace

The Demographic and Work/employment items of the General Social Survey's Replicating
Core, as listed in [The GSS Replicating Core, current as of 2020](https://gss.norc.org/content/dam/gss/get-documentation/pdf/other/2020%20GSS%20Replicating%20Core.pdf)
("Demographic and life-course data" and "Work/employment data"), one YAML file per
question. Bootstrapped from [qretools-template](https://github.com/JHUCities/qretools-template): its
`workspace.yaml`, layout and conventions.

An example, not a publication of NORC's: it is published under JHU's DDI agency, `us.jhu`
(registered with the DDI Alliance on 2026-10-19). The GSS items
themselves are NORC's.

**Scope.** A start on the GSS, from its Replicating Core, deliberately limited to two
packages: Demographics and Work. The rest of the core (spouse/partner, parental and
social origin, household, technical and paradata, and the attitude items on every
ballot) is out of scope for now, not missed.

## Where each value comes from

| Field | Source |
|---|---|
| `title`, `responses` codes and labels, `source` URL | [kjhealy/gssrdoc](https://github.com/kjhealy/gssrdoc) `gss_doc` (GSS Data Explorer documentation, as of 2024), lower-case labels re-capitalized |
| `text` | `gss_doc`'s question wording, with the parts that aren't read to the respondent moved out: the "IF …" filter to `universe`, interviewer directions to `instruction`, GSS's parenthetical substitutions (`(PREFERENCE NAMED IN RELIG)`, `[the previous year]`) to `fills` |
| `note` | `gss_doc`'s full wording verbatim, so nothing moved out is lost; for numbers, the top-codes of the released data |
| `concept` | the 2020 document's category names (`concepts/`) |
| `missing.yaml` | the reserved codes `gss_doc` lists for every variable |

`uscitzn`'s wording is from the [2022 GSS codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf),
as `gss_doc` gives only a description. Three names differ from the 2020 document's
spelling in `gss_doc`: `divorced` is GSS `DIVORCE`, `wrkselffam` is `WRKSLFFAM`, `yrsusa`
is `YEARSUSA` (each question's `source` names the GSS variable).

How to open, check, regenerate and extend it: [AGENTS.md](AGENTS.md).
Its DDI, each item versioned from this history, is published on every push to `main` at
<https://jhucities.github.io/qretools-gss/ddi.json>.
An instrument uses it at a release tag (`uses: gss: JHUCities/qretools-gss@v1`), and gets
the questions as they were at that tag: changes merged into `main` reach it only when a new
tag is released and the instrument's author changes `@v1` to it.

There are two version numbers. The tag (`v1`, `v2`) is this workspace's version, chosen by
whoever releases it. Each question's DDI version (the `2` in `urn:ddi:us.jhu:agekdbrn:2`)
counts the changes to it merged into `main`, so between two tags it can go up by more than
one.

Make a release with the Release workflow (Actions → Release → Run workflow, with the next
tag, such as `v2`): it tags `main`'s last commit with each question's DDI version in the
tag's message, so an instrument reading the tag gets those versions. Never make, move or
delete a tag by hand. `v1` was tagged by hand, before the workflow existed, so its questions read
as version 1; `v2` is the first release that carries versions.

`tools/generate.py` writes `questions/`, `scales/`, `universes/`, `concepts/` and `units/`
from `gss_doc` (gssrdoc is MIT-licensed); edit its spec and rerun it rather than the files, while this stays an
import.

## Universes inferred from question order

Most universes quote the filter in GSS's wording. These are read from the order of the
questions instead: `other_language_speakers` (follows OTHLANG), `earned_income`,
`has_supervisor` and `supervises_someone` (each an "IF YES" to the question before).

## The instrument

`instruments/replicating_core.yaml` asks these questions in the document's order, with the routing the
documentation gives: the "IF ..." filter that became each question's `universe` on import
is here the condition that decides whether the question is asked. It is written by hand,
because the routing is not in `gss_doc`.

Three filters are questions this workspace doesn't hold, its scope being Demographics and
Work: GSS BORN (before citizenship and time in the US), GSS WRKSLF (before NUMEMPS) and
GSS's "did you earn any income from <occupation>" (before RINCOME). They are `inputs`, so
the routing is complete and what it rests on is named rather than assumed. Four more
inputs carry values GSS reads aloud that this workspace doesn't hold either: the year the
income and work questions ask about, the degree named in the field-of-study question, the
word "Latina" or "Latino", and the occupation named in the earnings question. The one
read-aloud value the bank does hold is the religious preference, which the
strength-of-affiliation question fills with `label(gss.relig)`.

Where the bank holds several versions of one question, the instrument asks one: the first
of GSS's up-to-three mentions (RACECEN1, ETH1, OTHLANG1, MAJOR1), the current version of
a pair (INCOME, RINCOME, POSSLQ, DENOM, YRSUSA, and WRKGOVT1 with WRKGOVT2). Each
omission is named in a comment at the top of the file. Recording three mentions of one
question is not something the surface can say; asking all three would be three questions.

Measured: `qretools instrument check` reports nothing, the DDI and the Qualtrics (QSF)
exports are both clean, and `qretools paths` counts 1,024 ways through the routing, 28 to
40 questions each (median 34), with every question reachable.

One thing the instrument can't fix: GSS surely asks DENOM only of Protestants and JEW only
of Jews, but `gss_doc` documents them as follow-ups ("A.", "B.") without stating the
filter, so no universe was imported and the instrument asks them of everyone. Writing the
conditions here would put routing in the instrument that the bank doesn't declare. The
source that would settle it is the GSS questionnaire itself, and it belongs in the import.

**Nothing reports that gap.** A question with no universe, asked with no condition, falls
back to the instrument's own universe, so `check` is silent and so is the paths report.
This paragraph is the only record until the universe check exists, which is why the rule
is written down in AGENTS.md as well.

## Left out

The 2020 document lists these in the two sections but they are not questions asked of
the respondent:

- **Recodes and derived variables** (marked so in the document): AGE, ZODIAC, ETHNIC,
  EDUC, DEGREE, FUND, CONINC, REALINC, INDUS10, OCC10, ISCO08, PRESTG10, PRESTG105PLUS,
  SEI10, SEI10EDUC, SEI10INC, CONRINC, REALRINC. COHORT and MARTYPE too: `gss_doc`
  describes them as derived (birth cohort; coded from the Household Enumeration Form).
- **Geocoded from the address**: REGION, XNORCSIZ, SRCBELT, SIZE.
- **Interviewer-coded with no respondent wording**: SEX ("CODE RESPONDENT'S SEX").

Kept although alike: INCOME and INCOME16, RINCOME and RINCOM16 (12- and 26-category
versions), POSSLQ and POSSLQY (the X/Y wording experiment), each marked `variant_of`.
WRKGOVT is last fielded in 2018 per `gss_doc`; WRKGOVT1 and WRKGOVT2 replace it.

## Known findings

`qretools check` reports two notes (SIBS and WEEKSWRK may be double-barreled: GSS's
wording, kept) and one warning pair: `yes_no` and `yes_no_3_4` have the same labels.
GSS codes WKSUBS1 and WKSUPS1 yes/no as 3/4, and a scale can't yet say it's alike on
purpose.
