"""Tests of tools/columns.py's map, on a hand-made DDI and hand-made labels. No GSS data.

Run: python3 -I -m unittest discover -s tools
"""
import os
import sys
import unittest

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
        the_map, without = columns.column_map(DDI, "sha256:0", LABELS)
        self.assertEqual(
            the_map,
            {
                "ddi": "sha256:0",
                "respondent": "id",
                # "iap" is no answer, a label the workspace has is its letter, others stay as they are.
                "values": {"-98": "D", "-100": None},
                "columns": [
                    {"column": "qcol", "variable": "urn:ddi:x:instrument-t.var-q:1"},
                    {"column": "born", "variable": "urn:ddi:x:instrument-t.var-born_in_us:1"},
                ],
            },
        )
        self.assertEqual(
            without,
            [("label_1", "computed by the instrument, not data"), ("last_year", "an input that no GSS variable holds")],
        )

    def test_refuses_a_guess(self):
        with self.assertRaises(SystemExit):
            columns.column_map(DDI, "sha256:0", {**LABELS, "born": {-98.0: "dk"}})
        with self.assertRaises(SystemExit):
            columns.column_map(DDI, "sha256:0", {"qcol": LABELS["qcol"]})

    def test_cell(self):
        self.assertEqual([columns.cell(v) for v in (40.0, -100.0, 1.5, float("nan"))], ["40", "-100", "1.5", ""])


if __name__ == "__main__":
    unittest.main()
