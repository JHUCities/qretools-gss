"""Extract the entries this workspace uses from NORC's GSS 1972-2018 cumulative codebook.

Usage: python -I tools/extract_cumulative.py <main.pdf> sources/gss-1972-2018-codebook.json
Needs pypdf. <main.pdf> is the codebook's main body ("GSS_Codebook_mainbody.pdf",
December 2019), from
https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS_Codebook_mainbody.pdf

The cumulative codebook carries no notice of its own. By the owner's decision of
2026-11-12, the 2022 codebook's permission notice is applied to it, so the output
carries that notice (read from sources/gss-2022-codebook.json) and says so.

Each entry in the PDF is a question (numbered, "115.") or a sub-item ("A."), its
interviewer directions, "[VAR: NAME]", then a table with one row per response: the
label, the punch code and 15 counts, one per column of survey years. The output keeps,
for each variable: the printed page ("Page 543") and the PDF's page, the wording as
printed (lines joined), the stem (the numbered question a lettered sub-item falls under,
up to its first lettered item; kept only while the letters run on in order), the directions, the rows as punch code and label, the
remarks, and the columns in which the question has answers. Counts are read only to
find those columns, and are never written.

- `asked`: the columns (as printed: "1993-98", "2008") where any row other than "Not
  applicable" has a count above 0.
- `directions`: a mechanical list of the runs of words in capitals in the wording. It is
  a convenience only: filters ("IF YES:") and placeholders are capitals too.
- Group headings between rows ("BAPTIST") are dropped. A label that wraps continues on
  an indented line.
- Where the remarks say the rows are "collapsed for convenience of display", or a punch
  code is a range ("1-9"), the rows are display bins, not codes: no rows are kept.
- A row whose counts don't add up to its ALL column has a cell in the wrong column: it
  is a problem. A row with 14 counts has a blank cell, and which column is blank is not
  known: its punch code and label are kept, its counts are never read, and it is a problem.
- Remarks are kept as printed; some of them hold counts.
- What can't be read is never guessed: it goes in the entry's `problems`, and is printed.
"""
import json
import os
import re
import sys

from pypdf import PdfReader

# The GSS variables this workspace takes from the cumulative codebook.
VARIABLES = """
racecen1 racecen2 racecen3 race eth1 eth2 eth3 hispanic sibs marital widowed divorce
posslq posslqy childs agekdbrn major1 major2 relig denom jew reliten income income16
uscitzn fucitzn mnthsusa yearsusa othlang othlang1 othlang2 betrlang spklang wrkstat
evwork wrkslffam wrkgovt numemps hrs1 hrs2 weekswrk partfull rincome rincom16 localnum
wksub1 wksubs1 wksup1 wksups1 vetyears
""".split()
# Variables of this workspace that have no entry in the main body.
ABSENT = {"other", "whatslf2", "wrkgovt1", "wrkgovt2"}

COLUMNS = "1972-82 1982B 1983-87 1987B 1988-91 1993-98 2000-04 2006 2008 2010 2012 2014 2016 2018 ALL".split()
PAGE = re.compile(r"^Page (\d+)$")
VAR = re.compile(r"^\[VAR:\s*([A-Z0-9_]+)\]\s*(\(CONTINUED\))?$")
ROW = re.compile(r"^(.*?)\s*(\S+)((?:\s+\d+){15})$")
SHORT = re.compile(r"^(.*?)\s*(-?\d+)((?:\s+\d+){14})$")  # a row with one cell blank
PUNCH = re.compile(r"-?\d+")
RANGE = re.compile(r"\d+(-\d+|\+)")
NUMBER = re.compile(r"^\d+\.\s")
LETTER = re.compile(r"^(?:\d+\.\s+)?[A-Z]\.\s")
FILTER = re.compile(r"^(IF|ASK)\b")
SIDEBAR = re.compile(r"^(HAND( CARD)?|CARD \S+)$")
HEADER = {"RESPONSE", "PUNCH YEAR", "RESPONSE PUNCH YEAR"}


def space(s):
    return re.sub(r"\s+", " ", s).strip()


def join(lines):
    """Lines as one text; a line ending in a dash runs on into the next."""
    return space("".join(x.strip() + ("" if x.strip().endswith("-") else " ") for x in lines))


def starts_item(s):
    return NUMBER.match(s) or LETTER.match(s) or FILTER.match(s)


def lines_of(texts):
    """Each line with its printed and PDF page; page headers and "HAND CARD" sidebars left out."""
    for pdf_page, text in enumerate(texts, 1):
        rows = text.splitlines()
        page = None
        if rows and PAGE.match(rows[0].strip()):
            page, rows = int(PAGE.match(rows[0].strip())[1]), rows[1:]
        card = False
        for raw in rows:
            s = raw.strip()
            if not s:
                continue
            if SIDEBAR.match(s):
                card = s.startswith("HAND")
                continue
            if card and re.fullmatch(r"[A-Z0-9.]{1,5}", s):  # the card's name, under HAND CARD
                card = False
                continue
            card = False
            yield page, pdf_page, raw.rstrip(), s


def text_of(gap):
    """The wording without its question number or letter, and the stem a numbered question gives its lettered items."""
    numbered = next((i for i, s in enumerate(gap) if NUMBER.match(s)), None)
    lines = [re.sub(r"^\d+\.\s+", "", s) for s in gap]  # the question's number is not its wording
    stem = None
    if numbered is not None:
        rest = lines[numbered:]
        cut = next((j for j, r in enumerate(rest) if LETTER.match(r)), len(rest))
        stem = join(rest[:cut])
    wording = re.sub(r"^[A-Z]\.\s+", "", join(lines))
    return wording, stem


def directions(wording):
    """Maximal runs of words in capitals (at least two words of two or more capitals)."""
    runs, run = [], []
    for w in wording.split(" ") + [""]:
        letters = re.sub(r"[^A-Za-z]", "", w)
        caps = letters and sum(c.isupper() for c in letters) > sum(c.islower() for c in letters)
        if caps or (run and not letters and w):
            run.append(w)
            continue
        while run and not re.sub(r"[^A-Za-z]", "", run[-1]):
            run.pop()
        if sum(len(re.sub(r"[^A-Z]", "", x)) >= 2 for x in run) >= 2:
            runs.append(" ".join(run))
        run = []
    return runs


def parse(texts):
    """Every entry in the codebook, by variable, and the problems met on the way."""
    out, problems = {}, []
    cur, state, gap, buf, stem, last = None, "seek", [], [], None, None

    def flag(entry, message):
        entry.setdefault("problems", []).append(message)

    for page, pdf_page, raw, s in lines_of(texts):
        m = VAR.match(s)
        if m:
            name = m[1].lower()
            if m[2]:  # "(CONTINUED)": the open entry's table goes on
                if cur is None or cur["variable"] != name:
                    problems.append(f"PDF page {pdf_page}: '{s}' while {cur and cur['variable']} is open; its rows are kept with {cur and cur['variable']}")
                state = "head"
                continue
            taken = state != "item" and buf
            if state != "item":
                gap, buf = buf, []
            wording, own_stem = text_of(gap)
            letters = [LETTER.match(x)[0].split()[-1][0] for x in gap if LETTER.match(x)]
            if own_stem is not None:
                stem, last = own_stem, (letters[-1] if letters else None)
                letters = []
            elif letters:
                # A lettered item falls under the stem only if its letter follows the last one.
                if letters[0] != (chr(ord(last) + 1) if last else "A"):
                    stem = None
                last = letters[-1]
            cur = {"variable": name, "page": page, "pdf_page": pdf_page, "wording": wording}
            if own_stem is None and letters and stem:
                cur["stem"] = stem
            cur.update(directions=directions(wording), rows=[], remarks=[], columns=None, counts=[])
            if not wording:
                flag(cur, "no wording of its own")
            if taken:
                flag(cur, "wording taken from lines that follow the previous table")
            if name in out:
                problems.append(f"{name}: a second entry on PDF page {pdf_page}; the first is kept")
            else:
                out[name] = cur
            state, gap, buf = "head", [], []
            continue
        if state in ("head", "table"):
            if s in HEADER:
                continue
            if "1972-82" in s:
                cols = s.replace("RESPONSE", "").split()
                if cur["columns"] is None:
                    cur["columns"] = cols
                elif cols != cur["columns"]:
                    flag(cur, f"PDF page {pdf_page}: other columns {cols}")
                state = "table"
                continue
            r = ROW.match(s)
            if r and state == "table":
                label, punch = space(r[1]), r[2]
                short = SHORT.match(s)
                if not (PUNCH.fullmatch(punch) or RANGE.fullmatch(punch)) and short and space(short[1]):
                    flag(cur, f"a row with 14 counts: its punch code and label are kept, its counts aren't read: {space(short[1])!r}")
                    cur["rows"].append({"code": short[2], "label": space(short[1])})
                elif not (PUNCH.fullmatch(punch) or RANGE.fullmatch(punch)):
                    flag(cur, f"unreadable row (not a label, a punch code and 15 counts): {space(s)!r}")
                    cur["rows"].append(None)
                elif not label:
                    flag(cur, f"a row with one value before its counts ({punch!r}): its label or its punch code is missing")
                    cur["rows"].append(None)
                else:
                    counts = [int(n) for n in r[3].split()]
                    if sum(counts[:-1]) != counts[-1]:  # the ALL column is the sum: a shifted cell shows here
                        flag(cur, f"a row whose counts don't add up to its ALL column: {label!r}")
                    cur["rows"].append({"code": punch, "label": label})
                    cur["counts"].append((label, [int(n) for n in r[3].split()]))
                buf = []
                continue
            if s.startswith("REMARKS:"):
                state = "remarks"
                cur["remarks"].append(s[len("REMARKS:"):].strip())
                continue
            if starts_item(s):
                state, gap, buf = "item", [s], []
                continue
            if raw[:1].isspace() and cur["rows"] and cur["rows"][-1] and not buf:
                old = cur["rows"][-1]["label"]
                cur["rows"][-1]["label"] = join([old, s])
                if cur["counts"] and cur["counts"][-1][0] == old:  # a row with 14 counts has none
                    cur["counts"][-1] = (cur["rows"][-1]["label"], cur["counts"][-1][1])
                continue
            buf.append(s)  # a group heading, or text after the table: kept only if a [VAR:] follows
            continue
        if state == "remarks" and raw[:1].isspace() and not starts_item(s):
            cur["remarks"].append(s)
            continue
        if state in ("remarks", "seek"):
            if starts_item(s):
                state, gap, buf = "item", [s], []
            else:
                buf.append(s)
            continue
        gap.append(s)
    return out, problems


def finish(e):
    """The entry as written: the columns asked, and no counts."""
    if e["columns"] != COLUMNS:
        e.setdefault("problems", []).append(f"columns {e['columns']}")
        e["asked"] = []
    else:
        e["asked"] = [c for i, c in enumerate(COLUMNS[:-1])
                      if any(n[i] > 0 for label, n in e["counts"] if not label.lower().startswith("not applicable"))]
        answers = {c for i, c in enumerate(COLUMNS[:-1])
                   if any(n[i] > 0 for label, n in e["counts"] if not re.match(r"(not applicable|don.t know|no answer)", label, re.I))}
        thin = [c for c in e["asked"] if c not in answers]
        if thin:
            e.setdefault("problems", []).append(f"asked in {', '.join(thin)} only by \"Don't know\" or \"No answer\" counts")
    if not e["rows"]:
        e.setdefault("problems", []).append("no rows")
    e["remarks"] = join(e["remarks"])
    bins = "collapsed for convenience of display" in e["remarks"] or any(r and RANGE.fullmatch(r["code"]) for r in e["rows"])
    e["codes"] = [] if bins else [r for r in e["rows"] if r]
    for k in ("rows", "counts", "columns"):
        e.pop(k)
    order = ["variable", "page", "pdf_page", "stem", "wording", "directions", "codes", "remarks", "asked", "problems"]
    return {k: e[k] for k in order if k in e}


def main(pdf, path):
    texts = [p.extract_text() or "" for p in PdfReader(pdf).pages]
    found, problems = parse(texts)
    missing = [v for v in VARIABLES if v not in found]
    if missing:
        sys.exit(f"Not in the codebook: {', '.join(missing)}")
    assert not ABSENT & set(found), f"now in the codebook: {ABSENT & set(found)}"
    entries = {v: finish(found[v]) for v in VARIABLES}
    notice = json.load(open(os.path.join(os.path.dirname(path), "gss-2022-codebook.json"), encoding="utf-8"))["notice"]
    doc = {
        "source": "General Social Survey 1972-2018 cumulative codebook, main body (NORC, December 2019)",
        "url": "https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS_Codebook_mainbody.pdf",
        "notice": notice,
        "notice_applied": "The cumulative codebook carries no notice of its own. By the owner's decision of 2026-11-12, the 2022 codebook's notice above is applied to it.",
        "columns": COLUMNS[:-1],
        "entries": entries,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(len(entries), "entries")
    for p in problems:
        if any(re.search(rf"\b{v}\b", p) for v in VARIABLES):
            print("problem:", p)
    for v, e in entries.items():
        for p in e.get("problems", []):
            print(f"problem: {v}: {p}")


if __name__ == "__main__":
    main(*sys.argv[1:])
