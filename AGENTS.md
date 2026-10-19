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
- **From a terminal:** the `qretools` CLI is in [JHUCities/qretools](https://github.com/JHUCities/qretools)
  (`v2/packages/cli`, Node 26, `pnpm install` in `v2/`). From `v2/`:

  ```sh
  pnpm qretools check ../../qretools-gss          # findings, one per line
  pnpm qretools export ../../qretools-gss -o gss.json   # DDI-Lifecycle 4.0 JSON
  ```

  Use whatever path leads to this checkout. The CLI's own guide for agents is
  `v2/packages/cli/AGENTS.md` there.

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
