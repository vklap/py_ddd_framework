from __future__ import annotations

from typing import Deque, Any
import collections

from src.ddd.model import AbstractEvent, AbstractCommand
from src.ddd.factories import CommandHandlerFactory, EventHandlersFactory, AsyncCommandHandlerFactory, \
    AsyncEventHandlersFactory
from src.ddd.unit_of_work import CommandUnitOfWork, EventUnitOfWork, AsyncCommandUnitOfWork, AsyncEventUnitOfWork


class MessageBus:
    def __init__(self, command_handler_factory: CommandHandlerFactory, event_handlers_factory: EventHandlersFactory):
        self._command_handler_factory = command_handler_factory
        self._event_handlers_factory = event_handlers_factory
        self._events: Deque[AbstractEvent] = collections.deque()

    def publish(self, command: AbstractCommand) -> Any:
        command.validate()
        handler = self._command_handler_factory.create_handler(command.name)
        with CommandUnitOfWork(handler) as uow:
            result = uow.handle(command)
            self._events.extend(handler.events)
        self._handle_events()
        return result

    def _handle_events(self) -> None:
        while self._events:
            event = self._events.popleft()
            handlers = self._event_handlers_factory.create_handlers(event.name)
            for handler in handlers:
                with EventUnitOfWork(handler) as uow:
                    uow.handle(event)
                    self._events.extend(handler.events)


class AsyncMessageBus:
    def __init__(
            self, command_handler_factory: AsyncCommandHandlerFactory, event_handlers_factory: AsyncEventHandlersFactory
    ):
        self._command_handler_factory = command_handler_factory
        self._event_handlers_factory = event_handlers_factory
        self._events: Deque[AbstractEvent] = collections.deque()

    async def publish(self, command: AbstractCommand) -> Any:
        command.validate()
        handler = self._command_handler_factory.create_handler(command.name)
        async with AsyncCommandUnitOfWork(handler) as uow:
            result = await uow.handle(command)
            self._events.extend(handler.events)
        await self._handle_events()
        return result

    async def _handle_events(self) -> None:
        while self._events:
            event = self._events.popleft()
            handlers = self._event_handlers_factory.create_handlers(event.name)
            for handler in handlers:
                async with AsyncEventUnitOfWork(handler) as uow:
                    await uow.handle(event)
                    self._events.extend(handler.events)
