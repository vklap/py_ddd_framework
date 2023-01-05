from __future__ import annotations

import dataclasses

from src.ddd import error
from src.ddd.error import BoundedContextError
from src.ddd.model import AbstractEntity, AbstractCommand, AbstractEvent


@dataclasses.dataclass
class ChangeEmailCommand(AbstractCommand):
    user_id: str | None = None
    new_email: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__

    def validate(self) -> None:
        if not self.user_id:
            raise BoundedContextError(error.BAD_REQUEST, 'Missing user_id')
        if not self.new_email:
            raise BoundedContextError(error.BAD_REQUEST, 'Missing new_email')


@dataclasses.dataclass
class EmailChangedEvent(AbstractEvent):
    user_id: str | None = None
    new_email: str | None = None
    old_email: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__


@dataclasses.dataclass
class NotifySlackEvent(AbstractEvent):
    message: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__


class User(AbstractEntity):
    def __init__(self, email: str | None = None, id_: str | None = None):
        super().__init__()
        self._id = id_
        self._email = email

    def get_id(self) -> str:
        return self._id

    def set_id(self, value: str) -> None:
        self._id = value

    @property
    def email(self) -> str:
        return self._email

    def set_email(self, value: str) -> None:
        if self._email and self._email != value:
            self.add_event(EmailChangedEvent(user_id=self._id, new_email=value, old_email=self._email))
        self._email = value

    def __repr__(self) -> str:
        return f'<{type(self).__name__}(id={self._id}, email={self._email})>'
