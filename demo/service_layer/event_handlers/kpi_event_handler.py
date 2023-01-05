from __future__ import annotations

import ddd
from demo.adapters.clients.pubsub_client import AbstractPubSubClient, AbstractAsyncPubSubClient
from demo.domain.command_model.kpi_event import KpiEvent


class KpiEventHandler(ddd.AbstractEventHandler[KpiEvent]):
    def __init__(self, pubsub_client: AbstractPubSubClient):
        super().__init__()
        self._pubsub_client = pubsub_client
        self._events: list[ddd.AbstractEvent] = []

    def handle(self, event: ddd.TEvent) -> None:
        self._pubsub_client.notify_kpi_service(event)

    @property
    def events(self) -> list[ddd.AbstractEvent]:
        return list(self._events)

    def commit(self) -> None:
        self._pubsub_client.commit()

    def rollback(self) -> None:
        self._pubsub_client.rollback()


class AsyncKpiEventHandler(ddd.AbstractAsyncEventHandler[KpiEvent]):
    def __init__(self, pubsub_client: AbstractAsyncPubSubClient):
        super().__init__()
        self._pubsub_client = pubsub_client
        self._events: list[ddd.AbstractEvent] = []

    async def handle(self, event: ddd.TEvent) -> None:
        await self._pubsub_client.notify_kpi_service(event)

    @property
    def events(self) -> list[ddd.AbstractEvent]:
        return list(self._events)

    async def commit(self) -> None:
        await self._pubsub_client.commit()

    async def rollback(self) -> None:
        await self._pubsub_client.rollback()
