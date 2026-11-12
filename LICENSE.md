# Licence

This repository holds two kinds of material, under different terms, and most files mix
them.

## NORC's material: from two GSS codebooks, under the 2022 codebook's notice

The General Social Survey's material here is NORC's (NORC at the University of
Chicago). From release `v3` on, all of it comes from two sources:

- the [GSS 2022 codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf)
  (Release 4, November 21, 2024), which carries the notice below;
- the [GSS 1972-2018 cumulative codebook](https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS_Codebook_mainbody.pdf)
  (main body, December 2019), used from the replay of 2008 on. It carries no notice of
  its own. By the owner's decision of 2026-11-12, the 2022 codebook's notice is applied
  to it. That is our decision, not a grant from NORC.

The material is:

- question wording and interviewer instructions, word for word;
- response codes and their labels, and the reserved (missing-value) codes;
- variable names;
- the filters quoted in universes;
- the codebook's labels and notes, quoted in each question's `note`.

It's in these files:

- `sources/gss-2022-codebook.json`, the entries `tools/extract.py` takes from the 2022
  codebook, and `missing.yaml`;
- `sources/gss-1972-2018-codebook.json`, the entries `tools/extract_cumulative.py` takes
  from the cumulative codebook, which carries the notice below and says it is applied;
- `questions/` and `scales/`;
- `universes/`, except those we wrote (listed in `README.md`: `born_outside_us`,
  `other_language_speakers`, `self_employed`, `has_supervisor` and `supervises_someone`);
- `tools/generate.py`, whose `SPEC` holds spans of the codebooks' wording.
- `instruments/`, whose comments and input descriptions quote the cumulative codebook's
  variable names and routing notes.

The 2022 codebook carries this notice, which applies to that material here (from both
codebooks) and to any copy of it. It is quoted as printed, with its spacing and quotation marks made plain:

> Copyright 2021-2024 NORC
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this codebook, portions thereof, and the associated documentation (the "codebook"), to use the codebook, including, without limitation, the rights to use, copy, modify, merge, publish, and distribute copies of the codebook, and to permit persons to whom the codebook is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or portions of the codebook. Any distribution of the codebook must be free of charge to the recipient, except for charges to recover duplicating costs.
>
> The codebook is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of, or in connection with the codebook or the use or other dealings in the codebook.

We don't license NORC's material to you: the notice above does. It doesn't cover the
rest of NORC's website, whose terms (<https://gss.norc.org/terms-and-conditions>) forbid
copying without NORC's written consent. Nothing from the website is in `v3` or later,
but earlier commits and the tags `v1` and `v2` hold material taken from it (through the
GSS Data Explorer's documentation), which this notice doesn't cover.

**Where the notice travels.** This file holds the notice for every file listed above; a
copy of such a file should take this file with it. The files published on GitHub Pages hold NORC's material
too: the DDI (`ddi.json`), and each instrument's DDI, Qualtrics survey and QSF column map
in `instruments/`. So the workflow publishes this file beside them, as `LICENSE.md`, and
each release's folder (`v3/`, `v4/`, …) carries that release's own `LICENSE.md`. The
tags `v1` and `v2` are never published.

The General Social Survey (GSS) is a project of the independent research organization
NORC at the University of Chicago, with principal funding from the National Science
Foundation.

## Our own work

© 2026 Johns Hopkins University. Our own work is what we added around NORC's material.
Some examples:

- the titles, intents and concept labels;
- the `{{fill}}` placeholders and fill names;
- the universes we wrote, listed above;
- the tools' rules for reading the codebooks (which rows are missing values, which lines
  are wording);
- the names of scales, universes and concepts;
- the `variant_of` reasons;
- the workspace's layout and configuration;
- the tools, the README and AGENTS.md.

It's under these licences:

- **Code** (`tools/`) is under the MIT License (`LICENSES/MIT.txt`), except the NORC
  material written into it, listed above.
- **Everything else of ours** is under Creative Commons Attribution 4.0 International
  (CC BY 4.0, `LICENSES/CC-BY-4.0.txt`). Credit "qretools-gss, Johns Hopkins
  University", with a link to the licence. NORC's material is not under CC BY.
