from __future__ import annotations

import ddd
from demo.adapters.clients.pubsub_client import InMemoryPubSubClient, AsyncInMemoryPubSubClient
from demo.adapters.repositories.user_repository import InMemoryUserRepository, AsyncInMemoryUserRepository
from demo.domain.command_model.email_set_event import EmailSetEvent
from demo.domain.command_model.kpi_event import KpiEvent
from demo.domain.command_model.save_user_command import SaveUserCommand
from demo.service_layer.command_handlers.save_user_command_handler import SaveUserCommandHandler, \
    AsyncChangeEmailCommandHandler
from demo.service_layer.event_handlers.email_set_event_handler import EmailSetEventHandler, \
    AsyncEmailSetEventHandler
from demo.service_layer.event_handlers.kpi_event_handler import KpiEventHandler, \
    AsyncKpiEventHandler


class DemoBootstrapper(ddd.Bootstrapper):
    def __init__(self):
        super().__init__()
        self.user_repository = InMemoryUserRepository()
        self.pubsub_client = InMemoryPubSubClient()
        self.async_user_repository = AsyncInMemoryUserRepository()
        self.async_pubsub_client = AsyncInMemoryPubSubClient()
        self.register_command_handler_factory(SaveUserCommand().name, self.create_save_user_command_handler)
        self.register_async_command_handler_factory(
            SaveUserCommand().name, self.create_async_save_user_command_handler
        )
        self.register_event_handler_factory(EmailSetEvent().name, self.create_email_changed_event_handler)
        self.register_async_event_handler_factory(
            EmailSetEvent().name, self.create_async_email_changed_event_handler
        )
        self.register_event_handler_factory(KpiEvent().name, self.create_kpi_event_handler)
        self.register_async_event_handler_factory(
            KpiEvent().name, self.create_async_kpi_event_handler
        )

    def create_save_user_command_handler(self) -> ddd.AbstractCommandHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return SaveUserCommandHandler(self.user_repository)

    def create_email_changed_event_handler(self) -> ddd.AbstractEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return EmailSetEventHandler(self.pubsub_client)

    def create_kpi_event_handler(self) -> ddd.AbstractEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return KpiEventHandler(self.pubsub_client)

    def create_async_save_user_command_handler(self) -> ddd.AbstractAsyncCommandHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return AsyncChangeEmailCommandHandler(self.async_user_repository)

    def create_async_email_changed_event_handler(self) -> ddd.AbstractAsyncEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return AsyncEmailSetEventHandler(self.async_pubsub_client)

    def create_async_kpi_event_handler(self) -> ddd.AbstractAsyncEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return AsyncKpiEventHandler(self.async_pubsub_client)
