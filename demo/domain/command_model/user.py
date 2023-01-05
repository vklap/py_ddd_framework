from __future__ import annotations

import ddd
from demo.domain.command_model.email_set_event import EmailSetEvent


class User(ddd.AbstractEntity):
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
        if value and self._email != value:
            self.add_event(EmailSetEvent(user_id=self._id, new_email=value, old_email=self._email))
        self._email = value

    def __repr__(self) -> str:
        return f'<{type(self).__name__}(id={self._id}, email={self._email})>'
