from __future__ import annotations

import abc
import collections
import threading
from typing import Callable, Generic, TypeVar, Union

from src.ddd.handlers import AbstractCommandHandler, AbstractEventHandler, CreateCommandHandler, CreateEventHandler, \
    AbstractAsyncCommandHandler, CreateAsyncCommandHandler, CreateAsyncEventHandler, AbstractAsyncEventHandler

TCreateCommandHandler = TypeVar('TCreateCommandHandler', bound=Union[CreateCommandHandler, CreateAsyncCommandHandler])
TAbstractCommandHandler = TypeVar(
    'TAbstractCommandHandler', bound=Union[AbstractCommandHandler, AbstractAsyncCommandHandler]
)
TCreateEventHandler = TypeVar('TCreateEventHandler', bound=Union[CreateEventHandler, CreateAsyncEventHandler])
TAbstractEventHandler = TypeVar(
    'TAbstractEventHandler', bound=Union[AbstractEventHandler, AbstractAsyncEventHandler]
)


class _AbstractCommandHandlerFactory(Generic[TCreateCommandHandler, TAbstractCommandHandler], abc.ABC):
    def __init__(self):
        self._handler_factories: dict[str, TCreateCommandHandler] = {}

    def register(self, command_name: str, factory: TCreateCommandHandler) -> None:
        self._handler_factories[command_name] = factory

    def create_handler(self, command_name: str) -> TAbstractCommandHandler:
        factory = self._handler_factories.get(command_name)
        if not factory:
            raise ValueError(f'Handler factory was not registered for command: "{command_name}"')
        return factory()


class CommandHandlerFactory(_AbstractCommandHandlerFactory[CreateCommandHandler, AbstractCommandHandler]):
    """CommandHandlerFactory"""


class AsyncCommandHandlerFactory(
    _AbstractCommandHandlerFactory[CreateAsyncCommandHandler, AbstractAsyncCommandHandler]
):
    """AsyncCommandHandlerFactory"""


class _AbstractEventHandlersFactory(Generic[TCreateEventHandler, TAbstractEventHandler], abc.ABC):
    def __init__(self):
        self._handler_factories: dict[str, [TCreateEventHandler]] = collections.defaultdict(list)

    def register(self, event_name: str, factory: TCreateEventHandler) -> None:
        self._handler_factories[event_name].append(factory)

    def create_handlers(self, event_name: str) -> list[TAbstractEventHandler]:
        factories = self._handler_factories[event_name]
        result = []
        for factory in factories:
            handler = factory()
            result.append(handler)
        return result


class EventHandlersFactory(_AbstractEventHandlersFactory[CreateEventHandler, AbstractEventHandler]):
    """EventHandlersFactory"""


class AsyncEventHandlersFactory(_AbstractEventHandlersFactory[CreateAsyncEventHandler, AbstractAsyncEventHandler]):
    """AsyncEventHandlersFactory"""
