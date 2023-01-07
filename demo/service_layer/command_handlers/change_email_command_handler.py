from __future__ import annotations

from demo.adapters.clients.pubsub_client import AbstractPubSubClient
from demo.adapters.repositories.user_repository import AbstractUserRepository, AbstractAsyncUserRepository
from demo.domain.model import ChangeEmailCommand
from ddd import async_utils
from ddd.handlers import AbstractCommandHandler, TCommand, THandleCommandResult, AbstractAsyncCommandHandler
from ddd.model import AbstractEvent


class ChangeEmailCommandHandler(AbstractCommandHandler[ChangeEmailCommand, str]):
    def __init__(self, user_repository: AbstractUserRepository):
        super().__init__()
        self._user_repository = user_repository
        self._events: list[AbstractEvent] = []

    def handle(self, command: TCommand) -> THandleCommandResult:
        user = self._user_repository.get_by_id(command.user_id)
        user.set_email(command.new_email)
        self._events.extend(user.events)
        return user.get_id()

    @property
    def events(self) -> list[AbstractEvent]:
        return list(self._events)

    def commit(self) -> None:
        self._user_repository.commit()

    def rollback(self) -> None:
        self._user_repository.rollback()


class AsyncChangeEmailCommandHandler(AbstractAsyncCommandHandler[ChangeEmailCommand, str]):
    def __init__(self, user_repository: AbstractAsyncUserRepository):
        super().__init__()
        self._user_repository = user_repository
        self._events: list[AbstractEvent] = []

    async def handle(self, command: TCommand) -> THandleCommandResult:
        user = await self._user_repository.get_by_id(command.user_id)
        user.set_email(command.new_email)
        self._events.extend(user.events)
        return user.get_id()

    @property
    def events(self) -> list[AbstractEvent]:
        return list(self._events)

    async def commit(self) -> None:
        await self._user_repository.commit()

    async def rollback(self) -> None:
        await self._user_repository.rollback()
