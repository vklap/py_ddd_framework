from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, Type

from src.ddd.factories import CommandHandlerFactory, EventHandlersFactory, CreateCommandHandler, CreateEventHandler, \
    AsyncCommandHandlerFactory, AsyncEventHandlersFactory
from src.ddd.handlers import CreateAsyncCommandHandler, CreateAsyncEventHandler, AbstractCommandHandler, \
    AbstractEventHandler, AbstractAsyncCommandHandler, AbstractAsyncEventHandler
from src.ddd.message_bus import MessageBus, AsyncMessageBus
from src.ddd.model import AbstractCommand


class Bootstrapper:
    def __init__(self):
        self._command_handler_factory = CommandHandlerFactory()
        self._async_command_handler_factory = AsyncCommandHandlerFactory()
        self._event_handlers_factory = EventHandlersFactory()
        self._async_event_handlers_factory = AsyncEventHandlersFactory()

    def register_command_handler_factory(self, command_name: str, factory: CreateCommandHandler) -> None:
        self._validate_type_returned_by(factory, AbstractCommandHandler)
        self._command_handler_factory.register(command_name, factory)

    def register_event_handler_factory(self, event_name: str, factory: CreateEventHandler) -> None:
        self._validate_type_returned_by(factory, AbstractEventHandler)
        self._event_handlers_factory.register(event_name, factory)

    def register_async_command_handler_factory(self, command_name: str, factory: CreateAsyncCommandHandler) -> None:
        self._validate_type_returned_by(factory, AbstractAsyncCommandHandler)
        self._async_command_handler_factory.register(command_name, factory)

    def register_async_event_handler_factory(self, event_name: str, factory: CreateAsyncEventHandler) -> None:
        self._validate_type_returned_by(factory, AbstractAsyncEventHandler)
        self._async_event_handlers_factory.register(event_name, factory)

    def handle_command(self, command: AbstractCommand) -> Any:
        message_bus = MessageBus(self._command_handler_factory, self._event_handlers_factory)
        result = message_bus.publish(command)
        return result

    async def async_handle_command(self, command: AbstractCommand) -> Any:
        message_bus = AsyncMessageBus(self._async_command_handler_factory, self._async_event_handlers_factory)
        result = await message_bus.publish(command)
        return result

    @classmethod
    def _validate_type_returned_by(cls, func: Callable, type_: Type) -> None:
        signature = inspect.signature(func)
        if signature.return_annotation is inspect.Signature.empty:
            return
        if signature.return_annotation != type_.__name__:
            raise ValueError(f'register expected "{type_.__name__}", got "{signature.return_annotation}"')

