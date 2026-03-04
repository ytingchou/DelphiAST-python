from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
import re

from .ast_builder import ESyntaxTreeException, TPasSyntaxTreeBuilder
from .classes import TIncludeFileInfo, TProblemInfo, TSyntaxNode, TUnitInfo
from .consts import TAttributeName, TSyntaxNodeType


class TProblemType(IntEnum):
    ptCantFindFile = 0
    ptCantOpenFile = 1
    ptCantParseFile = 2


@dataclass
class _ParseContext:
    file_path: Path
    unit_name: str
    is_project: bool


class TProjectIndexer:
    def __init__(self) -> None:
        self.Defines = ""
        self.Options = {"piUseDefinesDefinedByCompiler"}
        self.SearchPath = ""

        self.ParsedUnits: list[TUnitInfo] = []
        self.IncludeFiles: list[TIncludeFileInfo] = []
        self.Problems: list[TProblemInfo] = []
        self.NotFoundUnits: list[str] = []

        self._parsed_units_by_name: dict[str, TUnitInfo] = {}
        self._include_keys: set[tuple[str, str]] = set()
        self._project_folder = Path.cwd()

    def _reset(self) -> None:
        self.ParsedUnits.clear()
        self.IncludeFiles.clear()
        self.Problems.clear()
        self.NotFoundUnits.clear()
        self._parsed_units_by_name.clear()
        self._include_keys.clear()

    def _log_problem(self, problem_type: TProblemType, file_name: str, description: str) -> None:
        self.Problems.append(
            TProblemInfo(
                ProblemType=int(problem_type),
                FileName=file_name,
                Description=description,
            )
        )

    def _search_paths(self, relative_to_folder: Path) -> list[Path]:
        paths = [relative_to_folder, self._project_folder]
        if self.SearchPath:
            for item in self.SearchPath.split(";"):
                item = item.strip()
                if not item:
                    continue
                path = Path(item)
                if not path.is_absolute():
                    path = self._project_folder / path
                paths.append(path)
        return paths

    def _find_file(self, unit_name: str, relative_to_folder: Path, path_hint: str = "") -> Path | None:
        if path_hint:
            hint = Path(path_hint)
            if not hint.is_absolute():
                hint = relative_to_folder / hint
            if hint.exists():
                return hint.resolve()

        candidates = [f"{unit_name}.pas", f"{unit_name}.dpr"]
        for base in self._search_paths(relative_to_folder):
            for candidate in candidates:
                full = (base / candidate).resolve()
                if full.exists():
                    return full
        return None

    def _iter_nodes(self, root: TSyntaxNode):
        stack = [root]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.ChildNodes))

    def _scan_include_directives(self, file_path: Path) -> None:
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self._log_problem(TProblemType.ptCantOpenFile, str(file_path), str(exc))
            return

        pattern = re.compile(r"\{\$\s*(?:I|INCLUDE)\s+([^}]+)\}", re.IGNORECASE)
        for match in pattern.finditer(text):
            raw_name = match.group(1).strip()
            if (raw_name.startswith("'") and raw_name.endswith("'")) or (
                raw_name.startswith('"') and raw_name.endswith('"')
            ):
                raw_name = raw_name[1:-1]

            include_path = (file_path.parent / raw_name).resolve()
            key = (raw_name.lower(), str(include_path))
            if key in self._include_keys:
                continue
            self._include_keys.add(key)
            self.IncludeFiles.append(TIncludeFileInfo(Name=raw_name, Path=str(include_path)))

    def _append_used_units(self, root: TSyntaxNode) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for node in self._iter_nodes(root):
            if node.Typ not in (TSyntaxNodeType.ntUses, TSyntaxNodeType.ntContains):
                continue
            for child in node.ChildNodes:
                if child.Typ != TSyntaxNodeType.ntUnit:
                    continue
                unit_name = child.GetAttribute(TAttributeName.anName)
                if not unit_name:
                    continue
                path_hint = child.GetAttribute(TAttributeName.anPath)
                result.append((unit_name, path_hint))
        return result

    def _record_not_found(self, unit_name: str) -> None:
        if unit_name not in self.NotFoundUnits:
            self.NotFoundUnits.append(unit_name)

    def _parse_unit(self, ctx: _ParseContext) -> None:
        unit_key = ctx.unit_name.lower()
        if unit_key in self._parsed_units_by_name:
            return

        self._scan_include_directives(ctx.file_path)

        try:
            syntax_tree = TPasSyntaxTreeBuilder.RunFile(str(ctx.file_path), InterfaceOnly=False)
        except ESyntaxTreeException as exc:
            self._log_problem(TProblemType.ptCantParseFile, str(ctx.file_path), str(exc))
            self._record_not_found(ctx.unit_name)
            return
        except OSError as exc:
            self._log_problem(TProblemType.ptCantOpenFile, str(ctx.file_path), str(exc))
            self._record_not_found(ctx.unit_name)
            return

        unit_info = TUnitInfo(Name=ctx.unit_name, Path=str(ctx.file_path), SyntaxTree=syntax_tree)
        self._parsed_units_by_name[unit_key] = unit_info

        for used_unit, path_hint in self._append_used_units(syntax_tree):
            next_file = self._find_file(used_unit, ctx.file_path.parent, path_hint)
            if next_file is None:
                self._record_not_found(used_unit)
                self._log_problem(
                    TProblemType.ptCantFindFile,
                    str(ctx.file_path),
                    f"Cannot find unit '{used_unit}'",
                )
                continue
            self._parse_unit(_ParseContext(file_path=next_file, unit_name=used_unit, is_project=False))

    def Index(self, file_name: str) -> None:
        self._reset()

        root_file = Path(file_name).resolve()
        self._project_folder = root_file.parent

        if not root_file.exists():
            self._log_problem(TProblemType.ptCantFindFile, str(root_file), "Project file not found")
            self._record_not_found(root_file.stem)
            return

        self._parse_unit(_ParseContext(file_path=root_file, unit_name=root_file.stem, is_project=True))

        self.ParsedUnits = sorted(
            self._parsed_units_by_name.values(),
            key=lambda item: item.Name.lower(),
        )
        self.IncludeFiles = sorted(self.IncludeFiles, key=lambda item: (item.Name.lower(), item.Path.lower()))
        self.NotFoundUnits.sort(key=str.lower)
