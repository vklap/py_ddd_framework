from __future__ import annotations

import abc
from typing import TypeVar, Generic, Callable

from ddd.model import AbstractCommand, AbstractEvent
from ddd.repository import RollbackCommitter, AsyncRollbackCommitter

THandleCommandResult = TypeVar('THandleCommandResult')
TCommand = TypeVar('TCommand', bound=AbstractCommand)
TEvent = TypeVar('TEvent', bound=AbstractEvent)


class _EventsReporter(abc.ABC):
    @property
    @abc.abstractmethod
    def events(self) -> list[AbstractEvent]:
        raise NotImplementedError


class AbstractCommandHandler(Generic[TCommand, THandleCommandResult], _EventsReporter, RollbackCommitter, abc.ABC):
    def handle(self, command: TCommand) -> THandleCommandResult:
        raise NotImplementedError


class AbstractAsyncCommandHandler(
    Generic[TCommand, THandleCommandResult], _EventsReporter, AsyncRollbackCommitter, abc.ABC
):
    async def handle(self, command: TCommand) -> THandleCommandResult:
        raise NotImplementedError


class AbstractEventHandler(Generic[TEvent], _EventsReporter, RollbackCommitter, abc.ABC):
    def handle(self, event: TEvent) -> None:
        raise NotImplementedError


class AbstractAsyncEventHandler(Generic[TEvent], _EventsReporter, RollbackCommitter, abc.ABC):
    async def handle(self, event: TEvent) -> None:
        raise NotImplementedError


CreateCommandHandler = Callable[[], AbstractCommandHandler]
CreateAsyncCommandHandler = Callable[[], AbstractAsyncCommandHandler]
CreateEventHandler = Callable[[], AbstractEventHandler]
CreateAsyncEventHandler = Callable[[], AbstractAsyncEventHandler]
