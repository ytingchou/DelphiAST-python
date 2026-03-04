from __future__ import annotations

from enum import IntEnum
from typing import Protocol


class TMessageEventType(IntEnum):
    meError = 0
    meNotSupported = 1


class IIncludeHandler(Protocol):
    def GetIncludeFileContent(
        self,
        ParentFileName: str,
        IncludeName: str,
    ) -> tuple[bool, str, str]:
        ...
