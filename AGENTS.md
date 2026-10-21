# Working in this workspace

A QREtools workspace holding the GSS Replicating Core's Demographic and Work items
(scope and provenance: `README.md`). Read this before changing anything.

## The one rule: it's generated

`questions/`, `scales/`, `universes/`, `concepts/` and `units/` are written by
`tools/generate.py` from kjhealy/gssrdoc's `gss_doc`. Don't edit those files by hand:
change the `SPEC` (or another table) in `tools/generate.py` and regenerate, so the
import can always be rerun. `workspace.yaml`, `missing.yaml`, `README.md` and this file
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

- **The workspace's version is its tag.** Instruments read `JHUCities/qretools-gss@v1`;
  release a new tag (`v2`, …) for any change instruments should see, with the Release
  workflow (Actions → Release), never by hand: its tag carries each question's DDI version.
  Never move or delete a tag.
- **Each item's version is counted, never written.** `qretools build` counts each file's
  changes along `main`'s history; a question also moves when a shared file it names
  does. Never rewrite `main`'s history: versions would restart.
- **On every push to `main`,** `.github/workflows/ddi.yml` runs `build` and deploys
  `dist/ddi.json` to <https://jhucities.github.io/qretools-gss/ddi.json>. Locally,
  `qretools build .` writes it to `dist/`, which is gitignored. It builds the last commit; commit first.

**What `check` should say:** `0 with something to fill in or fix`, with these known
findings and nothing else:
- `double-barreled` notes on `sibs` and `weekswrk`: GSS's wording, kept;
- one `duplicate-scale` warning pair, `yes_no` against `yes_no_3_4`: GSS codes
  WKSUBS1 and WKSUPS1 yes/no as 3/4, and a scale can't yet be marked alike on purpose.

Any other finding after a change is yours to fix.

## Regenerate

```sh
python3 -m venv .venv && .venv/bin/pip install rdata pandas
curl -L -o gss_doc.rda https://raw.githubusercontent.com/kjhealy/gssrdoc/main/data/gss_doc.rda
.venv/bin/python -I -c "import rdata, pickle, sys; d = rdata.conversion.convert(rdata.parser.parse_file(sys.argv[1]), default_encoding='utf8'); pickle.dump(d['gss_doc'], open(sys.argv[2], 'wb'))" gss_doc.rda gss_doc.pkl 2>/dev/null
rm -rf questions scales universes concepts units
.venv/bin/python -I tools/generate.py gss_doc.pkl .
```

- **Clear the folders first:** the generator overwrites files but never deletes one, so
  a renamed or dropped item would linger. That's what the `rm -rf` is for.
- **`rdata` is noisy:** it prints many `Missing constructor` warnings while converting.
  They're harmless, and the `2>/dev/null` hides them.
- **Expected result:** with gssrdoc unchanged, `git status` shows no changes. If
  gssrdoc has been updated, review the diff before committing; wording and labels can
  change upstream.
- **Don't commit the downloads:** `.venv`, `gss_doc.rda` and `gss_doc.pkl` are
  gitignored.

## Add or change an item

1. **Look it up** in `gss_doc` (`variable` is the lowercase GSS mnemonic):
   - `question` is the wording;
   - `value_labels` gives the codes;
   - `norc_url` is the GSS Data Explorer page.
2. **Add a `SPEC` entry** keyed by the question's name, giving its folder, its concept
   (a key of `CONCEPTS`) and its fields:
   - `text`: only what's read to the respondent;
   - `universe`: an "IF …" filter, as a key of `UNIVERSES`;
   - `instruction`: interviewer directions;
   - `fills`: GSS's parenthetical substitutions, written `{{name}}` in the text;
   - `number`: a unit, or `None`, for numeric items;
   - `scale`: a key of `SCALES`, when the list is shared;
   - `variant_of`: why it deliberately resembles another item;
   - `gss`: the mnemonic, when `gss_doc` spells it differently from the 2020 document.
3. **Regenerate**, then `check`.

What's generated without you asking: `title`, `responses`, `source` and the verbatim
wording in `note`.

## Rules for content

- **Every value has a source.** Wording, codes and labels come from `gss_doc`, or from
  a GSS codebook named in `note`. Never invent or paraphrase wording. Where a source
  has none, leave the item out and say so in `README.md`.
- **The original stays readable.** `text` may be cut down to what's read aloud, but
  `note` keeps `gss_doc`'s full wording verbatim.
- **Only items asked of the respondent.** Recodes, derived variables, geocoded
  variables and interviewer-coded items with no respondent wording stay out. Add each
  exclusion to `README.md`'s "Left out" list.
- **Scope is Demographics and Work only.** The rest of the Replicating Core is out of
  scope until the owner widens it (`README.md`, "Scope").
- **The agency is `us.jhu`**, JHU's DDI agency, registered with the DDI Alliance on
  2026-10-19. Don't change it, and don't add a sub-agency, without the owner.
