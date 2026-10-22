# Licence

This repository holds two kinds of material, under different terms, and most files mix
them.

## NORC's material: not licensed by us

The General Social Survey's material here is NORC's (NORC at the University of
Chicago), wherever it appears, including inside `tools/generate.py`:

- question wording and interviewer instructions;
- response codes and labels, missing-value labels, and released-data labels quoted in notes;
- variable names, titles and descriptions;
- the filters quoted in universes;
- the category names used as concept labels.

Most came through [gssrdoc](https://github.com/kjhealy/gssrdoc) (the GSS Data Explorer's
documentation), whose MIT licence covers that package, not NORC's content. The concept
labels are from "The GSS Replicating Core, current as of 2020", and `uscitzn`'s wording
is from the 2022 GSS codebook.

NORC's terms (<https://gss.norc.org/terms-and-conditions>) say: "No part of the contents
of NORC websites may be reproduced, stored, or transmitted in any form or by any means,
electronic or mechanical, in whole or in any part, without the express written consent
of NORC." Nothing here licenses NORC's material to you; permission requests go to
commhelp@norc.org.

The General Social Survey (GSS) is a project of the independent research organization
NORC at the University of Chicago, with principal funding from the National Science
Foundation. NORC offers the data and documentation "as is", with no warranty.

## Our own work

© 2026 Johns Hopkins University. Our own work is what we added around NORC's material.
Some examples:

- the intents' wording around NORC's descriptions;
- the `{{fill}}` placeholders and fill names;
- the instruction and note text we added;
- the universes inferred from question order;
- the names of scales, universes and concepts;
- the `variant_of` reasons;
- the workspace's layout and configuration;
- the README and AGENTS.md.

It's under these licences:

- **Code** (`tools/`) is under the MIT License (`LICENSES/MIT.txt`), except the NORC
  material written into it, listed above.
- **Everything else of ours** is under Creative Commons Attribution 4.0 International
  (CC BY 4.0, `LICENSES/CC-BY-4.0.txt`). Credit "qretools-gss, Johns Hopkins
  University", with a link to the licence.
