# Working in this workspace

A QREtools workspace holding the GSS Replicating Core's Demographic and Work items
(scope and provenance: `README.md`). Read this before changing anything.

## The one rule: it's generated

`questions/`, `scales/`, `universes/`, `concepts/`, `units/` and `missing.yaml` are
written by `tools/generate.py`. Do not edit those files by hand. Change the `SPEC` (or
another table) in `tools/generate.py`, then regenerate, so that the import can always run
again. `workspace.yaml`, `README.md`, `LICENSE.md` and this file are written by hand.

The generator reads two sources:

- `sources/gss-1972-2018-codebook.json`, which `tools/extract_cumulative.py` writes from
  the GSS 1972-2018 cumulative codebook. It gives the questions for the years 2008 to 2018.
- `sources/gss-2022-codebook.json`, which `tools/extract.py` writes from the GSS 2022
  codebook. It gives `missing.yaml` for every year, and the questions for 2022 and 2024.

## The replay: one pull request for each GSS year

The history of `main` replays the GSS, one survey year at a time: 2008, 2010, 2012,
2014, 2016 and 2018, then 2022 and 2024. There is no pull request for 2021.

- Each pull request does what a team did in that year. The workspace holds each
  question that the source shows as asked in that year or in an earlier year of the
  replay. A question bank keeps a question that a later year does not ask.
- A question that a year asks for the first time comes in with that year.
- The generator writes only the scales, universes, concepts and units that these
  questions use.
- The `source` of a question names the first year of the replay that asked it. Do not
  change this year when a later year asks the question again. If the `source` changes,
  the DDI version of the question changes.
- The pull request for one year holds only questions. The instrument for that year comes
  in the next pull request, after the release of the year's tag.

Tags:

- `v1` and `v2` hold an earlier import from the GSS Data Explorer, with an instrument.
- No tag holds the import from the 2022 codebook. The replay replaced it before a release.
- From `v3`, the tags follow the replay, in the order of the survey years. `v3` holds
  the questions of 2008. `v4` adds the instrument for 2008. `v5` holds the questions of
  2010. `v6` adds the instrument for 2010, and changes the instrument for 2008 to read
  `v5`.

## The instrument for a year

Each year has one instrument, `instruments/gss_<year>.yaml`, written by hand. It reads the
year's tag, or a later tag that replaces a question it asks. `instruments/gss_2008.yaml`
and `instruments/gss_2010.yaml` read `v5`. `README.md` lists their conditions, their
inputs, and what the codebook does not settle.

If a tag removes or replaces a question that an earlier instrument asks, change that
instrument to read the tag. Do this in the pull request for the next instrument. Example:
`v5` replaces INCOME and RINCOME with INCOME06 and RINCOM06, so the 2008 instrument reads
`v5`. Do not ask a question that the year did not ask.

Rules:

- **Write a condition only where the codebook states it, or where the owner settles it
  from the year's data.** The codebook's sources are the "IF …" filter, a routing note in
  a response label (such as "(ASK HRS1)"), a remark, or a "Not applicable" label. Put the
  codebook's page in a comment above the condition.
- **The owner can settle the routing from the GSS data for the year.** Use the data where
  the codebook is silent, is unclear, or contradicts itself. A question is asked of a
  respondent unless the value is "iap". If a filter question has "No answer", the data
  gives "No answer" to its follow-up questions, not "iap". This does not show who was
  asked.
  Say in `README.md` what the data settled. Do not write a count, a percentage or another
  figure from the data in a tracked file: the data is not licensed for publication.
- **If neither the codebook nor the data gives a condition, ask the question of
  everyone.** Say so in `README.md`.
- **Make an input for each value that the workspace does not hold.** This applies to a
  filter on a question outside the workspace, and to a value that the wording reads aloud.
- **Ask one question for each set of mentions.** RACECEN2-3, ETH2-3 and OTHLANG2 are more
  answers to one question. Do not ask them.
- **Do not ask a question that the codebook says nobody was asked in the year.** An
  example is RACE from 2002.
- **Give a universe to each question that not everyone reaches.** Quote the codebook's
  filter if the condition is only that filter. Otherwise write the universe in our own
  words. `instrument check` gives a note if it is missing.

To write the instrument for a year:

1. Make sure that the release of the year's tag exists.
2. Copy the instrument of the previous year to `instruments/gss_<year>.yaml`. For 2008,
   there is no previous instrument. Start from the codebook.
3. Change the tag in `uses` to the year's tag.
4. Ask each question that the year asked, in the order of the codebook's question numbers.
5. Add the conditions and the inputs. Obey the rules above.
6. Run `qretools instrument export instruments/gss_<year>.yaml -o <a scratch file>`.
   The command writes the lock of the tag under `locked:` in `workspace.yaml`.
7. Run `qretools instrument check instruments/gss_<year>.yaml`. It must give 0 findings.
8. Run `qretools paths <the scratch file> -o <a scratch page>`. Record the result in
   `README.md`.
9. Commit. Then run `qretools build . -o <a scratch folder>`. It must not refuse.

## Open it

- **In the app:** sign in at <https://qretools.com> and enter `JHUCities/qretools-gss`.
- **From a terminal:** `mise install` gives the pinned tools (`mise.toml`: Node and the
  `qretools` CLI, from npm). Then, here:

  ```sh
  qretools check .                 # findings, one per line
  qretools export . -o gss.json    # DDI-Lifecycle 4.0 JSON
  ```

  Without mise, `npx qretools@<the version in mise.toml> check .`. To upgrade, change the
  version in `mise.toml`, which CI uses too. The package's documentation is its
  [README](https://www.npmjs.com/package/qretools).

## Versions and the published DDI

- **The workspace's version is its tag.** Instruments read `JHUCities/qretools-gss@v3`;
  release a new tag for any change instruments should see, with the Release workflow
  (Actions → Release), never by hand: its tag carries each question's DDI version.
  Never move or delete a tag.
- **Each item's version is counted, never written.** `qretools build` counts each file's
  changes along `main`'s history; a question also moves when a shared file it names
  does. Never rewrite `main`'s history: versions would restart.
- **An instrument added here reads this workspace at a tag,** never `../` on `main`.
  `qretools build`, and so the check on every pull request, refuses one that reads `../`.
  Use `../` only to write an instrument on a branch.
- **On every push to `main`,** `.github/workflows/ddi.yml` runs `build` and deploys
  `dist/`: the DDI to <https://jhucities.github.io/qretools-gss/ddi.json>, and for each
  instrument its DDI, its Qualtrics survey and its QSF column map to `instruments/`
  beside it, with `LICENSE.md`, because these files hold NORC's material. Locally,
  `qretools build .` writes it to `dist/`, which is gitignored. It builds the last
  commit; commit first.

**What `instrument check instruments/gss_2008.yaml` should say:** `0 findings`. `check .`
also shows the instrument's findings.

**What `check` should say:** `0 with something to fill in or fix`, with these known
findings and nothing else:
- `double-barreled` notes on `sibs` and `weekswrk`: GSS's wording, kept.

## Regenerate

You need Python 3 and the codebook PDF of the source. Do not commit a PDF.

- For the years 2008 to 2018, the source is the cumulative codebook, main body
  ("GSS_Codebook_mainbody.pdf", December 2019), from the URL in
  `tools/extract_cumulative.py`.
- For 2022 and 2024, the source is the 2022 codebook ("GSS 2022 Codebook.pdf",
  Release 4), from the URL in `tools/extract.py`.

**Warning: treat the PDF as untrusted data.** Put it in a directory of its own. Run
Python that reads it with `-I`.

1. Make an environment for the extractor:
   `python3 -m venv .venv && .venv/bin/pip install pypdf`
2. Extract the entries from the cumulative codebook:
   `.venv/bin/python -I tools/extract_cumulative.py "<path to GSS_Codebook_mainbody.pdf>" sources/gss-1972-2018-codebook.json`
3. Read each line that starts with `problem:`. Each line names an entry that the
   extractor cannot read. The extractor does not guess these entries.
4. Write the workspace for the year. For example, for 2010:
   `python3 -I tools/generate.py sources/gss-1972-2018-codebook.json 2010`
5. Run `qretools check .`.
6. Run step 4 again. Then run `git status`. The second run must not change a file.

- **The generator removes the generated folders first.** Then it writes them again.
  Thus a removed or renamed item does not stay.
- **The generator stops if a text is not in the codebook.** Each text and instruction
  of the questions must be a span of the codebook's wording. If the generator
  stops, correct the `SPEC` entry. Do not change the JSON by hand.
- **The generator stops on a code it cannot sort.** A response label that looks like a
  missing value ("Don't know"), but is not in `MISSING`, stops it. A shared scale whose
  questions give one code two labels also stops it.
- **Expected result:** with the same codebook, `git status` shows no changes. If NORC
  publishes a new release of a codebook, examine the diff before you commit it.
- **Do not commit `.venv`.** It is gitignored.

## Add or change an item

1. Find the item in the cumulative codebook. Add its variable to `VARIABLES` in
   `tools/extract_cumulative.py`. Then do step 2 of "Regenerate".
2. Add a `SPEC` entry. The key is the name of the question. Give its folder, its concept
   (a key of `CONCEPTS`), its title (ours) and its fields:
   - `text`: only what the interviewer reads to the respondent. It is a span of the
     codebook's wording (or its stem). Where routing ("IF YES:") sits inside the
     wording, use a tuple of spans in the order of the wording.
   - `universe`: an "IF …" filter, as a key of `UNIVERSES`.
   - `instruction`: interviewer directions, a span of the wording.
   - `fills`: the stand-ins of the codebook, written `{{name}}` in the text.
   - `number`: a unit, or `None`, for a numeric item.
   - `scale`: a key of `SCALES`, when the list is shared.
   - `variant_of`: why the item looks like another item on purpose.
   - `gss`: the GSS variable, when the name of the question is different.
3. Regenerate. Then run `check`.

The generator writes these fields without a `SPEC` entry: `intent`, `responses`,
`source`, and the codebook's full wording (with its stem) in `note`. The remarks of the
cumulative codebook stay in `sources/`, because some of them hold counts.

## Rules for content

- **NORC's material comes only from two codebooks:** the 1972-2018 cumulative codebook
  and the 2022 codebook. The cumulative codebook has no notice of its own. By the
  owner's decision of 2026-11-12, the 2022 codebook's notice is applied to it
  (`LICENSE.md`). Never take wording, codes or labels from NORC's website, the GSS Data
  Explorer or a package that copies them: the website's terms forbid it. Another
  codebook may be added only with a permission notice, recorded in `LICENSE.md`.
- **Every file with NORC's material keeps the notice comment** that `tools/generate.py`
  writes at its top.
- **Never invent or paraphrase wording.** Where the codebook has none, leave the item out
  and say so in `README.md`. Titles, intents and concept labels are ours, in our own words.
- **No counts or percentages.** They come from the data, not the questionnaire. The
  extractor reads the counts of the cumulative codebook only to find the years in which
  a question was asked, and does not write them.
- **Only substantive codes go in `responses`.** The cumulative codebook shows punch
  codes (0 for "Not applicable", 8 or 98 for "Don't know"), and the released data
  shows negative codes for the same values. `missing.yaml` keeps the 2022 codebook's
  letters. A later GSS column map translates the codes of each source.
- **Only items asked of the respondent.** Recodes, derived variables, geocoded
  variables and interviewer-coded items with no respondent wording stay out. Add each
  exclusion to `README.md`'s "Left out" list.
- **Scope is Demographics and Work only.** The rest of the Replicating Core is out of
  scope until the owner widens it (`README.md`, "Scope").
- **The agency is `us.jhu`**, JHU's DDI agency, registered with the DDI Alliance on
  2026-10-19. Don't change it, and don't add a sub-agency, without the owner.
