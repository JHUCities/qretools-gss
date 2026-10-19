# GSS Replicating Core: an example QREtools workspace

The Demographic and Work/employment items of the General Social Survey's Replicating
Core, as listed in [The GSS Replicating Core, current as of 2020](https://gss.norc.org/content/dam/gss/get-documentation/pdf/other/2020%20GSS%20Replicating%20Core.pdf)
("Demographic and life-course data" and "Work/employment data"), one YAML file per
question. Bootstrapped from [qretools-template](https://github.com/JHUCities/qretools-template): its
`workspace.yaml`, layout and conventions.

An example, not a publication of NORC's: it is published under JHU's DDI agency, `us.jhu`
(requested from the DDI Alliance on 2026-10-19). The GSS items
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

`tools/generate.py` writes `questions/`, `scales/`, `universes/`, `concepts/` and `units/`
from `gss_doc` (gssrdoc is MIT-licensed); edit its spec and rerun it rather than the files, while this stays an
import.

## Universes inferred from question order

Most universes quote the filter in GSS's wording. These are read from the order of the
questions instead: `other_language_speakers` (follows OTHLANG), `earned_income`,
`has_supervisor` and `supervises_someone` (each an "IF YES" to the question before).

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
