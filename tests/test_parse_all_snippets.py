from __future__ import annotations

from pathlib import Path

import pytest

from delphiast import TPasSyntaxTreeBuilder, TSyntaxNodeType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNIPPETS_DIR = PROJECT_ROOT / "fixtures" / "Test" / "Snippets"
SNIPPET_FILES = sorted(SNIPPETS_DIR.glob("*.pas"))


@pytest.mark.parametrize("snippet_path", SNIPPET_FILES, ids=lambda p: p.name)
def test_parse_all_snippets(snippet_path: Path) -> None:
    root = TPasSyntaxTreeBuilder.RunFile(str(snippet_path))
    assert root.Typ == TSyntaxNodeType.ntUnit
    assert root.HasChildren
