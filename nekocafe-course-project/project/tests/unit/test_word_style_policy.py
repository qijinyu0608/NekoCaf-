from pathlib import Path
import sys
import unittest

from docx import Document


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import build_foundation_docs  # noqa: E402
import build_lab1_docs  # noqa: E402
import build_lab2_docs  # noqa: E402


EXPECTED_BLACK_STYLES = [
    "Normal",
    "Title",
    "Heading 1",
    "Heading 2",
    "Heading 3",
    "List Bullet",
    "List Number",
]


def color_hex(style) -> str | None:
    color = style.font.color.rgb
    return None if color is None else str(color)


class WordStylePolicyTest(unittest.TestCase):
    def assert_black_text_policy(self, apply_style) -> None:
        doc = Document()
        apply_style(doc)

        for style_name in EXPECTED_BLACK_STYLES:
            if style_name not in doc.styles:
                continue
            self.assertEqual(color_hex(doc.styles[style_name]), "000000", style_name)

    def test_foundation_docs_apply_black_text_policy(self) -> None:
        self.assert_black_text_policy(build_foundation_docs.apply_page_style)

    def test_lab1_docs_apply_black_text_policy(self) -> None:
        self.assert_black_text_policy(build_lab1_docs.apply_page_style)

    def test_lab2_docs_apply_black_text_policy(self) -> None:
        self.assert_black_text_policy(build_lab2_docs.apply_page_style)


if __name__ == "__main__":
    unittest.main()
