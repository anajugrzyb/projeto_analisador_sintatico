from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from lexical.token import Token


@dataclass
class SyntaxNode:
    """Represents a node in the syntax tree produced by the parser."""

    label: str
    children: List["SyntaxNode"] = field(default_factory=list)
    token: Optional[Token] = None

    def add_child(self, child: Optional["SyntaxNode"]) -> None:
        """Append a child node if it is not ``None``."""

        if child is not None:
            self.children.append(child)


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\"", "\\\"")


def syntax_tree_to_dot(root: SyntaxNode) -> str:
    """Create a Graphviz DOT representation of the syntax tree."""

    lines: List[str] = ["digraph SyntaxTree {", "    node [shape=box];"]
    counter = 0

    def visit(node: SyntaxNode) -> str:
        nonlocal counter
        node_id = f"n{counter}"
        counter += 1
        label_parts = [node.label]
        if node.token is not None and node.token.value is not None:
            label_parts.append(str(node.token.value))
        label = "\\n".join(label_parts)
        lines.append(f'    {node_id} [label="{_escape(label)}"];')
        for child in node.children:
            child_id = visit(child)
            lines.append(f"    {node_id} -> {child_id};")
        return node_id

    visit(root)
    lines.append("}")
    return "\n".join(lines)


def export_syntax_tree(root: SyntaxNode, filepath: str) -> None:
    """Persist the DOT representation of *root* into *filepath*."""

    dot_source = syntax_tree_to_dot(root)
    with open(filepath, "w", encoding="utf-8") as dot_file:
        dot_file.write(dot_source)
