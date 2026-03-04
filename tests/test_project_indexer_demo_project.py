from __future__ import annotations

from pathlib import Path

from delphiast import TProjectIndexer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_FILE = PROJECT_ROOT / "fixtures" / "Demo" / "ProjectIndexer" / "demo" / "DemoProject.dpr"


def test_project_indexer_on_demo_project() -> None:
    indexer = TProjectIndexer()
    indexer.SearchPath = "sub2"
    indexer.Index(str(PROJECT_FILE))

    parsed_names = {item.Name.lower() for item in indexer.ParsedUnits}
    assert "demoproject" in parsed_names
    assert "unit1" in parsed_names
    assert "unit2" in parsed_names
    assert len(indexer.Problems) >= 0
