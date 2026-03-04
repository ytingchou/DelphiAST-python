from __future__ import annotations

import argparse
from pathlib import Path
import sys

from delphiast import TProjectIndexer


def main() -> int:
    parser = argparse.ArgumentParser(description="Index Delphi project uses/includes.")
    parser.add_argument("project", help="Path to .dpr project file")
    parser.add_argument("--search-path", default="", help="Semicolon-separated search path")
    args = parser.parse_args()

    project_path = Path(args.project)
    if not project_path.exists():
        print(f"File not found: {project_path}", file=sys.stderr)
        return 2

    indexer = TProjectIndexer()
    indexer.SearchPath = args.search_path
    indexer.Index(str(project_path))

    print(f"{len(indexer.ParsedUnits)} units")
    for item in indexer.ParsedUnits:
        print(f"{item.Name} in {item.Path}")

    print()
    print(f"{len(indexer.IncludeFiles)} includes")
    for item in indexer.IncludeFiles:
        print(f"{item.Name} @ {item.Path}")

    print()
    print(f"{len(indexer.NotFoundUnits)} not found")
    for unit_name in indexer.NotFoundUnits:
        print(unit_name)

    print()
    print(f"{len(indexer.Problems)} problems")
    for problem in indexer.Problems:
        print(f"{problem.ProblemType} {problem.FileName}: {problem.Description}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
