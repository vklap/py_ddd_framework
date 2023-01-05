from __future__ import annotations

import dataclasses

import ddd


@dataclasses.dataclass
class EmailSetEvent(ddd.AbstractEvent):
    user_id: str | None = None
    new_email: str | None = None
    old_email: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__

