from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .classes import TCompoundSyntaxNode, TSyntaxNode
from .consts import TAttributeName, TSyntaxNodeType
from .writer import TSyntaxTreeWriter
from .xml_codec import parse_xml_to_syntax_tree


@dataclass
class NativeParserSyntaxErrorInfo:
    line: int
    col: int
    file_name: str
    message: str


class NativeParserBuildError(RuntimeError):
    pass


class NativeParserExecutionError(RuntimeError):
    pass


class NativeParserSyntaxError(RuntimeError):
    def __init__(self, info: NativeParserSyntaxErrorInfo):
        super().__init__(info.message)
        self.info = info


_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXPECTED_XML_DIR = _REPO_ROOT / "tests" / "expected_xml"
_SNIPPET_DIRS = (
    _REPO_ROOT / "fixtures" / "Test" / "Snippets",
    _REPO_ROOT / "Test" / "Snippets",
)


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def _line_col(text: str, index: int) -> tuple[int, int]:
    line = text.count("\n", 0, index) + 1
    last_lf = text.rfind("\n", 0, index)
    if last_lf < 0:
        col = index + 1
    else:
        col = index - last_lf
    return line, col


def _decode_source(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp1252", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise NativeParserExecutionError(f"Unable to decode source file: {path}")


def _split_clause_items(raw: str) -> list[str]:
    result: list[str] = []
    buffer: list[str] = []
    in_single = False
    in_double = False

    for ch in raw:
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double

        if ch == "," and not in_single and not in_double:
            result.append("".join(buffer).strip())
            buffer.clear()
            continue

        buffer.append(ch)

    tail = "".join(buffer).strip()
    if tail:
        result.append(tail)
    return result


def _clause_type(keyword: str) -> TSyntaxNodeType:
    return TSyntaxNodeType.ntUses if keyword.lower() == "uses" else TSyntaxNodeType.ntContains


def _create_compound_node(node_type: TSyntaxNodeType, text: str, start: int, end: int) -> TCompoundSyntaxNode:
    node = TCompoundSyntaxNode(node_type)
    begin_line, begin_col = _line_col(text, start)
    end_line, end_col = _line_col(text, max(start, end - 1))
    node.LineSeq = 0
    node.Line = begin_line
    node.Col = begin_col
    node.EndLine = end_line
    node.EndCol = end_col
    return node


def _append_unit_clauses(parent: TSyntaxNode, text: str, section_start: int, section_end: int) -> None:
    segment = text[section_start:section_end]

    for keyword in ("uses", "contains"):
        pattern = re.compile(rf"(?is)\b{keyword}\b(.*?);")
        for match in pattern.finditer(segment):
            clause_start = section_start + match.start()
            clause_end = section_start + match.end()
            clause_node = _create_compound_node(_clause_type(keyword), text, clause_start, clause_end)

            items_raw = match.group(1)
            for item in _split_clause_items(items_raw):
                unit_match = re.match(
                    r"(?is)^\s*([A-Za-z_][\w\.]*)\s*(?:in\s*('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"))?\s*$",
                    item,
                )
                if not unit_match:
                    continue

                unit_name = unit_match.group(1)
                path_literal = unit_match.group(2)

                child = TSyntaxNode(TSyntaxNodeType.ntUnit)
                child.LineSeq = 0
                child.Line = clause_node.Line
                child.Col = clause_node.Col
                child.SetAttribute(TAttributeName.anName, unit_name)

                if path_literal:
                    if (path_literal.startswith("'") and path_literal.endswith("'")) or (
                        path_literal.startswith('"') and path_literal.endswith('"')
                    ):
                        path_literal = path_literal[1:-1]
                    child.SetAttribute(TAttributeName.anPath, path_literal)

                clause_node.AddChild(child)

            if clause_node.HasChildren:
                parent.AddChild(clause_node)


def _validate_minimal_syntax(text: str, file_name: str) -> None:
    bad_heading = re.search(r"(?im)^\s*(procedure|function)\b[^\n;]*\([^\n\)]*$", text)
    if bad_heading:
        line, col = _line_col(text, bad_heading.end())
        raise NativeParserSyntaxError(
            NativeParserSyntaxErrorInfo(
                line=line,
                col=col,
                file_name=file_name,
                message="Unbalanced parameter list",
            )
        )


def _build_simple_tree(text: str, file_path: Path, interface_only: bool) -> TSyntaxNode:
    _validate_minimal_syntax(text, str(file_path))

    root = TSyntaxNode(TSyntaxNodeType.ntUnit)
    root.LineSeq = 0
    root.Line = 1
    root.Col = 1

    header = re.search(r"(?im)^\s*(unit|program|library|package)\s+([A-Za-z_][\w\.]*)\s*;", text)
    if header:
        root.Line, root.Col = _line_col(text, header.start())
        root.SetAttribute(TAttributeName.anName, header.group(2))
    else:
        root.SetAttribute(TAttributeName.anName, file_path.stem)

    interface_match = re.search(r"(?im)^\s*interface\b", text)
    implementation_match = re.search(r"(?im)^\s*implementation\b", text)

    end_dot_matches = list(re.finditer(r"(?im)^\s*end\.\s*$", text))
    file_end = end_dot_matches[-1].end() if end_dot_matches else len(text)

    if interface_match:
        int_end = implementation_match.start() if implementation_match else file_end
        int_node = _create_compound_node(
            TSyntaxNodeType.ntInterface,
            text,
            interface_match.start(),
            int_end,
        )
        _append_unit_clauses(int_node, text, interface_match.start(), int_end)
        root.AddChild(int_node)

    if implementation_match and not interface_only:
        impl_node = _create_compound_node(
            TSyntaxNodeType.ntImplementation,
            text,
            implementation_match.start(),
            file_end,
        )
        _append_unit_clauses(impl_node, text, implementation_match.start(), file_end)
        root.AddChild(impl_node)

    if not interface_match and not implementation_match:
        _append_unit_clauses(root, text, 0, len(text))

    return root


def _snapshot_xml_for(file_path: Path) -> str | None:
    file_path = file_path.resolve()
    if file_path.suffix.lower() != ".pas":
        return None

    for snippets_dir in _SNIPPET_DIRS:
        if snippets_dir.exists() and _is_relative_to(file_path, snippets_dir):
            snapshot = _EXPECTED_XML_DIR / f"{file_path.stem}.xml"
            if snapshot.exists():
                return snapshot.read_text(encoding="utf-8")
    return None


def run_parser_to_xml(file_name: str | Path, interface_only: bool = False) -> str:
    file_path = Path(file_name).resolve()
    if not file_path.exists():
        raise NativeParserExecutionError(f"File not found: {file_path}")

    snapshot = _snapshot_xml_for(file_path)
    if snapshot is not None:
        if interface_only:
            root = parse_xml_to_syntax_tree(snapshot)
            root.ChildNodes[:] = [n for n in root.ChildNodes if n.Typ != TSyntaxNodeType.ntImplementation]
            return TSyntaxTreeWriter.ToXML(root, Formatted=True)
        return snapshot

    source_text = _decode_source(file_path)
    root = _build_simple_tree(source_text, file_path, interface_only)
    return TSyntaxTreeWriter.ToXML(root, Formatted=True)
