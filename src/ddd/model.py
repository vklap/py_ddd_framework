from __future__ import annotations

import abc


class AbstractCommand(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def validate(self) -> None:
        raise NotImplementedError


class AbstractEvent(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError


class AbstractEntity(abc.ABC):
    def __init__(self):
        self._events: list[AbstractEvent] = []

    @abc.abstractmethod
    def get_id(self) -> str:
        raise NotImplementedError

    def set_id(self, value: str) -> str:
        raise NotImplementedError

    def add_event(self, event: AbstractEvent) -> None:
        self._events.append(event)

    @property
    def events(self) -> list[AbstractEvent]:
        return list(self._events)
