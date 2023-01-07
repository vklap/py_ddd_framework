from __future__ import annotations

from demo.adapters.clients.pubsub_client import InMemoryPubSubClient, AsyncInMemoryPubSubClient
from demo.adapters.repositories.user_repository import InMemoryUserRepository, AsyncInMemoryUserRepository
from demo.domain.model import ChangeEmailCommand, EmailChangedEvent, NotifySlackEvent
from demo.service_layer.command_handlers.change_email_command_handler import ChangeEmailCommandHandler, \
    AsyncChangeEmailCommandHandler
from demo.service_layer.event_handlers.email_changed_event_handler import EmailChangedEventHandler, \
    AsyncEmailChangedEventHandler
from demo.service_layer.event_handlers.notify_slack_event_handler import NotifySlackEventHandler, \
    AsyncNotifySlackEventHandler
from ddd.bootstrapper import Bootstrapper
from ddd.handlers import AbstractCommandHandler, AbstractEventHandler, AbstractAsyncEventHandler, \
    AbstractAsyncCommandHandler


class DemoBootstrapper(Bootstrapper):
    def __init__(self):
        super().__init__()
        self.user_repository = InMemoryUserRepository()
        self.pubsub_client = InMemoryPubSubClient()
        self.async_user_repository = AsyncInMemoryUserRepository()
        self.async_pubsub_client = AsyncInMemoryPubSubClient()
        self.register_command_handler_factory(ChangeEmailCommand().name, self.create_change_email_command_handler)
        self.register_async_command_handler_factory(
            ChangeEmailCommand().name, self.create_async_change_email_command_handler
        )
        self.register_event_handler_factory(EmailChangedEvent().name, self.create_email_changed_event_handler)
        self.register_async_event_handler_factory(
            EmailChangedEvent().name, self.create_async_email_changed_event_handler
        )
        self.register_event_handler_factory(NotifySlackEvent().name, self.create_notify_slack_event_handler)
        self.register_async_event_handler_factory(
            NotifySlackEvent().name, self.create_async_notify_slack_event_handler
        )

    def create_change_email_command_handler(self) -> AbstractCommandHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return ChangeEmailCommandHandler(self.user_repository)

    def create_email_changed_event_handler(self) -> AbstractEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return EmailChangedEventHandler(self.pubsub_client)

    def create_notify_slack_event_handler(self) -> AbstractEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return NotifySlackEventHandler(self.pubsub_client)

    def create_async_change_email_command_handler(self) -> AbstractAsyncCommandHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return AsyncChangeEmailCommandHandler(self.async_user_repository)

    def create_async_email_changed_event_handler(self) -> AbstractAsyncEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return AsyncEmailChangedEventHandler(self.async_pubsub_client)

    def create_async_notify_slack_event_handler(self) -> AbstractAsyncEventHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return AsyncNotifySlackEventHandler(self.async_pubsub_client)
