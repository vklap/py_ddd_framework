from __future__ import annotations

import ddd
from demo.adapters.repositories.user_repository import AbstractUserRepository, AbstractAsyncUserRepository
from demo.domain.command_model.save_user_command import SaveUserCommand


class SaveUserCommandHandler(ddd.AbstractCommandHandler[SaveUserCommand, str]):
    def __init__(self, user_repository: AbstractUserRepository):
        super().__init__()
        self._user_repository = user_repository
        self._events: list[ddd.AbstractEvent] = []

    def handle(self, command: ddd.TCommand) -> ddd.THandleCommandResult:
        user = self._user_repository.get_by_id(command.user_id)
        user.set_email(command.email)
        self._events.extend(user.events)
        return user.get_id()

    @property
    def events(self) -> list[ddd.AbstractEvent]:
        return list(self._events)

    def commit(self) -> None:
        self._user_repository.commit()

    def rollback(self) -> None:
        self._user_repository.rollback()


class AsyncChangeEmailCommandHandler(ddd.AbstractAsyncCommandHandler[SaveUserCommand, str]):
    def __init__(self, user_repository: AbstractAsyncUserRepository):
        super().__init__()
        self._user_repository = user_repository
        self._events: list[ddd.AbstractEvent] = []

    async def handle(self, command: ddd.TCommand) -> ddd.THandleCommandResult:
        user = await self._user_repository.get_by_id(command.user_id)
        user.set_email(command.email)
        self._events.extend(user.events)
        return user.get_id()

    @property
    def events(self) -> list[ddd.AbstractEvent]:
        return list(self._events)

    async def commit(self) -> None:
        await self._user_repository.commit()

    async def rollback(self) -> None:
        await self._user_repository.rollback()
