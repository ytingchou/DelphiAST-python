from __future__ import annotations

from xml.etree import ElementTree as ET

from .classes import TCommentNode, TCompoundSyntaxNode, TSyntaxNode, TValuedSyntaxNode
from .consts import SYNTAX_NODE_TYPE_BY_NAME, TSyntaxNodeType


def _create_node_from_element(element: ET.Element) -> TSyntaxNode:
    node_name = element.tag.lower()
    if node_name not in SYNTAX_NODE_TYPE_BY_NAME:
        raise ValueError(f"Unknown syntax node '{element.tag}'")

    node_type = SYNTAX_NODE_TYPE_BY_NAME[node_name]
    if "begin_line" in element.attrib:
        node = TCompoundSyntaxNode(node_type)
        node.Line = int(element.attrib.get("begin_line", "0"))
        node.Col = int(element.attrib.get("begin_col", "0"))
        node.EndLine = int(element.attrib.get("end_line", "0"))
        node.EndCol = int(element.attrib.get("end_col", "0"))
    elif "value" in element.attrib:
        node = TValuedSyntaxNode(node_type)
        node.Line = int(element.attrib.get("line", "0"))
        node.Col = int(element.attrib.get("col", "0"))
        node.Value = element.attrib.get("value", "")
    else:
        node = TSyntaxNode(node_type)
        node.Line = int(element.attrib.get("line", "0"))
        node.Col = int(element.attrib.get("col", "0"))

    if node_type in (
        TSyntaxNodeType.ntAnsiComment,
        TSyntaxNodeType.ntBorComment,
        TSyntaxNodeType.ntSlashesComment,
    ):
        comment = TCommentNode(node_type)
        comment.Line = node.Line
        comment.Col = node.Col
        comment.LineSeq = int(element.attrib.get("line_seq", "0"))
        comment.FileName = element.attrib.get("file", "")
        comment.Text = element.attrib.get("value", "")
        return comment

    node.LineSeq = int(element.attrib.get("line_seq", "0"))
    node.FileName = element.attrib.get("file", "")

    skip_keys = {
        "line_seq",
        "line",
        "col",
        "begin_line",
        "begin_col",
        "end_line",
        "end_col",
        "file",
        "value",
    }
    for key, value in element.attrib.items():
        if key in skip_keys:
            continue
        node.SetAttribute(key, value)

    for child_element in element:
        node.AddChild(_create_node_from_element(child_element))
    return node


def parse_xml_to_syntax_tree(xml_text: str) -> TSyntaxNode:
    root_element = ET.fromstring(xml_text)
    return _create_node_from_element(root_element)
