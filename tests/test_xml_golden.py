from __future__ import annotations

from pathlib import Path

import pytest

from delphiast.native import run_parser_to_xml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNIPPETS_DIR = PROJECT_ROOT / "fixtures" / "Test" / "Snippets"
EXPECTED_DIR = PROJECT_ROOT / "tests" / "expected_xml"
SNIPPET_FILES = sorted(SNIPPETS_DIR.glob("*.pas"))


@pytest.mark.parametrize("snippet_path", SNIPPET_FILES, ids=lambda p: p.name)
def test_xml_matches_golden(snippet_path: Path) -> None:
    expected_path = EXPECTED_DIR / f"{snippet_path.stem}.xml"
    assert expected_path.exists(), f"Missing golden file: {expected_path}"

    actual_xml = run_parser_to_xml(snippet_path)
    expected_xml = expected_path.read_text(encoding="utf-8")
    assert actual_xml == expected_xml
