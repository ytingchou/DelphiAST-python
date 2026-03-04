from __future__ import annotations

import argparse
from pathlib import Path
import sys

from delphiast import TPasSyntaxTreeBuilder, TSyntaxTreeWriter


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Delphi/Pascal source and print DelphiAST XML.")
    parser.add_argument("file", help="Path to .pas/.dpr file")
    parser.add_argument("--interface-only", action="store_true", help="Parse interface section only")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        return 2

    root = TPasSyntaxTreeBuilder.RunFile(str(file_path), InterfaceOnly=args.interface_only)
    xml = TSyntaxTreeWriter.ToXML(root, Formatted=True)
    sys.stdout.write(xml)
    if not xml.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
