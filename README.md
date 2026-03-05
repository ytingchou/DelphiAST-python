# DelphiAST Python

Pure Python 3.11 package for DelphiAST-style APIs.

## Highlights

- Delphi-style Python API (`TPasSyntaxTreeBuilder`, `TProjectIndexer`, `TSyntaxTreeWriter`)
- Pure Python parser backend (no external compiler/runtime dependency)
- Pytest suite with fixture corpus and XML golden outputs

## Install (dev)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Regenerate golden XML

```bash
python3 scripts/generate_golden.py
```

## Demo

```bash
python3 -m delphiast.demos.parser_demo fixtures/Test/Snippets/tryexcept.pas
python3 -m delphiast.demos.project_indexer_demo fixtures/Demo/ProjectIndexer/demo/DemoProject.dpr --search-path sub2
```

## Notes

- Runtime is pure Python and does not require `fpc` or a bundled native binary.

## GitHub / PyPI

- CI workflow: `.github/workflows/ci.yml`
- Publish workflow: `.github/workflows/publish.yml`
  - Triggered on GitHub Release publication or manual dispatch.
  - Uses trusted publishing (`id-token: write`).
