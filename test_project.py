import json
from pathlib import Path
import unittest

from project import analyze


def example():
    return json.loads(Path(__file__).with_name("example.json").read_text(encoding="utf-8"))


class ProjectTests(unittest.TestCase):
    def test_prefers_complete_clean_take(self):
        result = analyze(example())
        self.assertEqual(result["rows"][0]["Take"], "A02")
        self.assertEqual(result["rows"][-1]["Take"], "A03")
        self.assertEqual(result["metrics"]["Eligible"], 3)

    def test_matching_respects_order_and_repetitions(self):
        data = {"script":"blue blue red", "target_seconds":1, "takes":[
                {"id":"reverse", "transcript":"red blue", "seconds":1,"defects":[]}]}
        self.assertEqual(analyze(data)["rows"][0]["Script covered (%)"], 33.3)

    def test_all_blocked(self):
        data = example()
        data["takes"] = [data["takes"][2]]
        self.assertEqual(analyze(data)["metrics"]["Eligible"], 0)
        self.assertIn("pickup", analyze(data)["summary"])

    def test_rejects_invalid_defect_severity(self):
        data = example()
        data["takes"][2]["defects"][0]["severity"] = "unknown"
        with self.assertRaises(ValueError):
            analyze(data)


if __name__ == "__main__":
    unittest.main()
