"""Extract the entries this workspace uses from NORC's 2022 GSS codebook.

Usage: python -I tools/extract.py <codebook.pdf> sources/gss-2022-codebook.json
Needs pypdf. <codebook.pdf> is "GSS 2022 Codebook.pdf" (Release 4), from
https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf

The codebook's permission notice lets anyone use, copy, modify, publish and distribute
it, free of charge, with its copyright notice and permission notice in every copy or
portion. The output carries both (NOTICE). It holds, for each variable: its label, its
notes, its codes and their labels, and its reserved codes. Counts and percentages are
left out. Where the codebook shows ranges ("collapsed for convenience of display"), no
codes are kept: those rows are display bins, not codes. Review the output's diff before
committing it.
"""
import json
import re
import sys

from pypdf import PdfReader

VARIABLES = """
racecen1 racecen2 racecen3 race eth1 eth2 eth3 hispanic sibs marital widowed divorce
posslq posslqy childs agekdbrn major1 major2 relig denom other jew reliten income
income16 uscitzn fucitzn mnthsusa yearsusa othlang othlang1 othlang2 betrlang spklang
wrkstat evwork wrkslffam whatslf2 wrkgovt1 wrkgovt2 numemps hrs1 hrs2 weekswrk partfull
rincom16 localnum wksub1 wksubs1 wksup1 wksups1 vetyears
""".split()

NOTICE = """Copyright 2021-2024 NORC
Permission is hereby granted, free of charge, to any person obtaining a copy of this codebook, portions thereof, and the associated documentation (the "codebook"), to use the codebook, including, without limitation, the rights to use, copy, modify, merge, publish, and distribute copies of the codebook, and to permit persons to whom the codebook is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or portions of the codebook. Any distribution of the codebook must be free of charge to the recipient, except for charges to recover duplicating costs.
The codebook is provided "as is," without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of, or in connection with the codebook or the use or other dealings in the codebook."""

HEADER = re.compile(r"^(General Social Survey Codebook Produced on|Codebook and Unweighted Frequencies)")
SKIP = {"LABEL VALUE COUNT PCT", "PCT", "Excl.", "Reserve", "Codes", "PCT Excl.", "RESERVED CODES:"}
VALUE = re.compile(r"^(.*?) ?(-?\d+(?:\.\d+)?) \d+ [\d.]+% (?:[\d.]+%|n/a)$")
RESERVED = re.compile(r"^(.+) ([A-Z]) \d+ [\d.]+% n/a$")


def lines_of(pdf):
    """Each line of the codebook with its page, page headers left out."""
    for number, page in enumerate(PdfReader(pdf).pages, 1):
        rows = (page.extract_text() or "").splitlines()
        # A page opens with two header lines, the section's name and "Page N".
        start = next((i + 2 for i, r in enumerate(rows[:6]) if re.match(r"^Page \d+$", rows[i + 1] if i + 1 < len(rows) else "")), 0)
        for row in rows[start:]:
            row = row.strip()
            if row and not HEADER.match(row):
                yield number, row


def entries(pdf):
    """Each variable's entry; one that runs over a page is one entry, its header repeated."""
    out, current = {}, None
    for page, row in lines_of(pdf):
        m = re.match(r"^Variable: (\S+)\s+Type: (\S+)", row)
        if m:
            name = m[1].lower()
            if current is not None and current["variable"] == name:
                current["part"] = "header"  # the same entry, continued: its header again
                continue
            current = out.setdefault(name, {"variable": name, "type": m[2], "page": page, "label": [], "notes": [], "codes": [], "reserved": [], "pending": []})
            current["part"] = "label"
            continue
        if current is None:
            continue
        if row.startswith("Label:"):
            if current["part"] == "header":
                current["part"] = "repeat"
                continue
            current["part"] = "label"
            row = row[len("Label:"):].strip()
        elif row.startswith("Notes:"):
            current["part"] = "repeat" if current["part"] == "repeat" else "notes"
            row = row[len("Notes:"):].strip()
        elif row in SKIP or row.startswith("LABEL VALUE"):
            current["part"] = "rows"
            continue
        elif row.startswith(("SUBTOTALS:", "TOTALS:")):
            current["pending"] = []
            continue
        if current["part"] == "repeat" or not row:
            continue
        if current["part"] in ("label", "notes"):
            current[current["part"]].append(row)
            continue
        r = RESERVED.match(row)
        if r and not VALUE.match(row):
            current["reserved"].append({"code": r[2], "label": " ".join(current["pending"] + [r[1]])})
            current["pending"] = []
            continue
        v = VALUE.match(row)
        if v:
            current["codes"].append({"code": v[2], "label": " ".join(current["pending"] + [v[1]]).strip()})
            current["pending"] = []
        else:
            current["pending"].append(row)
    for e in out.values():
        e["label"] = " ".join(e["label"])
        e["notes"] = " ".join(e["notes"])
        if "collapsed for convenience of display" in e["notes"]:
            e["codes"] = []
        for k in ("part", "pending"):
            e.pop(k)
    return out


def main(pdf, path):
    found = entries(pdf)
    missing = [v for v in VARIABLES if v not in found]
    if missing:
        sys.exit(f"Not in the codebook: {', '.join(missing)}")
    doc = {
        "source": "General Social Survey 2022 codebook, Release 4 (NORC, November 21, 2024)",
        "url": "https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202022%20Codebook.pdf",
        "notice": NOTICE,
        "entries": {v: found[v] for v in VARIABLES},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(len(VARIABLES), "entries")


if __name__ == "__main__":
    main(*sys.argv[1:])
