"""Write an instrument's GSS column map, and convert one year of the GSS data to CSV for it.

Usage: python3 -I tools/columns.py <gss.sav> <instrument DDI .json> <year> -o <scratch dir>
For example:
  python3 -I tools/columns.py gss7224_r3a.sav v9/instruments/gss_2010.json 2010 -o <scratch dir>

<instrument DDI .json> is the instrument's DDI as a release publishes it (or as
`qretools build` writes it at that release's tag). The tool writes two files:

- instruments/<instrument>-ddi-gss.columns.json, in this workspace: the column map that
  `qretools responses` reads. It holds the GSS variable names, the instrument's Variable
  URNs and the translation of the GSS reserved codes. It holds no data.
- <scratch dir>/<instrument>-<year>.csv: the year's rows of the GSS data, for the mapped
  columns and the respondent's `id`. It holds data: never commit it or publish it.

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


def column_map(ddi, digest, labels_by_column):
    """The column map, and the variables it leaves out with why."""
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
    return {
        "ddi": digest,
        "respondent": "id",
        "values": values,
        "columns": entries,
    }, without


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
    if "id" not in labels_by_column or "year" not in labels_by_column:
        sys.exit("The data has no `id` or `year` column.")
    the_map, without = column_map(ddi, "sha256:" + hashlib.sha256(raw).hexdigest(), labels_by_column)
    for n, reason in without:
        print(f"not mapped: {n}: {reason}", file=sys.stderr)

    by_lower = {n.lower(): n for n in meta.column_names}
    # A filtered column's data isn't read, so it isn't written either.
    names = ["id"] + [c["column"] for c in the_map["columns"] if not c.get("filtered")]
    data, _ = pyreadstat.read_sav(sav, usecols=[by_lower["year"]] + [by_lower[n] for n in names], user_missing=True)
    data.columns = [c.lower() for c in data.columns]
    rows = data[data["year"] == int(year)]
    if rows.empty:
        sys.exit(f"The data has no rows for {year}.")
    if not rows["id"].is_unique:
        sys.exit(f"`id` isn't unique in {year}.")
    for c in names[1:]:
        if rows[c].isin(ABSENT).all():
            sys.exit(f"{c}: the data has no values for it in {year}; does the instrument ask it then?")

    map_path = os.path.join(ROOT, "instruments", f"{instrument}-ddi-gss.columns.json")
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
