# Working in this workspace

A QREtools workspace holding the GSS Replicating Core's Demographic and Work items
(scope and provenance: `README.md`). Read this before changing anything.

## The one rule: it's generated

`questions/`, `scales/`, `universes/`, `concepts/`, `units/` and `missing.yaml` are
written by `tools/generate.py` from `sources/gss-2022-codebook.json`, which
`tools/extract.py` writes from the GSS 2022 codebook. Don't edit those files by hand:
change the `SPEC` (or another table) in `tools/generate.py` and regenerate, so the
import can always be rerun. `workspace.yaml`, `README.md`, `LICENSE.md` and this file
are written by hand.

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
  `dist/`: the DDI to <https://jhucities.github.io/qretools-gss/ddi.json>, with
  `LICENSE.md` beside it, because the DDI holds NORC's material. Locally,
  `qretools build .` writes it to `dist/`, which is gitignored. It builds the last
  commit; commit first.

**What `check` should say:** `0 with something to fill in or fix`, with these known
findings and nothing else:
- `double-barreled` notes on `sibs` and `weekswrk`: GSS's wording, kept;
- one `duplicate-scale` warning pair, `yes_no` against `yes_no_3_4`: GSS codes
  WKSUBS1 and WKSUPS1 yes/no as 3/4, and a scale can't yet be marked alike on purpose.

## Regenerate

You need Python 3 and the 2022 codebook PDF ("GSS 2022 Codebook.pdf", Release 4, from
the URL in `tools/extract.py`). Do not commit the PDF.

1. Make an environment for the extractor:
   `python3 -m venv .venv && .venv/bin/pip install pypdf`
2. Extract the entries from the codebook:
   `.venv/bin/python -I tools/extract.py "<path to GSS 2022 Codebook.pdf>" sources/gss-2022-codebook.json`
3. Remove the generated folders:
   `rm -rf questions scales universes concepts units`
4. Write the workspace:
   `python3 -I tools/generate.py`
5. Run `qretools check .`.

- **Step 3 is necessary.** The generator overwrites files, but it does not delete a
  file. Without step 3, a renamed or dropped item stays.
- **The generator stops if a text is not in the codebook.** Each text and instruction in
  `SPEC` must be a span of the codebook's label. If the generator stops, correct the
  `SPEC` entry. Do not change the JSON by hand.
- **Expected result:** with the same codebook, `git status` shows no changes. If NORC
  publishes a new release of the codebook, examine the diff before you commit it.
- **Do not commit `.venv`:** it is gitignored.

## Add or change an item

1. **Find it** in the 2022 codebook. Add its variable to `VARIABLES` in
   `tools/extract.py`, then run step 2 above.
2. **Add a `SPEC` entry** keyed by the question's name, giving its folder, its concept
   (a key of `CONCEPTS`), its title (ours) and its fields:
   - `text`: only what's read to the respondent, a span of the codebook's label, or a
     tuple of spans in the label's order where routing ("IF YES:") sits between them;
   - `universe`: an "IF …" filter, as a key of `UNIVERSES`;
   - `instruction`: interviewer directions, a span of the label;
   - `fills`: the codebook's stand-ins, written `{{name}}` in the text;
   - `number`: a unit, or `None`, for numeric items;
   - `scale`: a key of `SCALES`, when the list is shared;
   - `variant_of`: why it deliberately resembles another item;
   - `gss`: the GSS variable, when the question's name differs from it.
3. **Regenerate**, then `check`.

What's generated without you asking: `intent`, `responses`, `source` and the codebook's
full label and notes in `note`.

## Rules for content

- **NORC's material comes only from the 2022 codebook.** Never take wording, codes or
  labels from NORC's website, the GSS Data Explorer or a package that copies them: the
  website's terms forbid it. A newer codebook may be added only with its own permission
  notice, recorded in `LICENSE.md`.
- **Every file with NORC's material keeps the notice comment** that `tools/generate.py`
  writes at its top.
- **Never invent or paraphrase wording.** Where the codebook has none, leave the item out
  and say so in `README.md`. Titles, intents and concept labels are ours, in our own words.
- **No counts or percentages.** They come from the data, not the questionnaire.
- **Only items asked of the respondent.** Recodes, derived variables, geocoded
  variables and interviewer-coded items with no respondent wording stay out. Add each
  exclusion to `README.md`'s "Left out" list.
- **Scope is Demographics and Work only.** The rest of the Replicating Core is out of
  scope until the owner widens it (`README.md`, "Scope").
- **The agency is `us.jhu`**, JHU's DDI agency, registered with the DDI Alliance on
  2026-10-19. Don't change it, and don't add a sub-agency, without the owner.
