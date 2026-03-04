from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
ENV = dict(os.environ)
ENV["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{os.environ.get('PYTHONPATH', '')}"


def test_parser_demo_smoke() -> None:
    target_file = PROJECT_ROOT / "fixtures" / "Test" / "Snippets" / "tryexcept.pas"
    proc = subprocess.run(
        [PYTHON, "-m", "delphiast.demos.parser_demo", str(target_file)],
        cwd=PROJECT_ROOT,
        env=ENV,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "<UNIT" in proc.stdout


def test_project_indexer_demo_smoke() -> None:
    project_file = PROJECT_ROOT / "fixtures" / "Demo" / "ProjectIndexer" / "demo" / "DemoProject.dpr"
    proc = subprocess.run(
        [
            PYTHON,
            "-m",
            "delphiast.demos.project_indexer_demo",
            str(project_file),
            "--search-path",
            "sub2",
        ],
        cwd=PROJECT_ROOT,
        env=ENV,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "units" in proc.stdout
