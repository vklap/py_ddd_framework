from __future__ import annotations

import abc

from ddd import async_utils
from ddd.repository import RollbackCommitter, AsyncRollbackCommitter


class AbstractPubSubClient(RollbackCommitter, abc.ABC):
    def notify_email_changed(self, user_id: str, new_email: str, old_email: str) -> None:
        self._notify_email_changed(user_id, new_email, old_email)

    def notify_slack(self, message: str) -> None:
        self._notify_slack(message)

    @abc.abstractmethod
    def _notify_slack(self, message: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def _notify_email_changed(self, user_id: str, new_email: str, old_email: str) -> None:
        raise NotImplementedError


class AbstractAsyncPubSubClient(AsyncRollbackCommitter, abc.ABC):
    async def notify_email_changed(self, user_id: str, new_email: str, old_email: str) -> None:
        await self._notify_email_changed(user_id, new_email, old_email)

    async def notify_slack(self, message: str) -> None:
        await self._notify_slack(message)

    @abc.abstractmethod
    async def _notify_slack(self, message: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def _notify_email_changed(self, user_id: str, new_email: str, old_email: str) -> None:
        raise NotImplementedError


class InMemoryPubSubClient(AbstractPubSubClient):
    def __init__(self):
        super().__init__()
        self.commit_called = False
        self.commit_should_raise = False
        self.new_email: str | None = None
        self.notify_should_raise = False
        self.old_email: str | None = None
        self.rollback_called = False
        self.rollback_should_raise = False
        self.sent_slack_message = False
        self.sent_email = False
        self.user_id: str | None = None

    def _notify_slack(self, message: str) -> None:
        self.sent_slack_message = True

    def _notify_email_changed(self, user_id: str, new_email: str, old_email: str) -> None:
        if self.notify_should_raise:
            raise Exception('notify failed')
        self.user_id = user_id
        self.new_email = new_email
        self.old_email = old_email
        self.sent_email = True

    def commit(self) -> None:
        self.commit_called = True
        if self.commit_should_raise:
            raise Exception('commit failed')

    def rollback(self) -> None:
        self.rollback_called = True
        if self.rollback_should_raise:
            raise Exception('rollback failed')


class AsyncInMemoryPubSubClient(AbstractAsyncPubSubClient):

    def __init__(self):
        super().__init__()
        self.commit_called = False
        self.commit_should_raise = False
        self.new_email: str | None = None
        self.notify_should_raise = False
        self.old_email: str | None = None
        self.rollback_called = False
        self.rollback_should_raise = False
        self.sent_slack_message = False
        self.sent_email = False
        self.user_id: str | None = None

    async def _notify_slack(self, message: str) -> None:
        self.sent_slack_message = True

    async def _notify_email_changed(self, user_id: str, new_email: str, old_email: str) -> None:
        if self.notify_should_raise:
            raise Exception('notify failed')
        self.user_id = user_id
        self.new_email = new_email
        self.old_email = old_email
        self.sent_email = True

    async def commit(self) -> None:
        self.commit_called = True
        if self.commit_should_raise:
            raise Exception('commit failed')

    async def rollback(self) -> None:
        self.rollback_called = True
        if self.rollback_should_raise:
            raise Exception('rollback failed')
