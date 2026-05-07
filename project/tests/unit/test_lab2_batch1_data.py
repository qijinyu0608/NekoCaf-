from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lab2_common  # noqa: E402


class Lab2Batch1DataTest(unittest.TestCase):
    def test_top_10_qas_are_defined(self) -> None:
        self.assertEqual(len(lab2_common.QUALITY_ATTRIBUTE_SCENARIOS), 10)

    def test_event_storming_has_at_least_30_domain_events(self) -> None:
        self.assertGreaterEqual(len(lab2_common.DOMAIN_EVENTS), 30)

    def test_context_map_has_at_least_6_bounded_contexts(self) -> None:
        self.assertGreaterEqual(len(lab2_common.BOUNDED_CONTEXTS), 6)

    def test_each_bounded_context_traces_back_to_at_least_3_requirements(self) -> None:
        for context in lab2_common.BOUNDED_CONTEXTS:
            self.assertGreaterEqual(len(context["requirements"]), 3, context["id"])

    def test_candidate_architectures_keep_two_options_for_atam(self) -> None:
        self.assertEqual(len(lab2_common.CANDIDATE_ARCHITECTURES), 2)


if __name__ == "__main__":
    unittest.main()
