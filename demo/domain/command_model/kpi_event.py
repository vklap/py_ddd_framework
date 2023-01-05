from __future__ import annotations

import dataclasses

import ddd


@dataclasses.dataclass
class KpiEvent(ddd.AbstractEvent):
    action: str | None = None
    data: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__
