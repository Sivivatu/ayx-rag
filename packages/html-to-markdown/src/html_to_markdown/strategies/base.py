from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Strategy(Protocol):
    name: str

    def available(self) -> bool:  # whether dependencies present
        ...

    def version(self) -> str:
        ...

    def convert(self, html: str) -> str:  # returns Markdown
        ...

    def supports_tables(self) -> bool:
        ...

    def supports_code_lang(self) -> bool:
        ...


@dataclass
class StrategyInfo:
    name: str
    version: str
    supports_tables: bool
    supports_code_lang: bool
    available: bool
