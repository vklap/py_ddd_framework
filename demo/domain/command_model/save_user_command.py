from __future__ import annotations

import dataclasses

import ddd


@dataclasses.dataclass
class SaveUserCommand(ddd.AbstractCommand):
    user_id: str | None = None
    email: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__

    def validate(self) -> None:
        if not self.user_id:
            raise ddd.BoundedContextError(ddd.BAD_REQUEST, 'Missing user_id')
        if not self.email:
            raise ddd.BoundedContextError(ddd.BAD_REQUEST, 'Missing email')
