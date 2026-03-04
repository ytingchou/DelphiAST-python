from __future__ import annotations

from pathlib import Path
import tempfile

import pytest

from delphiast import ESyntaxTreeException, TPasSyntaxTreeBuilder


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNIPPETS_DIR = PROJECT_ROOT / "fixtures" / "Test" / "Snippets"


def test_include_file_parses() -> None:
    root = TPasSyntaxTreeBuilder.RunFile(str(SNIPPETS_DIR / "includefile.pas"))
    assert root.GetAttribute("name") == "includefile"


def test_syntax_error_surface() -> None:
    bad_source = "unit Broken;\ninterface\nprocedure X(\nimplementation\nend.\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pas", delete=False, encoding="utf-8") as handle:
        handle.write(bad_source)
        temp_name = handle.name

    with pytest.raises(ESyntaxTreeException):
        TPasSyntaxTreeBuilder.RunFile(temp_name)
