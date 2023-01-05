from __future__ import annotations

import ddd
from demo.adapters.clients.pubsub_client import AbstractPubSubClient, AbstractAsyncPubSubClient
from demo.domain.command_model.email_set_event import EmailSetEvent
from demo.domain.command_model.kpi_event import KpiEvent


class EmailSetEventHandler(ddd.AbstractEventHandler[EmailSetEvent]):
    def __init__(self, email_client: AbstractPubSubClient):
        super().__init__()
        self._email_client = email_client
        self._events: list[ddd.AbstractEvent] = []

    def handle(self, event: ddd.TEvent) -> None:
        self._email_client.notify_email_changed(event.user_id, event.new_email, event.old_email)
        self._events.append(
            KpiEvent(action=event.name, data=f'{event!r}')
        )

    @property
    def events(self) -> list[ddd.AbstractEvent]:
        return list(self._events)

    def commit(self) -> None:
        self._email_client.commit()

    def rollback(self) -> None:
        self._email_client.rollback()


class AsyncEmailSetEventHandler(ddd.AbstractAsyncEventHandler[EmailSetEvent]):
    def __init__(self, email_client: AbstractAsyncPubSubClient):
        super().__init__()
        self._email_client = email_client
        self._events: list[ddd.AbstractEvent] = []

    async def handle(self, event: ddd.TEvent) -> None:
        await self._email_client.notify_email_changed(event.user_id, event.new_email, event.old_email)
        self._events.append(
            KpiEvent(action=event.name, data=f'{event!r}')
        )

    @property
    def events(self) -> list[ddd.AbstractEvent]:
        return list(self._events)

    async def commit(self) -> None:
        await self._email_client.commit()

    async def rollback(self) -> None:
        await self._email_client.rollback()
