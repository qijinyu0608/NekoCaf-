from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lab2_batch3_common import ADR_RECORDS, ROADMAP, adr_markdown_dir, adr_package_dir  # noqa: E402


class Lab2Batch3DataTest(unittest.TestCase):
    def test_adr_records_cover_required_topics(self) -> None:
        self.assertGreaterEqual(len(ADR_RECORDS), 7)
        self.assertEqual(ADR_RECORDS[0]["id"], "0001")
        expected_topics = {
            "ADR 制度",
            "服务拆分粒度",
            "数据库选型",
            "消息中间件",
            "API 风格",
            "鉴权方案",
            "跨境数据同步策略",
        }
        actual_topics = {record["topic"] for record in ADR_RECORDS}
        self.assertEqual(actual_topics, expected_topics)

    def test_roadmap_has_three_milestones(self) -> None:
        self.assertEqual(len(ROADMAP["milestones"]), 3)
        codes = [item["code"] for item in ROADMAP["milestones"]]
        self.assertEqual(codes, ["M1", "M2", "M3"])
        for item in ROADMAP["milestones"]:
            self.assertTrue(item["definition_of_success"])
            self.assertTrue(item["deliverables"])

    def test_output_locations_are_stable(self) -> None:
        self.assertIn("docs/adr", str(adr_markdown_dir()))
        self.assertIn("docs/lab2/source", str(adr_package_dir()))


if __name__ == "__main__":
    unittest.main()
