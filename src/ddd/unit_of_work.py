from __future__ import annotations
import abc

from typing import Any, Generic, Type, TypeVar, Union
from types import TracebackType
from src.ddd.model import AbstractCommand, AbstractEvent
from src.ddd.handlers import (
    AbstractCommandHandler,
    AbstractEventHandler,
    AbstractAsyncCommandHandler,
    AbstractAsyncEventHandler,
)

Message = Union[AbstractCommand, AbstractEvent]
TMessage = TypeVar('TMessage', bound=Message)
Handler = Union[AbstractCommandHandler, AbstractEventHandler]
THandler = TypeVar('THandler', bound=Handler)
AsyncHandler = Union[AbstractAsyncCommandHandler, AbstractAsyncEventHandler]
TAsyncHandler = TypeVar('TAsyncHandler', bound=AsyncHandler)


class AbstractUnitOfWork(Generic[TMessage, THandler], abc.ABC):
    def __init__(self, handler: THandler):
        self._handler = handler

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, exc_type: Type, exc_val: Exception, exc_tb: TracebackType) -> bool | None:
        if exc_val:
            self._handler.rollback()
        else:
            self._handler.commit()

    def handle(self, message: TMessage) -> Any:
        result = self._handler.handle(message)
        return result


class AbstractAsyncUnitOfWork(Generic[TMessage, TAsyncHandler], abc.ABC):
    def __init__(self, handler: TAsyncHandler):
        self._handler = handler

    async def __aenter__(self) -> AbstractAsyncUnitOfWork:
        return self

    async def __aexit__(self, exc_type: Type, exc_val: Exception, exc_tb: TracebackType) -> bool | None:
        if exc_val:
            await self._handler.rollback()
        else:
            await self._handler.commit()

    async def handle(self, message: TMessage) -> Any:
        result = await self._handler.handle(message)
        return result


class CommandUnitOfWork(AbstractUnitOfWork[AbstractCommand, AbstractCommandHandler]):
    """CommandUnitOfWork"""


class AsyncCommandUnitOfWork(AbstractAsyncUnitOfWork[AbstractCommand, AbstractAsyncCommandHandler]):
    """CommandUnitOfWork"""


class EventUnitOfWork(AbstractUnitOfWork[AbstractEvent, AbstractEventHandler]):
    """EventUnitOfWork"""


class AsyncEventUnitOfWork(AbstractAsyncUnitOfWork[AbstractEvent, AbstractAsyncEventHandler]):
    """AsyncEventUnitOfWork"""
