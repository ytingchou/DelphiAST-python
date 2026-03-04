from __future__ import annotations

from .classes import TCompoundSyntaxNode, TSyntaxNode, TValuedSyntaxNode
from .consts import ATTRIBUTE_NAME_STRINGS, TAttributeName, syntax_node_name


def _xml_encode(data: str) -> str:
    return (
        data.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


class TSyntaxTreeWriter:
    @classmethod
    def _node_to_xml(cls, node: TSyntaxNode, formatted: bool, indent: str, out: list[str]) -> None:
        has_children = node.HasChildren
        new_indent = indent + "  "
        if formatted:
            out.append(indent)

        out.append("<" + syntax_node_name(node.Typ).upper())
        out.append(f'  line_seq="{node.LineSeq}"')

        if isinstance(node, TCompoundSyntaxNode):
            out.append(f' begin_line="{node.Line}"')
            out.append(f' begin_col="{node.Col}"')
            out.append(f' end_line="{node.EndLine}"')
            out.append(f' end_col="{node.EndCol}"')
        else:
            out.append(f' line="{node.Line}"')
            out.append(f' col="{node.Col}"')

        if node.FileName:
            out.append(f'  file="{_xml_encode(node.FileName)}"')

        if isinstance(node, TValuedSyntaxNode):
            out.append(f' value="{_xml_encode(node.Value)}"')

        for attr_key, attr_value in node.Attributes:
            if isinstance(attr_key, TAttributeName):
                key_str = ATTRIBUTE_NAME_STRINGS[int(attr_key)]
            else:
                key_str = str(attr_key)
            out.append(f' {key_str}="{_xml_encode(attr_value)}"')

        if has_children:
            out.append(">")
        else:
            out.append("/>")

        if formatted:
            out.append("\n")

        for child in node.ChildNodes:
            cls._node_to_xml(child, formatted, new_indent, out)

        if has_children:
            if formatted:
                out.append(indent)
            out.append("</" + syntax_node_name(node.Typ).upper() + ">")
            if formatted:
                out.append("\n")

    @classmethod
    def ToXML(cls, root: TSyntaxNode, Formatted: bool = False) -> str:
        parts: list[str] = []
        cls._node_to_xml(root, Formatted, "", parts)
        return "<?xml version=\"1.0\"?>\n" + "".join(parts)

    @classmethod
    def to_xml(cls, root: TSyntaxNode, formatted: bool = False) -> str:
        return cls.ToXML(root, formatted)
