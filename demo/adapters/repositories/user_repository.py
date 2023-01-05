from __future__ import annotations

import abc

from demo.domain.model import User
from src.ddd import error
from src.ddd.repository import RollbackCommitter, AsyncRollbackCommitter


class AbstractUserRepository(RollbackCommitter, abc.ABC):
    def get_by_id(self, id_: str) -> User:
        return self._get_by_id(id_)

    def save(self, user: User) -> None:
        self._save(user)

    @abc.abstractmethod
    def _get_by_id(self, id_: str) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def _save(self, user: User) -> None:
        raise NotImplementedError


class AbstractAsyncUserRepository(AsyncRollbackCommitter, abc.ABC):
    async def get_by_id(self, id_: str) -> User:
        return await self._get_by_id(id_)

    async def save(self, user: User) -> None:
        await self._save(user)

    @abc.abstractmethod
    async def _get_by_id(self, id_: str) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    async def _save(self, user: User) -> None:
        raise NotImplementedError


class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        super().__init__()
        self.users_by_id: dict[str, User] = {}
        self._saved_users: list[User] = []
        self.commit_called = False
        self.rollback_called = False
        self.commit_should_raise = False
        self.rollback_should_raise = False

    def _get_by_id(self, id_: str) -> User:
        result = self.users_by_id.get(id_)
        if not result:
            raise error.BoundedContextError(error.NOT_FOUND, f'User with ID "{id_}" does not exist')
        return result

    def _save(self, user: User) -> None:
        self._saved_users.append(user)

    def commit(self) -> None:
        self.commit_called = True
        if self.commit_should_raise:
            raise Exception('commit failed')
        for user in self._saved_users:
            self.users_by_id[user.get_id()] = user

    def rollback(self) -> None:
        self.rollback_called = True
        if self.rollback_should_raise:
            raise Exception('rollback failed')
        self._saved_users.clear()


class AsyncInMemoryUserRepository(AbstractAsyncUserRepository):
    def __init__(self):
        super().__init__()
        self.users_by_id: dict[str, User] = {}
        self._saved_users: list[User] = []
        self.commit_called = False
        self.rollback_called = False
        self.commit_should_raise = False
        self.rollback_should_raise = False

    async def _get_by_id(self, id_: str) -> User:
        result = self.users_by_id.get(id_)
        if not result:
            raise error.BoundedContextError(error.NOT_FOUND, f'User with ID "{id_}" does not exist')
        return result

    async def _save(self, user: User) -> None:
        self._saved_users.append(user)

    async def commit(self) -> None:
        self.commit_called = True
        if self.commit_should_raise:
            raise Exception('commit failed')
        for user in self._saved_users:
            self.users_by_id[user.get_id()] = user

    async def rollback(self) -> None:
        self.rollback_called = True
        if self.rollback_should_raise:
            raise Exception('rollback failed')
        self._saved_users.clear()
