from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable

from .consts import (
    ATTRIBUTE_NAME_BY_STRING,
    ATTRIBUTE_NAME_STRINGS,
    SYNTAX_NODE_NAMES,
    TSyntaxNodeType,
    TAttributeName,
)


class EParserException(Exception):
    def __init__(self, line: int, col: int, file_name: str, msg: str):
        super().__init__(msg)
        self.Line = line
        self.Col = col
        self.FileName = file_name


class TSyntaxNode:
    def __init__(self, typ: TSyntaxNodeType):
        self.FTyp = typ
        self.FLineSeq = 0
        self.FCol = 0
        self.FLine = 0
        self.FFileName = ""
        self.FParentNode: TSyntaxNode | None = None
        self._attributes: "OrderedDict[str, str]" = OrderedDict()
        self._child_nodes: list[TSyntaxNode] = []

    def Clone(self) -> "TSyntaxNode":
        clone = self.__class__(self.FTyp)
        clone.FLineSeq = self.FLineSeq
        clone.FCol = self.FCol
        clone.FLine = self.FLine
        clone.FFileName = self.FFileName
        for key, value in self._attributes.items():
            clone._attributes[key] = value
        for child in self._child_nodes:
            clone.AddChild(child.Clone())
        return clone

    def AssignPositionFrom(self, node: "TSyntaxNode") -> None:
        self.FLineSeq = node.LineSeq
        self.FLine = node.Line
        self.FCol = node.Col
        self.FFileName = node.FileName

    def _normalize_attr_key(self, key: TAttributeName | str) -> str:
        if isinstance(key, TAttributeName):
            return ATTRIBUTE_NAME_STRINGS[int(key)]
        return str(key)

    def GetAttribute(self, key: TAttributeName | str) -> str:
        return self._attributes.get(self._normalize_attr_key(key), "")

    def HasAttribute(self, key: TAttributeName | str) -> bool:
        return self._normalize_attr_key(key) in self._attributes

    def SetAttribute(self, key: TAttributeName | str, value: str) -> None:
        self._attributes[self._normalize_attr_key(key)] = value

    def ClearAttributes(self) -> None:
        self._attributes.clear()

    def AddChild(self, node_or_type: "TSyntaxNode | TSyntaxNodeType") -> "TSyntaxNode":
        if isinstance(node_or_type, TSyntaxNodeType):
            node = TSyntaxNode(node_or_type)
        else:
            node = node_or_type
        node.FParentNode = self
        self._child_nodes.append(node)
        return node

    def DeleteChild(self, node: "TSyntaxNode") -> None:
        self._child_nodes.remove(node)

    def ExtractChild(self, node: "TSyntaxNode") -> None:
        self.DeleteChild(node)
        node.FParentNode = None

    def FindNode(self, typ_or_path: TSyntaxNodeType | Iterable[TSyntaxNodeType]) -> "TSyntaxNode | None":
        if isinstance(typ_or_path, TSyntaxNodeType):
            for child in self._child_nodes:
                if child.Typ == typ_or_path:
                    return child
            return None

        path = list(typ_or_path)
        if not path:
            return None

        def _find(node: TSyntaxNode, offset: int) -> TSyntaxNode | None:
            if offset >= len(path):
                return node
            expected = path[offset]
            for child in node.ChildNodes:
                if expected != TSyntaxNodeType.ntUnknown and child.Typ != expected:
                    continue
                found = _find(child, offset + 1)
                if found is not None:
                    return found
            return None

        return _find(self, 0)

    @property
    def Attributes(self) -> list[tuple[TAttributeName | str, str]]:
        values: list[tuple[TAttributeName | str, str]] = []
        for key, value in self._attributes.items():
            values.append((ATTRIBUTE_NAME_BY_STRING.get(key, key), value))
        return values

    @property
    def ChildNodes(self) -> list["TSyntaxNode"]:
        return self._child_nodes

    @property
    def HasAttributes(self) -> bool:
        return bool(self._attributes)

    @property
    def HasChildren(self) -> bool:
        return bool(self._child_nodes)

    @property
    def Typ(self) -> TSyntaxNodeType:
        return self.FTyp

    @property
    def ParentNode(self) -> "TSyntaxNode | None":
        return self.FParentNode

    @property
    def LineSeq(self) -> int:
        return self.FLineSeq

    @LineSeq.setter
    def LineSeq(self, value: int) -> None:
        self.FLineSeq = value

    @property
    def Col(self) -> int:
        return self.FCol

    @Col.setter
    def Col(self, value: int) -> None:
        self.FCol = value

    @property
    def Line(self) -> int:
        return self.FLine

    @Line.setter
    def Line(self, value: int) -> None:
        self.FLine = value

    @property
    def FileName(self) -> str:
        return self.FFileName

    @FileName.setter
    def FileName(self, value: str) -> None:
        self.FFileName = value


class TCompoundSyntaxNode(TSyntaxNode):
    def __init__(self, typ: TSyntaxNodeType):
        super().__init__(typ)
        self.FEndCol = 0
        self.FEndLine = 0

    def Clone(self) -> TSyntaxNode:
        clone = super().Clone()
        assert isinstance(clone, TCompoundSyntaxNode)
        clone.EndCol = self.EndCol
        clone.EndLine = self.EndLine
        return clone

    @property
    def EndCol(self) -> int:
        return self.FEndCol

    @EndCol.setter
    def EndCol(self, value: int) -> None:
        self.FEndCol = value

    @property
    def EndLine(self) -> int:
        return self.FEndLine

    @EndLine.setter
    def EndLine(self, value: int) -> None:
        self.FEndLine = value


class TValuedSyntaxNode(TSyntaxNode):
    def __init__(self, typ: TSyntaxNodeType):
        super().__init__(typ)
        self.FValue = ""

    def Clone(self) -> TSyntaxNode:
        clone = super().Clone()
        assert isinstance(clone, TValuedSyntaxNode)
        clone.Value = self.Value
        return clone

    @property
    def Value(self) -> str:
        return self.FValue

    @Value.setter
    def Value(self, value: str) -> None:
        self.FValue = value


class TCommentNode(TSyntaxNode):
    def __init__(self, typ: TSyntaxNodeType):
        super().__init__(typ)
        self.FText = ""

    def Clone(self) -> TSyntaxNode:
        clone = super().Clone()
        assert isinstance(clone, TCommentNode)
        clone.Text = self.Text
        return clone

    @property
    def Text(self) -> str:
        return self.FText

    @Text.setter
    def Text(self, value: str) -> None:
        self.FText = value


@dataclass
class TUnitInfo:
    Name: str
    Path: str
    SyntaxTree: TSyntaxNode
    HasError: bool = False
    ErrorInfo: dict[str, int | str] | None = None


@dataclass
class TIncludeFileInfo:
    Name: str
    Path: str


@dataclass
class TProblemInfo:
    ProblemType: int
    FileName: str
    Description: str


def node_type_name(node_type: TSyntaxNodeType) -> str:
    return SYNTAX_NODE_NAMES[int(node_type)]
