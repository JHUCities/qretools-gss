"""Write this GSS example workspace from kjhealy/gssrdoc's gss_doc.

Usage: python -I tools/generate.py <doc.pkl> <workspace_dir>
<doc.pkl> is gssrdoc's data/gss_doc.rda, read with the `rdata` package and pickled
(a pandas DataFrame).
Wording, titles, codes and labels come from gss_doc. The spec below only says how each
question's wording is split into QREtools fields (text, universe, instruction, fills).
"""
import json
import os
import pickle
import re
import sys

doc = pickle.load(open(sys.argv[1], "rb")).set_index("variable")
OUT = sys.argv[2]

# The 2020 Replicating Core document's own category names, which become shared concepts.
CONCEPTS = {
    "race": "Race",
    "ethnicity": "Ethnicity",
    "hispanic_origin": "Hispanic origin",
    "siblings": "Siblings",
    "marital_status": "Marital status or cohabitation status",
    "number_of_children": "Number of children",
    "age_at_first_birth": "Age at birth of first child",
    "education": "Education",
    "religious_affiliation": "Religious affiliation",
    "household_income": "Household income",
    "citizenship_status": "Citizenship status",
    "language": "Language",
    "employment_status": "Employment status",
    "industry": "Industry",
    "sector": "Private or public sector",
    "number_of_employees": "Number of employees",
    "labor_supply": "Labor supply",
    "income_from_occupation": "Income from occupation",
    "size_of_workplace": "Size of workplace",
    "workplace_hierarchy": "Superiors/subordinates in workplace",
    "veteran_status": "Veteran status",
}

# Shared scales: response lists that two or more questions share word for word in gss_doc.
SCALES = {"yes_no": "widowed", "yes_no_3_4": "wksubs1", "race_census": "racecen1",
          "ancestry": "eth1", "college_major": "major1", "language_list": "othlang1",
          "income_12": "income"}

# name: (folder, concept, fields). Fields: text (as read to the respondent), universe,
# instruction, fills, number (its unit), scale, variant_of, and gss (the GSS variable
# name, when gss_doc spells it differently from the 2020 document).
D, W = "demographics", "work"
SPEC = {
    "racecen1": (D, "race", dict(text="What is your race? Indicate one or more races that you consider yourself to be.", scale="race_census")),
    "racecen2": (D, "race", dict(text="What is your race? Indicate one or more races that you consider yourself to be.", scale="race_census", variant_of={"racecen1": "the second race mentioned in answer to the same question"})),
    "racecen3": (D, "race", dict(text="What is your race? Indicate one or more races that you consider yourself to be.", scale="race_census", variant_of={"racecen1": "the third race mentioned in answer to the same question", "racecen2": "the third race mentioned, where racecen2 is the second"})),
    "race": (D, "race", dict(text="What race do you consider yourself?", instruction="CODE WITHOUT ASKING ONLY IF THERE IS NO DOUBT IN YOUR MIND. RECORD VERBATIM AND CODE.")),
    "eth1": (D, "ethnicity", dict(text="From what countries or part of the world did your ancestors come?", scale="ancestry")),
    "eth2": (D, "ethnicity", dict(text="From what countries or part of the world did your ancestors come?", scale="ancestry", variant_of={"eth1": "the second country mentioned in answer to the same question"})),
    "eth3": (D, "ethnicity", dict(text="From what countries or part of the world did your ancestors come?", scale="ancestry", variant_of={"eth1": "the third country mentioned in answer to the same question", "eth2": "the third country mentioned, where eth2 is the second"})),
    "hispanic": (D, "hispanic_origin", dict(text="Are you Spanish, Hispanic, or {{latino}}? Which group are you from?", instruction="IF R IS FEMALE, READ LATINA; IF MALE, READ LATINO. Ask which group only if yes.", fills={"latino": "text"})),
    "sibs": (D, "siblings", dict(text="How many brothers and sisters did you have? Please count those born alive, but no longer living, as well as those alive now. Also include stepbrothers and stepsisters, and children adopted by your parents.", number=None)),
    "marital": (D, "marital_status", dict(text="Are you currently--married, widowed, divorced, separated, or have you never been married?")),
    "widowed": (D, "marital_status", dict(text="Have you ever been widowed?", universe="currently_married_separated_divorced", scale="yes_no")),
    "divorced": (D, "marital_status", dict(gss="divorce", text="Have you ever been divorced or legally separated?", universe="currently_married_widowed", scale="yes_no")),
    "posslq": (D, "marital_status", dict(text="Which of these statements applies to you?", instruction="CODE ONE ONLY.")),
    "posslqy": (D, "marital_status", dict(text="Which of these statements applies to you?", instruction="CODE ONE ONLY.", variant_of={"posslq": "the Y form of the X/Y wording experiment: option 2 reads 'steady partner' for 'living as married'"})),
    "childs": (D, "number_of_children", dict(text="How many children have you ever had? Please count all that were born alive at any time (including any you had from a previous marriage).", number=None)),
    "agekdbrn": (D, "age_at_first_birth", dict(text="How old were you when your first child was born?", number="years")),
    "major1": (D, "education", dict(text="What was your major or field of study when you received your {{degree}} degree?", instruction="IF THE RESPONDENT RECEIVED MORE THAN ONE GRADUATE LEVEL DEGREE, ASK ABOUT THE HIGHEST DEGREE OBTAINED (E.G. ABOUT A Ph.D. RATHER THAN AN M.B.A). COUNT UP TO 2 MENTIONS.", fills={"degree": "text"}, scale="college_major")),
    "major2": (D, "education", dict(text="What was your major or field of study when you received your {{degree}} degree?", instruction="IF THE RESPONDENT RECEIVED MORE THAN ONE GRADUATE LEVEL DEGREE, ASK ABOUT THE HIGHEST DEGREE OBTAINED (E.G. ABOUT A Ph.D. RATHER THAN AN M.B.A). COUNT UP TO 2 MENTIONS.", fills={"degree": "text"}, scale="college_major", variant_of={"major1": "the second major mentioned in answer to the same question"})),
    "relig": (D, "religious_affiliation", dict(text="What is your religious preference? Is it Protestant, Catholic, Jewish, some other religion, or no religion?")),
    "denom": (D, "religious_affiliation", dict(text="What specific denomination is that, if any?")),
    "other": (D, "religious_affiliation", dict(text="What specific denomination is that, if any?", variant_of={"denom": "GSS's detailed list of other Protestant denominations, coded from the same question"})),
    "jew": (D, "religious_affiliation", dict(text="Do you consider yourself Orthodox, Conservative, Reform or none of these?", instruction="PROBE FOR EXACT DENOMINATION")),
    "reliten": (D, "religious_affiliation", dict(text="Would you call yourself a strong {{religion}} or a not very strong {{religion}}?", fills={"religion": "text"})),
    "income": (D, "household_income", dict(text="In which of these groups did your total family income, from all sources, fall last year before taxes, that is? Just tell me the letter.", scale="income_12")),
    "income16": (D, "household_income", dict(text="In which of these groups did your total family income, from all sources, fall last year -- {{last_year}} -- before taxes, that is. Just tell me the letter.", instruction="Total income includes interest or dividends, rent, Social Security, other pensions, alimony or child support, unemployment compensation, public aid (welfare), armed forces or veteran's allotment.", fills={"last_year": "number"}, variant_of={"income": "the 26-category version of the family income question"})),
    "uscitzn": (D, "citizenship_status", dict(text="Now we would like to ask you about U.S. citizenship. Are you…", universe="born_outside_us", note="Wording from the 2022 GSS codebook: gss_doc gives only a description.")),
    "fucitzn": (D, "citizenship_status", dict(text="Are you…")),
    "mnthsusa": (D, "citizenship_status", dict(text="How long have you lived in the United States? If you have lived in the United States for more than one period during your life, what is the total number of years you have lived in the United States?", universe="born_outside_us", number="months", variant_of={"yrsusa": "the months part of the answer, when it is less than a year"})),
    "yrsusa": (D, "citizenship_status", dict(gss="yearsusa", text="How long have you lived in the United States? If you have lived in the United States for more than one period during your life, what is the total number of years you have lived in the United States?", universe="born_outside_us", number="years")),
    "othlang": (D, "language", dict(text="Can you speak a language other than English [Spanish]?", scale="yes_no")),
    "othlang1": (D, "language", dict(text="What other language(s) do you speak?", universe="other_language_speakers", scale="language_list")),
    "othlang2": (D, "language", dict(text="What other language(s) do you speak?", universe="other_language_speakers", scale="language_list", variant_of={"othlang1": "the second language mentioned in answer to the same question"})),
    "betrlang": (D, "language", dict(text="Which language do you speak more fluent?", universe="other_language_speakers")),
    "spklang": (D, "language", dict(text="How well do you speak that language?", universe="other_language_speakers", instruction="IF SPEAKS 2 OR MORE, ASK ONLY OF THE MOST FLUENT LANGUAGE. READ CATEGORIES.")),
    "wrkstat": (W, "employment_status", dict(text="Last week were you working full time, part time, going to school, keeping house, or what?")),
    "evwork": (W, "employment_status", dict(text="Did you ever work for as long as one year?", universe="not_in_labor_force", scale="yes_no")),
    "wrkselffam": (W, "employment_status", dict(gss="wrkslffam", text="(Do/did) you work in your own family business or farm?", scale="yes_no")),
    "whatslf2": (W, "industry", dict(text="How would you classify the place where you (work/worked)? Was this mainly...?")),
    "wrkgovt": (W, "sector", dict(text="(Are/Were) you employed by the federal, state or local government or by a private employer (including non-profit organizations)?")),
    "wrkgovt1": (W, "sector", dict(text="Are/were you employed by the government? (Please consider federal, state, or local government.)", scale="yes_no")),
    "wrkgovt2": (W, "sector", dict(text="Are/were you employed by a private employer (including non-profit organizations)?", scale="yes_no")),
    "numemps": (W, "number_of_employees", dict(text="Do/did you have any employees? How many employees do/did you have?", universe="self_employed")),
    "hrs1": (W, "labor_supply", dict(text="How many hours did you work last week, at all jobs?", universe="working", number="hours")),
    "hrs2": (W, "labor_supply", dict(text="How many hours a week do you usually work, at all jobs?", universe="with_job_not_at_work", number="hours")),
    "weekswrk": (W, "labor_supply", dict(text="Now I'd like to ask you about last year. In {{last_year}} how many weeks did you work either full-time or part-time not counting work around the house--include paid vacations and sick leave?", fills={"last_year": "number"}, number="weeks")),
    "partfull": (W, "labor_supply", dict(text="When you worked in {{last_year}}, was it usually full or part time?", fills={"last_year": "number"})),
    "rincome": (W, "income_from_occupation", dict(text="In which of these groups did your earnings from {{occupation}} for last year--{{last_year}}--fall? That is, before taxes or other deductions. Just tell me the letter.", universe="earned_income", fills={"occupation": "text", "last_year": "number"}, scale="income_12")),
    "rincom16": (W, "income_from_occupation", dict(text="In which of these groups did your earnings from {{job}}, from all sources for {{last_year}} fall? That is, before taxes or other deductions. Just tell me the letter.", fills={"job": "text", "last_year": "number"}, variant_of={"rincome": "the 26-category version of the earnings question"})),
    "localnum": (W, "size_of_workplace", dict(text="About how many people work at the location where you work? (Count part-time as well as full-time employees in all areas, departments and buildings.)")),
    "wksub1": (W, "workplace_hierarchy", dict(text="Do you (does your (SPOUSE or PARTNER)) have a supervisor on (your/his/her) job to whom you are (he/she is) directly responsible?", scale="yes_no")),
    "wksubs1": (W, "workplace_hierarchy", dict(text="Does that person have a supervisor on the job to whom he is directly responsible?", universe="has_supervisor", scale="yes_no_3_4")),
    "wksup1": (W, "workplace_hierarchy", dict(text="In your (SPOUSE or PARTNER'S) job, (do you/does he/she) supervise anyone who is directly responsible to (you/him/her)?", scale="yes_no")),
    "wksups1": (W, "workplace_hierarchy", dict(text="Do any of those persons supervise anyone else?", universe="supervises_someone", scale="yes_no_3_4")),
    "vetyears": (W, "veteran_status", dict(text="Have you ever been on active duty for military training or service for two consecutive months or more? What was your total time on active duty?")),
}

# Universes: the "IF ..." filters in gss_doc's wording, as written there.
UNIVERSES = {
    "currently_married_separated_divorced": "IF CURRENTLY MARRIED, SEPARATED, OR DIVORCED",
    "currently_married_widowed": "IF CURRENTLY MARRIED OR WIDOWED",
    "born_outside_us": "If not born in US",
    "other_language_speakers": "Respondents who can speak a language other than English [Spanish] (follows OTHLANG)",
    "not_in_labor_force": "IF RETIRED, IN SCHOOL, KEEPING HOUSE, OR OTHER",
    "self_employed": "If self-employed",
    "working": "IF WORKING, FULL OR PART TIME",
    "with_job_not_at_work": "IF WITH A JOB, BUT NOT AT WORK",
    "earned_income": "IF YES to: Did you earn any income from (OCCUPATION DESCRIBED IN OCC-INDUSTRY) in [the previous year]?",
    "has_supervisor": "IF YES to WKSUB1 (has a supervisor)",
    "supervises_someone": "IF YES to WKSUP1 (supervises someone)",
}
UNITS = ["years", "months", "hours", "weeks"]

# gss_doc writes proper nouns in lower case. These lists are mostly names, so each word
# gets a capital, except small words such as "and" (SMALL).
NAME_LISTS = {"eth1", "othlang1", "relig", "other", "denom", "jew", "racecen1"}
# Proper nouns that get a capital in the other lists.
PROPER = ["hispanic", "latino", "spanish", "mexican", "american", "puerto rican", "cuban", "english", "french", "chinese", "italian", "german", "african", "alaska", "native", "pacific", "asian", "christian"]
SMALL = {"and", "or", "of", "the", "in", "a", "to", "&", "for", "general"}


def labels(var):
    raw = doc.loc[var, "value_labels"]
    pairs = [re.match(r"\[([^\]]+)\] (.*)", p, re.S) for p in re.split(r" / (?=\[)", raw)]
    return [(m[1], m[2].strip()) for m in pairs if not m[1].startswith("NA(")]


def tidy(label, names):
    label = re.sub(r"\bu\.s\.", "U.S.", re.sub(r"\bi\b", "I", label))
    label = re.sub(r"\b(" + "|".join(PROPER) + r")\b", lambda m: m[1].title(), label)
    if names:
        label = " ".join(w if w in SMALL else w[:1].upper() + w[1:] for w in label.split(" "))
    return label[:1].upper() + label[1:]


def scalar(s):
    plain = re.fullmatch(r"[A-Za-z(][^\n#]*", s) and ": " not in s and not s.endswith(":") \
        and s.lower() not in {"yes", "no", "true", "false", "on", "off", "null"} and not s.startswith(("[", "{", "*", "&", "!", "%", "@", "`"))
    return s if plain else json.dumps(s, ensure_ascii=False)


def code_map(var, names, indent="  "):
    return "".join(f'{indent}"{c}": {scalar(tidy(l, names))}\n' for c, l in labels(var))


def write(path, body):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(body)


scale_of = {src: name for name, src in SCALES.items()}
for name, src in SCALES.items():
    write(f"scales/{name}.yaml", "labels:\n" + code_map(src, src in NAME_LISTS))
for name, text in UNIVERSES.items():
    write(f"universes/{name}.yaml", f"text: {scalar(text)}\n")
for name, label in CONCEPTS.items():
    write(f"concepts/{name}.yaml", f"label: {scalar(label)}\n")
for unit in UNITS:
    write(f"units/{unit}.yaml", f"label: {unit}\n")

for name, (folder, concept, f) in SPEC.items():
    var = f.get("gss", name)
    r = doc.loc[var]
    title = tidy(r["description"], False)
    wording = re.sub(r"\s+", " ", r["question"]).strip()
    out = [f"name: {name}", f"title: {scalar(title)}", f"text: {scalar(f['text'])}",
           f"intent: {scalar(f'{CONCEPTS[concept]}, in the GSS Replicating Core: {r.description} ({var.upper()}).')}",
           f"concept: {concept}"]
    if "universe" in f:
        out.append(f"universe: {f['universe']}")
    if "number" in f:
        out.append("number:\n  min: 0" + (f"\n  unit: {f['number']}" if f["number"] else ""))
    elif "scale" in f:
        out.append(f"responses: {f['scale']}")
    else:
        out.append("responses:\n" + code_map(var, var in NAME_LISTS).rstrip("\n"))
    if "instruction" in f:
        out.append(f"instruction: {scalar(f['instruction'])}")
    out.append(f"source: {scalar(f'GSS {var.upper()}, {r.norc_url}')}")
    top = [l for c, l in labels(var)] if "number" in f else []
    note = (f.get("note", "") + " " if "note" in f else "") + f"GSS documentation wording: {wording}"
    if top:
        note += f" Released data label: {'; '.join(top)}."
    out.append(f"note: {scalar(note)}")
    if "fills" in f:
        out.append("fills:\n" + "\n".join(f"  {k}: {t}" for k, t in f["fills"].items()))
    if "variant_of" in f:
        out.append("variant_of:\n" + "\n".join(f"  {k}: {scalar(why)}" for k, why in f["variant_of"].items()))
    write(f"questions/{folder}/{name}.yaml", "\n".join(out) + "\n")

# Every name the spec refers to exists.
assert all(f.get("universe", next(iter(UNIVERSES))) in UNIVERSES for _, _, f in SPEC.values())
assert all(f.get("scale", "yes_no") in SCALES for _, _, f in SPEC.values())
assert all(k in SPEC for _, _, f in SPEC.values() for k in f.get("variant_of", {}))
print(len(SPEC), "questions")
