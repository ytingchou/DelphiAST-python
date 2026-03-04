from __future__ import annotations

from pathlib import Path
import tempfile

from delphiast.ast_builder import TPasSyntaxTreeBuilder
from delphiast.classes import TSyntaxNode


class TmwSimplePasPar:
    """Compatibility wrapper around TPasSyntaxTreeBuilder."""

    def __init__(self) -> None:
        self.InterfaceOnly = False

    def Run(self, UnitName: str, SourceStream) -> TSyntaxNode:
        _ = UnitName
        payload = SourceStream.read()
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="replace")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pas", encoding="utf-8", delete=False) as handle:
            handle.write(str(payload))
            temp_name = handle.name
        try:
            return TPasSyntaxTreeBuilder.RunFile(temp_name, InterfaceOnly=self.InterfaceOnly)
        finally:
            Path(temp_name).unlink(missing_ok=True)
