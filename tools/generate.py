"""Write this GSS example workspace, as it was for one GSS year, from a NORC codebook.

Usage: python -I tools/generate.py <source.json> <year> [workspace_dir]
For example: python -I tools/generate.py sources/gss-1972-2018-codebook.json 2008
<source.json> is sources/gss-1972-2018-codebook.json (tools/extract_cumulative.py makes
it) or sources/gss-2022-codebook.json (tools/extract.py makes it). The workspace gets
the questions of SPEC that the source says were asked in any replay year up to <year>
(REPLAY), and only the scales, universes, concepts and units those questions name. missing.yaml always comes from the
2022 codebook: its letters are this workspace's reserved codes, whatever the source.

NORC's material here comes only from those codebooks, under the 2022 codebook's
permission notice (see LICENSE.md): question text, filters, interviewer directions,
codes and their labels, and the reserved (missing-value) codes. Each text of NORC's in
SPEC is a span of its variable's codebook wording, word for word apart from case and
spacing, where a {{fill}} stands for the codebook's placeholder: the asserts below check
it for the questions written. Titles, intents, concept labels and the universes in OURS
are our own words.
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SOURCE_PATH, YEAR = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else ROOT
SOURCE = json.load(open(SOURCE_PATH, encoding="utf-8"))
CUMULATIVE = "notice_applied" in SOURCE
ENTRIES = SOURCE["entries"]
RESERVED = json.load(open(os.path.join(ROOT, "sources", "gss-2022-codebook.json"), encoding="utf-8"))["entries"]
CITE = "GSS 1972-2018 cumulative codebook (NORC)" if CUMULATIVE else "GSS 2022 codebook (NORC)"

# Shared concepts: our own labels for the parts of the GSS Replicating Core used here.
CONCEPTS = {
    "race": "Race",
    "ethnicity": "Ancestry",
    "hispanic_origin": "Hispanic or Latino origin",
    "siblings": "Number of siblings",
    "marital_status": "Marital and partnership status",
    "number_of_children": "Number of children",
    "age_at_first_birth": "Age when the first child was born",
    "education": "Field of study",
    "religious_affiliation": "Religion",
    "household_income": "Family income",
    "citizenship_status": "Citizenship and time in the United States",
    "language": "Languages spoken",
    "employment_status": "Work status",
    "industry": "Kind of workplace",
    "sector": "Government or private employer",
    "number_of_employees": "Employees of the self-employed",
    "labor_supply": "Time worked",
    "income_from_occupation": "Earnings from work",
    "size_of_workplace": "Size of the workplace",
    "workplace_hierarchy": "Supervision at work",
    "veteran_status": "Military service",
}

# Shared scales, each named for the variable whose question it was first written for.
# A scale holds every code the codebook gives any question that uses it.
SCALES = {"yes_no": "widowed", "yes_no_3_4": "wksubs1", "race_census": "racecen1",
          "ancestry": "eth2", "college_major": "major1", "language_list": "othlang1",
          "income_25": "income06", "income_26": "income16"}
# shortcut: at code 25 INCOME16 prints "$150,000 or over" and RINCOM16 "$150,000 to $169,999", so income_26 stops the 2016 run; that pull request decides.

# name: (folder, concept, title, fields). The title is ours. Fields: text (the question, a
# span of the codebook's label), universe, instruction (a span of the label), fills,
# number (its unit), scale, variant_of (ours), and gss (the GSS variable, where its name
# differs).
D, W = "demographics", "work"
SPEC = {
    "racecen1": (D, "race", "Race, first mentioned", dict(text="What is your race? Indicate one or more races that you consider yourself to be.", scale="race_census")),
    "racecen2": (D, "race", "Race, second mentioned", dict(text="What is your race? Indicate one or more races that you consider yourself to be.", scale="race_census", variant_of={"racecen1": "the second race mentioned in answer to the same question"})),
    "racecen3": (D, "race", "Race, third mentioned", dict(text="What is your race? Indicate one or more races that you consider yourself to be.", scale="race_census", variant_of={"racecen1": "the third race mentioned in answer to the same question", "racecen2": "the third race mentioned, where racecen2 is the second"})),
    "eth1": (D, "ethnicity", "Ancestry, first country", dict(text="From what countries or part of the world did your ancestors come?")),  # its own list: 98 is an answer here, "Don't know" in ETH2 and ETH3
    "eth2": (D, "ethnicity", "Ancestry, second country", dict(text="From what countries or part of the world did your ancestors come?", scale="ancestry", variant_of={"eth1": "the second country mentioned in answer to the same question"})),
    "eth3": (D, "ethnicity", "Ancestry, third country", dict(text="From what countries or part of the world did your ancestors come?", scale="ancestry", variant_of={"eth1": "the third country mentioned in answer to the same question", "eth2": "the third country mentioned, where eth2 is the second"})),
    "hispanic": (D, "hispanic_origin", "Hispanic or Latino origin", dict(text=("Are you Spanish, Hispanic, or Latino/Latina?", "Which group are you from?"))),
    "sibs": (D, "siblings", "Number of siblings", dict(text="How many brothers and sisters did you have? Please count those born alive, but no longer living, as well as those alive now. Also include stepbrothers and stepsisters, and children adopted by your parents.", number=None)),
    "marital": (D, "marital_status", "Marital status", dict(text="Are you currently--married, widowed, divorced, separated, or have you never been married?")),
    "widowed": (D, "marital_status", "Ever widowed", dict(text="Have you ever been widowed?", universe="currently_married_separated_divorced", scale="yes_no")),
    "divorced": (D, "marital_status", "Ever divorced or separated", dict(gss="divorce", text="Have you ever been divorced or legally separated?", universe="currently_married_widowed", scale="yes_no")),
    "posslq": (D, "marital_status", "Living arrangement with a partner", dict(text="Which of these statements applies to you?")),
    "posslqy": (D, "marital_status", "Living arrangement with a partner, Y wording", dict(text="Which of these statements applies to you?", variant_of={"posslq": "the Y form of the X/Y wording experiment: option 2 reads 'steady partner' for 'living as married'"})),
    "childs": (D, "number_of_children", "Number of children", dict(text="How many children have you ever had? Please count all that were born alive at any time (including any you had from a previous marriage).", number=None)),
    "agekdbrn": (D, "age_at_first_birth", "Age when the first child was born", dict(text="How old were you when your first child was born?", number="years")),
    "major1": (D, "education", "Field of study, first", dict(text="What was your major or field of study when you received your {{degree}} degree?", instruction="IF THE RESPONDENT RECEIVED MORE THAN ONE GRADUATE LEVEL DEGREE, ASK ABOUT THE HIGHEST DEGREE OBTAINED (E.G. ABOUT A Ph.D. RATHER THAN AN M.B.A).", fills={"degree": "text"}, scale="college_major")),
    "major2": (D, "education", "Field of study, second", dict(text="What was your major or field of study when you received your {{degree}} degree?", instruction="IF THE RESPONDENT RECEIVED MORE THAN ONE GRADUATE LEVEL DEGREE, ASK ABOUT THE HIGHEST DEGREE OBTAINED (E.G. ABOUT A Ph.D. RATHER THAN AN M.B.A).", fills={"degree": "text"}, scale="college_major", variant_of={"major1": "the second field of study mentioned in answer to the same question"})),
    "relig": (D, "religious_affiliation", "Religion", dict(text="What is your religious preference? Is it Protestant, Catholic, Jewish, some other religion, or no religion?")),
    "denom": (D, "religious_affiliation", "Protestant denomination", dict(text="What specific denomination is that, if any?", instruction="PROBE FOR EXACT DENOMINATION")),
    "other": (D, "religious_affiliation", "Other Protestant denomination", dict(text="What specific denomination is that, if any?", variant_of={"denom": "the GSS's detailed list of other Protestant denominations, coded from the same question"})),
    "jew": (D, "religious_affiliation", "Jewish denomination", dict(text="Do you consider yourself Orthodox, Conservative, Reform or none of these?")),
    "reliten": (D, "religious_affiliation", "Strength of religion", dict(text="Would you call yourself a strong {{religion}} or a not very strong {{religion}}?", fills={"religion": "text"})),
    "income06": (D, "household_income", "Family income, 25 groups", dict(text="In which of these groups did your total family income, from all sources, fall last year before taxes, that is.", scale="income_25")),
    "income16": (D, "household_income", "Family income, 26 groups", dict(text="In which of these groups did your total family income, from all sources, fall last year? That is, before taxes.", scale="income_26", variant_of={"income06": "the 26-group version, from 2016"})),
    "uscitzn": (D, "citizenship_status", "U.S. citizenship", dict(text="Now we would like to ask you about U.S. citizenship. Are you…", universe="born_outside_us")),
    "fucitzn": (D, "citizenship_status", "Citizenship, follow-up", dict(text="Are you…")),
    "mnthsusa": (D, "citizenship_status", "Months lived in the United States", dict(text="How long have you lived in the United States? If less than a year, please specify the time in months. If you have lived in the United States for more than one period during your life, what is the total number of years you have lived in the United States?", universe="born_outside_us", number="months", variant_of={"yrsusa": "the months part of the answer, when it is less than a year"})),
    "yrsusa": (D, "citizenship_status", "Years lived in the United States", dict(gss="yearsusa", text="How long have you lived in the United States? If less than a year, please specify the time in months. If you have lived in the United States for more than one period during your life, what is the total number of years you have lived in the United States?", universe="born_outside_us", number="years")),
    "othlang": (D, "language", "Speaks another language", dict(text="Can you speak a language other than English [Spanish]?", scale="yes_no")),
    "othlang1": (D, "language", "Other language, first", dict(text="What other language(s) do you speak?", universe="other_language_speakers", scale="language_list")),
    "othlang2": (D, "language", "Other language, second", dict(text="What other language(s) do you speak?", universe="other_language_speakers", variant_of={"othlang1": "the second language mentioned in answer to the same question"})),
    "betrlang": (D, "language", "Language spoken more fluently", dict(text="Which language do you speak more fluently?", universe="other_language_speakers")),
    "spklang": (D, "language", "How well the other language is spoken", dict(text="How well do you speak that language?", universe="other_language_speakers", instruction="IF SPEAKS 2 OR MORE, ASK ONLY OF THE MOST FLUENT LANGUAGE")),
    "wrkstat": (W, "employment_status", "Work status last week", dict(text="Last week were you working full time, part time, going to school, keeping house, or what?")),
    "evwork": (W, "employment_status", "Ever worked for a year", dict(text="Did you ever work for as long as one year?", universe="not_in_labor_force", scale="yes_no")),
    "wrkselffam": (W, "employment_status", "Works in a family business or farm", dict(gss="wrkslffam", text="{{do}} you work in your own family business or farm?", fills={"do": "text"}, scale="yes_no")),
    "whatslf2": (W, "industry", "Kind of workplace", dict(text="How would you classify the place where you {{work}}? Was this mainly...?", fills={"work": "text"})),
    "wrkgovt": (W, "sector", "Government or private employer", dict(text="{{are}} you employed by the federal, state or local government or by a private employer (including non-profit organizations)?", fills={"are": "text"})),
    "wrkgovt1": (W, "sector", "Employed by the government", dict(text="{{are}} you employed by the government? (Please consider federal, state, or local government.)", fills={"are": "text"}, scale="yes_no")),
    "wrkgovt2": (W, "sector", "Employed by a private employer", dict(text="{{are}} you employed by a private employer (including non-profit organizations)?", fills={"are": "text"}, scale="yes_no")),
    "numemps": (W, "number_of_employees", "Number of employees", dict(text="How many employees {{do}} you have?", fills={"do": "text"}, universe="self_employed", number=None)),
    "hrs1": (W, "labor_supply", "Hours worked last week", dict(text="How many hours did you work last week, at all jobs?", universe="working", number="hours")),
    "hrs2": (W, "labor_supply", "Usual hours of work", dict(text="How many hours a week do you usually work, at all jobs?", universe="with_job_not_at_work", number="hours")),
    "weekswrk": (W, "labor_supply", "Weeks worked last year", dict(text="Now I'd like to ask you about last year. In {{last_year}} how many weeks did you work either full-time or part-time not counting work around the house--include paid vacations and sick leave?", fills={"last_year": "number"}, number="weeks")),
    "partfull": (W, "labor_supply", "Full or part time last year", dict(text="When you worked in {{last_year}}, was it usually full or part time?", fills={"last_year": "number"})),
    "rincom06": (W, "income_from_occupation", "Earnings from work, 25 groups", dict(text="In which of these groups did your earnings from {{job}}, from all sources for {{last_year}} fall? That is, before taxes or other deductions.", fills={"job": "text", "last_year": "text"}, scale="income_25")),
    "rincom16": (W, "income_from_occupation", "Earnings from work, 26 groups", dict(text="In which of these groups did your earnings from {{job}}, from all sources for {{last_year}} fall? That is, before taxes or other deductions.", fills={"job": "text", "last_year": "text"}, scale="income_26", variant_of={"rincom06": "the 26-group version, from 2016"})),
    "localnum": (W, "size_of_workplace", "People at the workplace", dict(text="About how many people work at the location where you work? (Count part-time as well as full-time employees in all areas, departments and buildings.)")),
    "wksub1": (W, "workplace_hierarchy", "Has a supervisor", dict(text="{{do_you}} have a supervisor on {{your}} job to whom {{you_are}} directly responsible?", fills={"do_you": "text", "your": "text", "you_are": "text"}, scale="yes_no")),
    "wksubs1": (W, "workplace_hierarchy", "The supervisor has a supervisor", dict(text="Does that person have a supervisor on the job to whom he is directly responsible?", universe="has_supervisor", scale="yes_no_3_4")),
    "wksup1": (W, "workplace_hierarchy", "Supervises others", dict(text="In {{your}} job, {{do_you}} supervise anyone who is directly responsible to {{you}}?", fills={"your": "text", "do_you": "text", "you": "text"}, scale="yes_no")),
    "wksups1": (W, "workplace_hierarchy", "Those supervised supervise others", dict(text="Do any of those persons supervise anyone else?", universe="supervises_someone", scale="yes_no_3_4")),
    "vetyears": (W, "veteran_status", "Time on active military duty", dict(text=("Have you ever been on active duty for military training or service for two consecutive months or more?", "What was your total time on active duty?"))),
}

# Variables in an extract that are left out of the workspace, and why (README.md, "Left out").
LEFT_OUT = {"race": "from 2002 RACECEN1-3 replaced it and it was imputed (its remarks)",
            "income": "recoded from INCOME06 from 2006 (the GSS data; its remarks say it was recoded up to 2006)",
            "rincome": "recoded from RINCOM06 from 2006 (the GSS data)"}

# The replay's years in the cumulative codebook, oldest first. Year Y holds every question
# asked in any of them up to Y: a bank keeps a question that a later year doesn't ask.
REPLAY = ["2008", "2010", "2012", "2014", "2016", "2018"]

# Universes: the codebook's filters, word for word, or our own description (OURS) of who
# is asked, where we infer it from the order of the questions.
UNIVERSES = {
    "currently_married_separated_divorced": "IF CURRENTLY MARRIED, SEPARATED, OR DIVORCED",
    "currently_married_widowed": "IF CURRENTLY MARRIED OR WIDOWED",
    "not_in_labor_force": "IF RETIRED, IN SCHOOL, KEEPING HOUSE, OR OTHER",
    "working": "IF WORKING, FULL OR PART TIME",
    "with_job_not_at_work": "IF WITH A JOB, BUT NOT AT WORK",
    "born_outside_us": "Respondents who were not born in the United States",
    "other_language_speakers": "Respondents who speak a language other than English",
    "self_employed": "Respondents who are or were self-employed",
    "has_supervisor": "Respondents who have a supervisor at work",
    "supervises_someone": "Respondents who supervise someone at work",
}
OURS = {"born_outside_us", "other_language_speakers", "self_employed", "has_supervisor", "supervises_someone"}

# The 2022 codebook writes labels in capitals. These lists are mostly names, so each word gets
# a capital, except small words such as "and" (SMALL); the others are in sentence case.
NAME_LISTS = {"eth1", "othlang1", "othlang2", "relig", "other", "denom", "jew", "racecen1"}
PROPER = ["hispanic", "latino", "spanish", "mexican", "american", "puerto rican", "cuban", "english", "french", "chinese", "italian", "german", "african", "alaska", "native", "pacific", "asian", "christian", "protestant", "catholic", "jewish"]
SMALL = {"and", "or", "of", "the", "in", "a", "to", "&", "for", "general"}


def norm(s):
    return re.sub(r"\s+", " ", s.replace("…", "...").lower()).strip()


def is_span(text, entry):
    """Whether text is in the codebook's label, word for word, a {{fill}} standing for a placeholder.
    A tuple is several spans, in the label's order, with what lies between them (routing) cut."""
    def one(span):
        pattern = re.escape(norm(span)).replace(r"\ ", r"\s*")
        return re.sub(r"\\\{\\\{\w+\\\}\\\}", r"[^?]{1,60}?", pattern)
    spans = text if isinstance(text, tuple) else (text,)
    return re.search(".*?".join(map(one, spans)), norm(entry["label"])) is not None


def joined(text):
    return " ".join(text) if isinstance(text, tuple) else text


def tidy(label, names):
    """A label as the respondent reads it: routing and "[See REMARKS]" cut, and capitals made ordinary where the codebook writes them all."""
    label = re.sub(r"\s*\([^()]*\b(ASK|GO TO|SKIP)\b[^()]*\)", "", label, flags=re.I)
    label = re.sub(r"\s*\[See REMARKS[^\]]*\]", "", label)  # a cross-reference NORC added, not the label
    if not label.isupper():
        return label
    label = label.lower()
    label = re.sub(r"\bu\.s\.", "U.S.", re.sub(r"\bi\b", "I", label))
    label = re.sub(r"\b(" + "|".join(PROPER) + r")\b", lambda m: m[1].title(), label)
    if names:
        label = " ".join(w if w in SMALL else w[:1].upper() + w[1:] for w in label.split(" "))
    return label[:1].upper() + label[1:]


def scalar(s):
    plain = re.fullmatch(r"[A-Za-z(][^\n#]*", s) and ": " not in s and not s.endswith(":") \
        and s.lower() not in {"yes", "no", "true", "false", "on", "off", "null"} and not s.startswith(("[", "{", "*", "&", "!", "%", "@", "`"))
    return s if plain else json.dumps(s, ensure_ascii=False)


def label_of(entry):
    """The codebook's wording: the 2022 label, or the cumulative stem and wording."""
    return entry["label"] if "label" in entry else " ".join(x for x in (entry.get("stem"), entry["wording"]) if x)


# The labels the cumulative codebook gives its missing-value rows: these are never
# responses. Each source's codes are translated to missing.yaml's letters by a later
# GSS column map, not here.
MISSING = re.compile(r"(not applicable\b.*|don't know|no answer|refused|don't know, no answer|no answer, don't know"
                     r"|don't know/uncoded|not possible to code; see ethnic)")
# "No ethnicity mentioned" (ETH1's 98) is not here: the respondent answered and named no country.
# A response label with one of these words is a missing-value row this list doesn't name yet.
SUSPECT = re.compile(r"\b(know|answer|applicable|refused|uncoded|code|iap)\b")


def codes(var):
    out = []
    for c in ENTRIES[var]["codes"]:
        plain = space(c["label"]).replace("’", "'").lower()
        if MISSING.fullmatch(plain):
            continue
        assert not SUSPECT.search(plain) or plain.endswith(("don't know which", "don't know how long")), f"{var}: is '{c['label']}' a missing-value row?"
        out.append((c["code"], space(c["label"])))
    return out


def space(s):
    return re.sub(r"\s+", " ", s).strip()


def code_map(pairs, names, indent="  "):
    return "".join(f'{indent}"{c}": {scalar(tidy(l, names))}\n' for c, l in pairs)


def write(path, body):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(body)


def gss(name):
    return SPEC[name][3].get("gss", name)


def first_asked(name):
    """The first replay year, up to YEAR, that asked the question; None if none did. The 2022 codebook has no years: its questions are asked in 2022."""
    entry = ENTRIES.get(gss(name))
    if entry is None or not CUMULATIVE:
        # shortcut: the 2022 source alone, so it drops a question only the cumulative codebook asked; the 2022 pull request reads both sources.
        return entry and YEAR
    return next((y for y in REPLAY[:REPLAY.index(YEAR) + 1] if y in entry["asked"]), None)


assert not CUMULATIVE or YEAR in REPLAY, f"{YEAR} isn't a year of the replay"
QUESTIONS = {n: v for n, v in SPEC.items() if first_asked(n)}
# Entries the extractor couldn't read in full, kept only for the reason given.
KNOWN_PROBLEMS = {"eth3": "three rows (28, 36, 37) lack a count in one column; their codes and labels are read, and ETH2 gives the same ones to the ancestry scale",
                  "rincom06": "its 2016 column holds only Don't know and No answer counts; that doesn't change the first year that asked it",
                  "vetyears": "one row (4) lacks a count in one column; its code and label are read, and its other rows give the years asked"}
for n in QUESTIONS:
    assert not ENTRIES[gss(n)].get("problems") or gss(n) in KNOWN_PROBLEMS, f"{n}: {ENTRIES[gss(n)]['problems']}"
assert CUMULATIVE or YEAR == "2022", "the 2022 codebook gives the questions of 2022"
assert set(ENTRIES) <= {gss(n) for n in SPEC} | set(LEFT_OUT), "the extract has a variable SPEC lacks"
assert not CUMULATIVE or YEAR in SOURCE["columns"], f"{YEAR} isn't a column of the source"

# Each text of NORC's is the codebook's, word for word. Only the questions written are
# checked: an item's text is set to its source in the year it is first asked.
for name, (_, _, _, f) in QUESTIONS.items():
    entry = ENTRIES[gss(name)]
    label = label_of(entry)
    for key in ("text", "instruction"):
        assert key not in f or is_span(f[key], {"label": label}), f"{name}.{key} isn't in the codebook's wording: {label}"
    if "universe" in f and f["universe"] not in OURS:
        assert norm(UNIVERSES[f["universe"]]) in norm(label), f"{name}'s universe isn't its codebook filter"
assert all(f.get("universe", next(iter(UNIVERSES))) in UNIVERSES for _, _, _, f in SPEC.values())
assert all(f.get("scale", "yes_no") in SCALES for _, _, _, f in SPEC.values())
assert all(k in QUESTIONS for _, _, _, f in QUESTIONS.values() for k in f.get("variant_of", {})), "a variant_of names a question not asked this year"

# A scale holds every code the questions written on it give, and a code means the same on each.
scales = {}
for scale in SCALES:
    for var in [gss(n) for n, (_, _, _, f) in QUESTIONS.items() if f.get("scale") == scale]:
        seen = scales.setdefault(scale, {})
        for c, l in codes(var):
            assert tidy(seen.setdefault(c, l), False) == tidy(l, False), f"scale {scale}: code {c} is '{seen[c]}' and '{l}'"

# The generated folders are written afresh, so nothing dropped or renamed stays.
for folder in ("questions", "scales", "universes", "concepts", "units"):
    shutil.rmtree(os.path.join(OUT, folder), ignore_errors=True)

used = lambda key: {f[key] for _, _, _, f in QUESTIONS.values() if f.get(key)}
for scale, seen in scales.items():
    ordered = sorted(seen.items(), key=lambda cl: float(cl[0]))
    write(f"scales/{scale}.yaml", "labels:\n" + code_map(ordered, SCALES[scale] in NAME_LISTS))
for name in used("universe"):
    write(f"universes/{name}.yaml", f"text: {scalar(UNIVERSES[name])}\n")
for name in {c for _, c, _, _ in QUESTIONS.values()}:
    write(f"concepts/{name}.yaml", f"label: {scalar(CONCEPTS[name])}\n")
for unit in used("number"):
    write(f"units/{unit}.yaml", f"label: {unit}\n")

# The reserved codes the 2022 codebook gives these variables, each with its most common label.
reserved = {}
for entry in RESERVED.values():
    for r in entry["reserved"]:
        reserved.setdefault(r["code"], []).append(r["label"])
write("missing.yaml", "# The GSS's reserved codes, each written as its letter alone, as the codebook writes them.\nlabels:\n"
      + "".join(f"  {c}: {scalar(tidy(max(sorted(set(ls)), key=ls.count), False))}\n" for c, ls in sorted(reserved.items())))

for name, (folder, concept, title, f) in QUESTIONS.items():
    var = gss(name)
    entry = ENTRIES[var]
    page = entry["page"]
    out = [f"name: {name}", f"title: {scalar(title)}", f"text: {scalar(joined(f['text']))}",
           f"intent: {scalar(f'{CONCEPTS[concept]}, as the GSS Replicating Core measures it ({var.upper()}).')}",
           f"concept: {concept}"]
    if "universe" in f:
        out.append(f"universe: {f['universe']}")
    if "number" in f:
        out.append("number:\n  min: 0" + (f"\n  unit: {f['number']}" if f["number"] else ""))
    elif "scale" in f:
        out.append(f"responses: {f['scale']}")
    else:
        out.append("responses:\n" + code_map(codes(var), var in NAME_LISTS).rstrip("\n"))
    if "instruction" in f:
        out.append(f"instruction: {scalar(f['instruction'])}")
    # The first replay year that asked it, so a question's file (and its DDI version) doesn't change when a later year asks it again.
    survey = f"; asked in the {first_asked(name)} survey" if CUMULATIVE else ""
    out.append(f"source: {scalar(f'GSS {var.upper()}; {CITE}, page {page}{survey}')}")
    if CUMULATIVE:  # remarks stay in the source: some hold counts
        note = (f"Codebook stem: {entry['stem']} " if "stem" in entry else "") + f"Codebook wording: {entry['wording']}"
    else:
        note = f"Codebook label: {entry['label']}" + (f" Codebook notes: {entry['notes']}" if entry["notes"] else "")
    out.append(f"note: {scalar(note)}")
    if "fills" in f:
        out.append("fills:\n" + "\n".join(f"  {k}: {t}" for k, t in f["fills"].items()))
    if "variant_of" in f:
        out.append("variant_of:\n" + "\n".join(f"  {k}: {scalar(why)}" for k, why in f["variant_of"].items()))
    write(f"questions/{folder}/{name}.yaml", "\n".join(out) + "\n")

print(len(QUESTIONS), "questions asked by", YEAR, "; not yet asked:", " ".join(n for n in SPEC if n not in QUESTIONS))
