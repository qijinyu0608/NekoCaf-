from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lab2_batch2_common import (  # noqa: E402
    C4_VIEWS,
    CROSS_BORDER_RULES,
    DATA_MODEL_CONTEXTS,
    MULTI_TENANT_STRATEGY,
    OPENAPI_SPECS,
    count_entities,
)


class Lab2Batch2DataTest(unittest.TestCase):
    def test_c4_views_cover_required_levels(self) -> None:
        files = [view["file"] for view in C4_VIEWS]
        self.assertEqual(len(C4_VIEWS), 5)
        self.assertIn("L1_System_Context.drawio", files)
        self.assertIn("L2_Container.drawio", files)
        self.assertIn("L3_Component_Member.drawio", files)
        self.assertIn("L3_Component_Reservation.drawio", files)
        self.assertIn("L4_Code_ReservationCore.drawio", files)

    def test_openapi_specs_keep_required_sections(self) -> None:
        self.assertEqual(set(OPENAPI_SPECS), {"member-service", "reservation-service"})
        for spec in OPENAPI_SPECS.values():
            self.assertEqual(spec["openapi"], "3.0.3")
            self.assertIn("description", spec["info"])
            self.assertTrue(spec["servers"])
            self.assertIn("securitySchemes", spec["components"])
            self.assertIn("responses", spec["components"])
            found_rate_limit = False
            for path_item in spec["paths"].values():
                for operation in path_item.values():
                    if isinstance(operation, dict) and "x-ratelimit-limit" in operation:
                        found_rate_limit = True
            self.assertTrue(found_rate_limit)

    def test_er_model_contains_at_least_15_entities(self) -> None:
        self.assertGreaterEqual(count_entities(), 15)

    def test_er_model_contains_gdpr_and_tenant_strategy(self) -> None:
        self.assertIn("行级隔离", MULTI_TENANT_STRATEGY)
        self.assertGreaterEqual(len(CROSS_BORDER_RULES), 3)
        gdpr_fields = 0
        for context in DATA_MODEL_CONTEXTS:
            self.assertIn("tenant_strategy", context)
            for entity in context["entities"]:
                for field_name, _, _ in entity["fields"]:
                    if "[GDPR]" in field_name:
                        gdpr_fields += 1
        self.assertGreaterEqual(gdpr_fields, 3)


if __name__ == "__main__":
    unittest.main()
