from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from delphiast.native import run_parser_to_xml  # noqa: E402


def main() -> int:
    snippets_dir = PROJECT_ROOT / "fixtures" / "Test" / "Snippets"
    expected_dir = PROJECT_ROOT / "tests" / "expected_xml"
    expected_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(snippets_dir.glob("*.pas"))
    if not files:
        print("No snippets found.", file=sys.stderr)
        return 1

    for file_path in files:
        xml_text = run_parser_to_xml(file_path)
        target = expected_dir / f"{file_path.stem}.xml"
        target.write_text(xml_text, encoding="utf-8")
        print(f"Wrote {target.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
