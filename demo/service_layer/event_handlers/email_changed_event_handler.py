from __future__ import annotations

from demo.adapters.clients.pubsub_client import AbstractPubSubClient, AbstractAsyncPubSubClient
from demo.adapters.repositories.user_repository import AbstractUserRepository
from demo.domain.model import ChangeEmailCommand, EmailChangedEvent, NotifySlackEvent
from src.ddd import async_utils
from src.ddd.handlers import AbstractCommandHandler, TEvent, THandleCommandResult, AbstractEventHandler, \
    AbstractAsyncEventHandler
from src.ddd.model import AbstractEvent


class EmailChangedEventHandler(AbstractEventHandler[EmailChangedEvent]):
    def __init__(self, email_client: AbstractPubSubClient):
        super().__init__()
        self._email_client = email_client
        self._events: list[AbstractEvent] = []

    def handle(self, event: TEvent) -> None:
        self._email_client.notify_email_changed(event.user_id, event.new_email, event.old_email)
        self._events.append(
            NotifySlackEvent(message=f'requested to notify user_id "{event.user_id}" about email modification')
        )

    @property
    def events(self) -> list[AbstractEvent]:
        return list(self._events)

    def commit(self) -> None:
        self._email_client.commit()

    def rollback(self) -> None:
        self._email_client.rollback()


class AsyncEmailChangedEventHandler(AbstractAsyncEventHandler[EmailChangedEvent]):
    def __init__(self, email_client: AbstractAsyncPubSubClient):
        super().__init__()
        self._email_client = email_client
        self._events: list[AbstractEvent] = []

    async def handle(self, event: TEvent) -> None:
        await self._email_client.notify_email_changed(event.user_id, event.new_email, event.old_email)
        self._events.append(
            NotifySlackEvent(message=f'requested to notify user_id "{event.user_id}" about email modification')
        )

    @property
    def events(self) -> list[AbstractEvent]:
        return list(self._events)

    async def commit(self) -> None:
        await self._email_client.commit()

    async def rollback(self) -> None:
        await self._email_client.rollback()
