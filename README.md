# DelphiAST Python

Python 3.11 package for DelphiAST with a bundled FreePascal bridge.

## Highlights

- Delphi-style Python API (`TPasSyntaxTreeBuilder`, `TProjectIndexer`, `TSyntaxTreeWriter`)
- Bundled DelphiAST Pascal source under `src/delphiast/_vendor/Source`
- Native bridge helper in `src/delphiast/_vendor/tools/pascal_bridge`
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
./scripts/generate_golden_from_pascal.sh
```

## Demo

```bash
python3 -m delphiast.demos.parser_demo fixtures/Test/Snippets/tryexcept.pas
python3 -m delphiast.demos.project_indexer_demo fixtures/Demo/ProjectIndexer/demo/DemoProject.dpr --search-path sub2
```

## Notes

- Runtime does not require `fpc` on platforms with a bundled native bridge binary.
- Current bundled binary: `linux-x86_64`.
- If your platform has no bundled binary, enable fallback compilation with:
  `DELPHIAST_ALLOW_FPC_BUILD=1` (requires `fpc` in `PATH`).
- Fallback build output defaults to `~/.cache/delphiast/native_build`.
- You can override fallback build location with `DELPHIAST_BUILD_DIR`.
