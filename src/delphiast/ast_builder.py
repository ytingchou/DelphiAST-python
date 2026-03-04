from __future__ import annotations

from pathlib import Path
import tempfile
from typing import Callable

from .classes import EParserException, TCommentNode, TSyntaxNode, TValuedSyntaxNode
from .consts import TSyntaxNodeType
from .native import NativeParserSyntaxError, run_parser_to_xml
from .xml_codec import parse_xml_to_syntax_tree


class ESyntaxTreeException(EParserException):
    def __init__(self, line: int, col: int, file_name: str, msg: str, syntax_tree: TSyntaxNode):
        super().__init__(line, col, file_name, msg)
        self.SyntaxTree = syntax_tree


class TPasSyntaxTreeBuilder:
    def __init__(self) -> None:
        self.InterfaceOnly = False
        self.IncludeHandler = None
        self.OnHandleString: Callable[[str], str | None] | None = None
        self.Comments: list[TCommentNode] = []

    def _apply_string_handler(self, node: TSyntaxNode) -> None:
        if self.OnHandleString is None:
            return

        if node.FileName:
            new_value = self.OnHandleString(node.FileName)
            if isinstance(new_value, str):
                node.FileName = new_value

        if isinstance(node, TValuedSyntaxNode):
            new_value = self.OnHandleString(node.Value)
            if isinstance(new_value, str):
                node.Value = new_value
            else:
                self.OnHandleString(node.Value)

        for key, value in node.Attributes:
            new_value = self.OnHandleString(value)
            if isinstance(new_value, str):
                node.SetAttribute(key, new_value)

        for child in node.ChildNodes:
            self._apply_string_handler(child)

    def _run_file(self, file_name: str | Path) -> TSyntaxNode:
        try:
            xml_text = run_parser_to_xml(file_name, interface_only=self.InterfaceOnly)
        except NativeParserSyntaxError as exc:
            partial_tree = TSyntaxNode(TSyntaxNodeType.ntUnit)
            raise ESyntaxTreeException(
                exc.info.line,
                exc.info.col,
                exc.info.file_name,
                exc.info.message,
                partial_tree,
            ) from exc

        root = parse_xml_to_syntax_tree(xml_text)
        self.Comments = self._collect_comments(root)
        self._apply_string_handler(root)
        return root

    @staticmethod
    def _collect_comments(node: TSyntaxNode) -> list[TCommentNode]:
        comments: list[TCommentNode] = []
        stack: list[TSyntaxNode] = [node]
        while stack:
            current = stack.pop()
            if isinstance(current, TCommentNode):
                comments.append(current)
            stack.extend(reversed(current.ChildNodes))
        return comments

    def RunStream(self, SourceStream) -> TSyntaxNode:
        stream_name = getattr(SourceStream, "name", None)
        if stream_name:
            path_candidate = Path(stream_name)
            if path_candidate.exists():
                return self._run_file(path_candidate)

        payload = SourceStream.read()
        if isinstance(payload, bytes):
            content = payload.decode("utf-8", errors="replace")
        else:
            content = str(payload)

        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".pas", delete=False) as handle:
            handle.write(content)
            temp_name = handle.name
        try:
            return self._run_file(temp_name)
        finally:
            Path(temp_name).unlink(missing_ok=True)

    @classmethod
    def Run(
        cls,
        FileName: str,
        InterfaceOnly: bool = False,
        IncludeHandler=None,
        OnHandleString: Callable[[str], str | None] | None = None,
    ) -> TSyntaxNode:
        builder = cls()
        builder.InterfaceOnly = InterfaceOnly
        builder.IncludeHandler = IncludeHandler
        builder.OnHandleString = OnHandleString
        return builder._run_file(FileName)

    @classmethod
    def RunFile(
        cls,
        FileName: str,
        InterfaceOnly: bool = False,
        IncludeHandler=None,
        OnHandleString: Callable[[str], str | None] | None = None,
    ) -> TSyntaxNode:
        return cls.Run(FileName, InterfaceOnly, IncludeHandler, OnHandleString)

    @classmethod
    def RunFromFile(
        cls,
        FileName: str,
        InterfaceOnly: bool = False,
        IncludeHandler=None,
        OnHandleString: Callable[[str], str | None] | None = None,
    ) -> TSyntaxNode:
        return cls.Run(FileName, InterfaceOnly, IncludeHandler, OnHandleString)
