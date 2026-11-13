"""Write an instrument's GSS column map, and convert one year of the GSS data to CSV for it.

Usage: python3 -I tools/columns.py <gss.sav> <instrument DDI .json> <year> -o <scratch dir>
For example:
  python3 -I tools/columns.py gss7224_r3a.sav dist/instruments/gss_2010.json 2010 -o <scratch dir>

<instrument DDI .json> is the instrument's DDI as `qretools build` writes it from `main`
(or as a release publishes it). The tool writes two files:

- maps/<instrument>-ddi-gss.columns.json, in this workspace: the column map that
  `qretools responses` reads. It holds the GSS variable names, the instrument's Variable
  URNs and the translation of the GSS reserved codes. It says who answered, cites the data
  file and names the columns of the interview's date. Its `metadata` describes the
  columns no respondent is asked: the mode of each interview, the sample's phase, the ballot, the
  form (unless the instrument has it as an input) and every weight that has values in the
  year, with NORC's advice on the weights in `weighting`. It holds no data.
- <scratch dir>/<instrument>-<year>.csv: the year's rows of the GSS data, for the mapped
  columns, the metadata columns, the date columns and the respondent's `id`. It holds data: never commit
  it or publish it.

Each question's GSS variable comes from its `source` ("GSS WRKSTAT; ..."), which the DDI
carries. An input's GSS variable is in INPUTS. The reserved codes are translated by label:
the data's label to the letter of the workspace's missing values with the same label.

The data is not licensed for publication: this tool prints names, never a count or a value.
"""
import csv
import hashlib
import json
import math
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# The instrument's inputs that are GSS variables. Each input's codes are the variable's.
INPUTS = {
    "born_in_us": "born",  # GSS BORN, codebook page 210
    "self_employed": "wrkslf",  # GSS WRKSLF, codebook page 127
}

# Questions filtered from the data: the data holds them in another form than the
# question records, so the map marks them `filtered` and nothing is read from them.
FILTERED = {
    "numemps": "the data groups it (0, 1-9, 10 or more employees), and the question asks for a number",
    "denom": "the data holds broad groups (Baptist, Methodist and so on), and the question records the codebook's detailed codes",
}

# A number's value label that means a range, not the number: a top or a bottom code.
TOP = re.compile(r"\+|\b(or|and) (more|older|over|above)\b", re.IGNORECASE)
BOTTOM = re.compile(r"\b(or|and) (younger|less|fewer|under|below)\b", re.IGNORECASE)
# A number's value label that is the number itself.
EXACT = re.compile(r"^(none|zero|none or zero|\d+)$", re.IGNORECASE)

# The data's code for "iap" (inapplicable): the respondent wasn't asked, so no answer.
# It isn't the letter I ("Not applicable"), which a respondent's answer can't be.
NOT_ASKED = -100

# The data's codes that mean "this variable has no data in this year or this release".
ABSENT = (-70, -80)

SOURCE = re.compile(r"^GSS ([A-Z0-9]+);")

# The map's `source`: the short name of the data, also in the map's file name.
SOURCE_NAME = "gss"

# Columns no respondent is asked, which the map's `metadata` describes. Labels and codes
# come from the data. The mode terms are DDI ModeOfCollection notations, by the data's
# label: NORC says the GSS interviews by telephone, not that it uses CATI. Multimode and
# web have no term yet: before you map a year, add a term for each mode of that year.
SURVEY = {"other": "survey organization"}
DESIGN = {
    "mode": {"role": "mode", "unit": "Interviewer",
             "modes": {"in-person": "Interview.FaceToFace.CAPIorCAMI", "by phone": "Interview.Telephone"}},
    "phase": {"role": "design", "unit": SURVEY},
    "ballot": {"role": "design", "unit": SURVEY},
    "form": {"role": "design", "unit": SURVEY},
}

# Who answered (a term of the DDI vocabulary DataSourceType), and the data file the tool
# reads. Both are facts of the data, so the map gives them.
ANSWERED_BY = "ResearchData.Published"
CITATION = {
    "title": "General Social Survey 1972-2024 Cumulative Data, Release 3a (SPSS)",
    "publisher": "NORC at the University of Chicago",
    "url": "https://gss.norc.org/get-the-data/spss.html",
}

# The date of each interview: DATEINTV holds the month and the day as one number (MMDD),
# and YEAR the year.
INTERVIEW_DATE = {"column": "dateintv", "form": "MMDD", "year": "year"}

# What NORC advises about its weights. The tool writes every weight the data holds for
# the year and never chooses one. Quoted from the GSS 2024 Codebook, Release 3a, page 40,
# under its permission notice (LICENSE.md); the PDF's extra spaces are dropped.
WEIGHTING = {
    "advice": (
        "WTSSPS and WTSSNRPS are the recommended weights of the GSS 1972-2024 Cumulative data file. "
        "WTSSPS is the recommended weight for analysis conducted from 1972-2024 and is now the default "
        "weight for the GSS Data Explorer. Both WTSSPS and WTSSNRPS are available for data users for "
        "2004-2024. For years where WTSSNRPS is available, NORC recommends data users use WTSSNRPS."
    ),
    "source": {
        "title": "GSS 2024 Codebook, Release 3a, page 40",
        "publisher": "NORC at the University of Chicago",
        "url": "https://gss.norc.org/content/dam/gss/get-documentation/pdf/codebook/GSS%202024%20Codebook%20R3a.pdf",
    },
    "read": "2026-11-12",
}


def is_weight(column, label, labels):
    """NORC's weights: named WT..., labelled as a weight, and a number (no labelled code).

    OVERSAMP, a coded adjustment that the codebook says WTSSPS and WTSSNRPS include, isn't one.
    """
    return column.startswith("wt") and "weight" in label.casefold() and not any(c >= 0 for c in labels)


def text(labels):
    """The English text of a DDI Label or Content list."""
    return labels[0]["Content"][0]["MultilingualStringValue"]["Value"]


def name(variable):
    return variable["VariableName"][0]["String"][0]["MultilingualStringValue"]["Value"]


def key(ref):
    """A DDI reference's key in its type's object: agency:id:version."""
    return ":".join(ref["value"])


def missing_letters(ddi):
    """The workspace's missing values, label (casefolded) to letter, from the DDI."""
    letters = {}
    for code_list in ddi["CodeList"].values():
        if code_list["ID"] != "missing-values.codes":
            continue
        for code in code_list["Code"]:
            label = text(ddi["Category"][key(code["CategoryReference"])]["Label"])
            letters[label.casefold()] = code["Value"]["StringValue"]
    if not letters:
        sys.exit("The DDI has no missing values (missing-values.codes).")
    return letters


def codes_of(ddi, variable):
    """A variable's codes, as strings, or None for a number or text."""
    domain = variable["VariableRepresentation"]["ValueRepresentation"]
    if domain["$type"] != "CodeDomain":
        return None
    return [c["Value"]["StringValue"] for c in ddi["CodeList"][key(domain["CodeListReference"])]["Code"]]


def plan(ddi):
    """Each Variable's GSS column, or why it has none: (columns, without).

    columns: [(variable, its GSS column, why it's filtered or None)] in the DDI's order.
    without: [(name, reason)].
    """
    computed = {item["AssignedVariableReference"]["URN"] for item in ddi.get("ComputationItem", {}).values()}
    columns, without = [], []
    for variable in ddi["Variable"].values():
        n = name(variable)
        if "QuestionReference" in variable:
            question = ddi["QuestionItem"][key(variable["QuestionReference"][0])]
            rationale = question["BasedOnObject"]["BasedOnRationaleDescription"]["String"][0]
            match = SOURCE.match(rationale["MultilingualStringValue"]["Value"])
            if match is None:
                sys.exit(f"{n}: its source doesn't start with the GSS variable (`GSS NAME;`).")
            columns.append((variable, match.group(1).lower(), FILTERED.get(n)))
        elif n in INPUTS:
            columns.append((variable, INPUTS[n], None))
        elif variable.get("OutParameter", {}).get("URN") in computed:
            without.append((n, "computed by the instrument, not data"))
        else:
            without.append((n, "an input that no GSS variable holds"))
    return columns, without


def reserved_values(letters, labels_by_column):
    """The map's `values`: each reserved code to its letter, by label, and "iap" to null.

    labels_by_column: {column: {code: label}} from the data. Every column must give a
    reserved code the same label, or a translation would be a guess.
    """
    reserved = {}
    for column, labels in labels_by_column.items():
        for code, label in labels.items():
            if code >= 0:
                continue
            if reserved.setdefault(code, label) != label:
                sys.exit(f"{column}: the data labels {code:g} differently in other columns.")
    if NOT_ASKED not in reserved:
        sys.exit(f"The data has no label for {NOT_ASKED} (iap).")
    values = {}
    for code in sorted(reserved, reverse=True):
        if code == NOT_ASKED:
            values[cell(code)] = None
        elif reserved[code].casefold() in letters:
            values[cell(code)] = letters[reserved[code].casefold()]
    return values


def cell(value):
    """A value as the CSV writes it: a whole number without `.0`, nothing for no value."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def censored(column, labels):
    """A number column's top and bottom codes, from the data's labels: {value: label}.

    A label that is neither a range nor the number itself is printed, never guessed.
    """
    ranges = {}
    for code in sorted(c for c in labels if c >= 0):
        label = labels[code]
        if TOP.search(label) or BOTTOM.search(label):
            ranges[cell(code)] = label
        elif not EXACT.match(label.strip()):
            print(f"note: {column}: the data labels {cell(code)} \"{label}\", which isn't read as a range or as the number", file=sys.stderr)
    return ranges


def metadata(present, labels_by_column, mapped, kept):
    """The map's `metadata`: each column in `present` ({column: its label} in the data's
    order, the columns with values in the year) that DESIGN names or that is a weight,
    unless the instrument maps it already (as an input).

    kept: the reserved codes (as cells) that the workspace holds as missing values. A
    coded column keeps them as codes with the data's labels, since the map's shared
    `values` don't apply to these columns.
    """
    entries = []
    for column, label in present.items():
        spec = DESIGN.get(column)
        labels = labels_by_column[column]
        weight = is_weight(column, label, labels)
        if column in mapped or (spec is None and not weight):
            continue
        entry = {"column": column, "label": label}
        if weight:
            entry.update(role="weight", unit=SURVEY, number=True, weight=True)
        else:
            entry.update(role=spec["role"], unit=spec["unit"])
            entry["codes"] = {cell(c): labels[c] for c in sorted(labels) if c >= 0}
            entry["codes"].update({cell(c): labels[c] for c in sorted(labels, reverse=True) if c < 0 and cell(c) in kept})
            if "modes" in spec:
                by_label = {v: k for k, v in entry["codes"].items()}
                missing = [m for m in spec["modes"] if m not in by_label]
                if missing:
                    sys.exit(f"{column}: the data labels no code {', '.join(missing)}.")
                entry["modes"] = {by_label[m]: term for m, term in spec["modes"].items()}
        # A weight's reserved codes are no value, or they'd be read as weights. In a coded
        # column only "iap" and the codes for no data are; another one, as in `columns`,
        # isn't translated, so it shows as a finding where it occurs.
        nothing = [c for c in labels if c < 0] if weight else [c for c in labels if c == NOT_ASKED or c in ABSENT]
        entry["values"] = {cell(c): None for c in sorted(nothing, reverse=True)}
        entries.append(entry)
    return entries


def column_map(ddi, digest, labels_by_column, present):
    """The column map, and the variables it leaves out with why.

    present: {column: label} of the data's columns with values in the year, for `metadata`.
    """
    columns, without = plan(ddi)
    letters = missing_letters(ddi)
    entries = []
    for variable, column, filtered in columns:
        entry = {"column": column, "variable": variable["URN"]}
        entries.append(entry)
        labels = labels_by_column.get(column)
        if labels is None:
            sys.exit(f"{name(variable)}: the data has no column `{column}`.")
        if filtered is not None:
            entry["filtered"] = True
            print(f"filtered: {name(variable)}: {filtered}", file=sys.stderr)
            continue
        codes = codes_of(ddi, variable)
        if codes is None:
            ranges = censored(column, labels)
            if ranges:
                entry["censored"] = ranges
        else:
            # Codes the data labels that the workspace doesn't hold: printed, not fatal, so
            # each shows as a finding where it occurs. Codes only: the data's labels are its
            # own, not the codebook's, so comparing them would mostly be noise.
            other = [cell(c) for c in sorted(labels) if c >= 0 and cell(c) not in codes]
            if other:
                print(f"note: {column}: the data labels {len(other)} codes that `{name(variable)}` doesn't hold: {', '.join(other)}", file=sys.stderr)
    values = reserved_values(letters, {c: labels_by_column[c] for _, c, f in columns if f is None})
    the_map = {
        "source": SOURCE_NAME,
        "ddi": digest,
        "answered_by": ANSWERED_BY,
        "citation": CITATION,
        "respondent": "id",
        "values": values,
        "columns": entries,
    }
    kept = {code for code, letter in values.items() if letter is not None}
    extra = metadata(present, labels_by_column, {c for _, c, _ in columns} | {"id"}, kept)
    if extra:
        the_map["metadata"] = extra
    if any(m.get("weight") for m in extra):
        the_map["weighting"] = WEIGHTING
    the_map["interview_date"] = INTERVIEW_DATE
    return the_map, without


def main(argv):
    if len(argv) != 6 or argv[4] != "-o":
        sys.exit(__doc__)
    sav, ddi_path, year, _, out = argv[1:]
    import pyreadstat  # only here: the map's logic above needs no data

    with open(ddi_path, "rb") as f:
        raw = f.read()
    ddi = json.loads(raw)
    instrument = next(iter(ddi["Instrument"].values()))["ID"].removeprefix("instrument-")
    _, meta = pyreadstat.read_sav(sav, metadataonly=True, user_missing=True)
    labels_by_column = {n.lower(): meta.variable_value_labels.get(n, {}) for n in meta.column_names}
    if not {"id", "year", INTERVIEW_DATE["column"]} <= labels_by_column.keys():
        sys.exit(f"The data has no `id`, `year` or `{INTERVIEW_DATE['column']}` column.")
    by_lower = {n.lower(): n for n in meta.column_names}
    column_labels = {n.lower(): label or "" for n, label in zip(meta.column_names, meta.column_labels)}

    def rows_of(names):
        data, _ = pyreadstat.read_sav(sav, usecols=[by_lower[n] for n in dict.fromkeys(["year", *names])], user_missing=True)
        data.columns = [c.lower() for c in data.columns]
        rows = data[data["year"] == int(year)]
        if rows.empty:
            sys.exit(f"The data has no rows for {year}.")
        return rows

    candidates = [n for n in column_labels if n in DESIGN or is_weight(n, column_labels[n], labels_by_column[n])]
    held = rows_of(candidates)
    present = {n: column_labels[n] for n in candidates if not held[n].isin(ABSENT).all()}
    for n in DESIGN:
        if n not in present:
            print(f"note: {n}: the data has no values for it in {year}, so the map leaves it out", file=sys.stderr)
    the_map, without = column_map(ddi, "sha256:" + hashlib.sha256(raw).hexdigest(), labels_by_column, present)
    for n, reason in without:
        print(f"not mapped: {n}: {reason}", file=sys.stderr)

    # A filtered column's data isn't read, so it isn't written either.
    names = ["id"] + [c["column"] for c in the_map["columns"] if not c.get("filtered")]
    names += [m["column"] for m in the_map.get("metadata", [])]
    names += [INTERVIEW_DATE["column"], INTERVIEW_DATE["year"]]
    rows = rows_of(names)
    if not rows["id"].is_unique:
        sys.exit(f"`id` isn't unique in {year}.")
    for c in [c["column"] for c in the_map["columns"] if not c.get("filtered")] + [INTERVIEW_DATE["column"]]:
        if rows[c].isin(ABSENT).all():
            sys.exit(f"{c}: the data has no values for it in {year}; does the instrument ask it then?")

    map_path = os.path.join(ROOT, "maps", f"{instrument}-ddi-{SOURCE_NAME}.columns.json")
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(the_map, indent=2, ensure_ascii=False) + "\n")
    os.makedirs(out, exist_ok=True)
    csv_path = os.path.join(out, f"{instrument}-{year}.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(names)
        for row in rows[names].itertuples(index=False):
            writer.writerow([cell(v) for v in row])
    print(f"wrote {os.path.relpath(map_path, ROOT)} and {csv_path}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
