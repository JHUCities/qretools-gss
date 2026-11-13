"""Tests of tools/columns.py's map, on a hand-made DDI and hand-made labels. No GSS data.

Run: python3 -I -m unittest discover -s tools
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import columns  # noqa: E402


def string(value):
    return [{"Content": [{"MultilingualStringValue": {"Value": value}}]}]


def variable(name, **rest):
    return {
        "URN": f"urn:ddi:x:instrument-t.var-{name}:1",
        "VariableName": [{"String": [{"MultilingualStringValue": {"Value": name}}]}],
        **rest,
    }


CODES = {"$type": "CodeDomain", "CodeListReference": {"value": ["x", "q.codes", "1"]}}
DDI = {
    "Variable": {
        "a": variable("q", QuestionReference=[{"value": ["x", "q", "1"]}], VariableRepresentation={"ValueRepresentation": CODES}),
        "b": variable("born_in_us", VariableRepresentation={"ValueRepresentation": CODES}),
        "c": variable("label_1", OutParameter={"URN": "urn:out-label_1"}, VariableRepresentation={"ValueRepresentation": {"$type": "TextDomain"}}),
        "d": variable("last_year", VariableRepresentation={"ValueRepresentation": {"$type": "NumericDomain"}}),
    },
    "QuestionItem": {
        "x:q:1": {"BasedOnObject": {"BasedOnRationaleDescription": {"String": [{"MultilingualStringValue": {"Value": "GSS QCOL; page 1"}}]}}},
    },
    "ComputationItem": {"x:c:1": {"AssignedVariableReference": {"URN": "urn:out-label_1"}}},
    "CodeList": {
        "x:q.codes:1": {"ID": "q.codes", "Code": [{"Value": {"StringValue": "1"}}, {"Value": {"StringValue": "2"}}]},
        "x:missing-values.codes:1": {
            "ID": "missing-values.codes",
            "Code": [
                {"Value": {"StringValue": "D"}, "CategoryReference": {"value": ["x", "m-0", "1"]}},
                {"Value": {"StringValue": "I"}, "CategoryReference": {"value": ["x", "m-1", "1"]}},
            ],
        },
    },
    "Category": {"x:m-0:1": {"Label": string("Don't know")}, "x:m-1:1": {"Label": string("Not applicable")}},
}
RESERVED = {-100.0: "iap", -98.0: "don't know", -96.0: "see codebook"}
LABELS = {"qcol": {1.0: "yes", 2.0: "no", **RESERVED}, "born": {1.0: "yes", 2.0: "no", **RESERVED}}


class ColumnMap(unittest.TestCase):
    def test_map(self):
        the_map, without = columns.column_map(DDI, "sha256:0", LABELS, {})
        self.assertEqual(
            the_map,
            {
                "source": "gss",
                "ddi": "sha256:0",
                "answered_by": "ResearchData.Published",
                "citation": columns.CITATION,
                "respondent": "id",
                # "iap" is no answer, a label the workspace has is its letter, others stay as they are.
                "values": {"-98": "D", "-100": None},
                "columns": [
                    {"column": "qcol", "variable": "urn:ddi:x:instrument-t.var-q:1"},
                    {"column": "born", "variable": "urn:ddi:x:instrument-t.var-born_in_us:1"},
                ],
                "interview_date": {"column": "dateintv", "form": "MMDD", "year": "year"},
            },
        )
        self.assertEqual(
            without,
            [("label_1", "computed by the instrument, not data"), ("last_year", "an input that no GSS variable holds")],
        )

    def test_refuses_a_guess(self):
        with self.assertRaises(SystemExit):
            columns.column_map(DDI, "sha256:0", {**LABELS, "born": {-98.0: "dk"}}, {})
        with self.assertRaises(SystemExit):
            columns.column_map(DDI, "sha256:0", {"qcol": LABELS["qcol"]}, {})

    def test_filtered_and_censored(self):
        number = variable("kids", QuestionReference=[{"value": ["x", "kids", "1"]}], VariableRepresentation={"ValueRepresentation": {"$type": "NumericDomain"}})
        ddi = {
            **DDI,
            "Variable": {**DDI["Variable"], "e": number},
            "QuestionItem": {
                **DDI["QuestionItem"],
                "x:kids:1": {"BasedOnObject": {"BasedOnRationaleDescription": {"String": [{"MultilingualStringValue": {"Value": "GSS KIDS; page 2"}}]}}},
            },
        }
        kids = {0.0: "none", 1.0: "1", 8.0: "8 or more", 17.0: "17 and younger", 9.0: "a stray label", **RESERVED}
        with mock.patch.dict(columns.FILTERED, {"q": "held in another form"}):
            the_map, _ = columns.column_map(ddi, "sha256:0", {**LABELS, "kids": kids}, {})
        self.assertEqual(
            the_map["columns"],
            [
                {"column": "qcol", "variable": "urn:ddi:x:instrument-t.var-q:1", "filtered": True},
                {"column": "born", "variable": "urn:ddi:x:instrument-t.var-born_in_us:1"},
                # A label that is neither a range nor the number is printed, never taken as a cap.
                {"column": "kids", "variable": "urn:ddi:x:instrument-t.var-kids:1", "censored": {"8": "8 or more", "17": "17 and younger"}},
            ],
        )

    def test_metadata(self):
        labels = {
            **LABELS,
            "mode": {1.0: "in-person", 2.0: "by phone", 3.0: "web", **RESERVED},
            "wtss": dict(RESERVED),
            "oversamp": {1.0: "not 1982/1987", **RESERVED},
        }
        present = {"born": "Born in this country", "mode": "Mode", "wtss": "Weight variable", "oversamp": "Weights for black oversamples"}
        the_map, _ = columns.column_map(DDI, "sha256:0", labels, present)
        self.assertEqual(
            the_map["metadata"],
            [
                # `born` is an input, so it stays in `columns`; OVERSAMP is coded, so no weight.
                {
                    "column": "mode", "label": "Mode", "role": "mode", "unit": "Interviewer",
                    # A reserved code with a missing letter is a code; "iap" is no value; others aren't translated.
                    "codes": {"1": "in-person", "2": "by phone", "3": "web", "-98": "don't know"},
                    "modes": {"1": "Interview.FaceToFace.CAPIorCAMI", "2": "Interview.Telephone"},
                    "values": {"-100": None},
                },
                {
                    "column": "wtss", "label": "Weight variable", "role": "weight", "unit": {"other": "survey organization"},
                    "number": True, "weight": True,
                    # Every reserved code of a weight is no value, or it would be read as a weight.
                    "values": {"-96": None, "-98": None, "-100": None},
                },
            ],
        )
        self.assertEqual(the_map["weighting"], columns.WEIGHTING)

    def test_weighting_only_with_a_weight(self):
        labels = {**LABELS, "phase": {1.0: "one", 2.0: "two", **RESERVED}}
        the_map, _ = columns.column_map(DDI, "sha256:0", labels, {"phase": "Phase"})
        self.assertEqual([m["column"] for m in the_map["metadata"]], ["phase"])
        self.assertNotIn("weighting", the_map)
        self.assertNotIn("metadata", columns.column_map(DDI, "sha256:0", LABELS, {})[0])

    def test_refuses_a_mode_the_data_doesnt_label(self):
        with self.assertRaises(SystemExit):
            columns.column_map(DDI, "sha256:0", {**LABELS, "mode": {1.0: "in-person", **RESERVED}}, {"mode": "Mode"})

    def test_untermed_modes(self):
        entry = {"codes": {"1": "in-person", "2": "by phone", "3": "web", "-100": "iap"},
                 "modes": {"1": "Interview.FaceToFace.CAPIorCAMI", "2": "Interview.Telephone"}}
        self.assertEqual(columns.untermed_modes(entry, {"1", "3", "-100", ""}), ["web"])
        self.assertEqual(columns.untermed_modes({"codes": {"1": "one"}}, {"1"}), [])

    def test_cell(self):
        self.assertEqual([columns.cell(v) for v in (40.0, -100.0, 1.5, float("nan"))], ["40", "-100", "1.5", ""])


if __name__ == "__main__":
    unittest.main()
