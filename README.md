# A Domain-Driven Design (DDD) Framework for Python Developers

## What is this library good for?
This is a lightweight framework that provides a quick and simple setup for
[Domain-Driven](https://en.wikipedia.org/wiki/Domain-driven_design) designed apps
that are a pleasure to maintain and easy to unit test.

These are the main features that are supported by the framework:
1. **Unit of Work** with a **commit** and **rollback** mechanism for application layer handlers
2. Definition of **Domain Commands** in the domain layer and their **Command Handlers** in the application layer
3. Definition of **Domain Events** in the domain layer and their **Event Handlers** in the application layer
4. **Event-Driven Architecture** based on **Domain Events**

This library has no external dependencies and hence should be easy to add to any project that can benefit from 
DDD.

## Installation

```shell
pip install py-ddd-framework
```

## Import

```python
import asyncio

import ddd

def main():
    bootstrapper = ddd.Bootstrapper()
    command = SaveUserCommand()
    # regular usage
    result = bootstrapper.handle_command(command)
    # async usage
    result = asyncio.run(bootstrapper.async_handle_command(command))
```

## How to implement it?

A sample implementation is provided within the [demo](https://github.com/vklap/py_ddd_framework/tree/main/demo) folder
in the source code. 

To run the demo, please `cd` into the root folder and execute the following command:
```shell
python run_demo.py
```

The below explanation is based on this sample implementation.

## Sample Implementation

Let's imagine a simplified background job for saving a user's details that consists 
of the following steps within a unit of work:

1. Get the new user's data from a **PubSub message broker** (such as Amazon SQS, RabbitMQ, etc.) 
   and transform it into a **command** object that can be handled by the **application layer**
2. Perform basic validations on the **command**'s data
3. Get the existing **user entity** data from the database, via a **repository**
4. Update the **user entity** with the data stored in the **command** object
5. **Save** the updated user entity **in the repository**
6. Either **commit** (and store the new data in the database) 
   or **rollback** (and thus discard the changes recorded in the previous steps)

Steps 2 (command validation) and 6 (commit or rollback) are triggered by the framework.

### How the code looks like?

#### Domain Layer

##### User Entity

```python
from __future__ import annotations

import ddd
from demo.domain.command_model.email_set_event import EmailSetEvent


class User(ddd.AbstractEntity):
    def __init__(self, email: str | None = None, id_: str | None = None):
        super().__init__()
        self._id = id_
        self._email = email

    def get_id(self) -> str:
        return self._id

    def set_id(self, value: str) -> None:
        self._id = value

    @property
    def email(self) -> str:
        return self._email

    def set_email(self, value: str) -> None:
        if value and self._email != value:
            self.add_event(EmailSetEvent(user_id=self._id, new_email=value, old_email=self._email))
        self._email = value

    def __repr__(self) -> str:
        return f'<{type(self).__name__}(id={self._id}, email={self._email})>'
```

##### SaveUserCommand

```python
from __future__ import annotations

import dataclasses

import ddd


@dataclasses.dataclass
class SaveUserCommand(ddd.AbstractCommand):
    user_id: str | None = None
    email: str | None = None

    @property
    def name(self) -> str:
        return type(self).__name__

    def validate(self) -> None:
        if not self.user_id:
            raise ddd.BoundedContextError(ddd.BAD_REQUEST, 'Missing user_id')
        if not self.email:
            raise ddd.BoundedContextError(ddd.BAD_REQUEST, 'Missing email')
```

##### Repository

Please note that we're using an in memory repository for demo purposes 
(and also for the [unit tests](https://github.com/vklap/py_ddd_framework/tree/main/tests))

```python
from __future__ import annotations

import abc

import ddd
from demo.domain.command_model.user import User


class AbstractUserRepository(ddd.RollbackCommitter, abc.ABC):
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


class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        super().__init__()
        self.users_by_id: dict[str, User] = {}
        self._saved_users: list[User] = []
        self.commit_called = False
        self.rollback_called = False
        self.commit_should_fail = False
        self.rollback_should_fail = False

    def _get_by_id(self, id_: str) -> User:
        result = self.users_by_id.get(id_)
        if not result:
            raise ddd.BoundedContextError(ddd.NOT_FOUND, f'User with ID "{id_}" does not exist')
        return result

    def _save(self, user: User) -> None:
        self._saved_users.append(user)

    def commit(self) -> None:
        self.commit_called = True
        if self.commit_should_fail:
            raise Exception('commit failed')
        for user in self._saved_users:
            self.users_by_id[user.get_id()] = user

    def rollback(self) -> None:
        self.rollback_called = True
        if self.rollback_should_fail:
            raise Exception('rollback failed')
        self._saved_users.clear()
```

##### SaveUserCommandHandler

This is the application layer flow that is triggered by the framework's unit of work - 
in order to either commit or rollback the changes. 

This handler is registered to the above defined `SaveUserCommand` - so that whenever this command is received, 
then this handler will be executed. The registration is handled by the `Bootstrapper` which will be shown later.

```python
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
```

##### Registration of the SaveUserCommand with its handler: SaveUserCommandHandler
This happens within the bootstrapper, like so:

```python
from __future__ import annotations

import ddd

from demo.adapters.clients.pubsub_client import InMemoryPubSubClient, AsyncInMemoryPubSubClient
from demo.adapters.repositories.user_repository import InMemoryUserRepository, AsyncInMemoryUserRepository
from demo.domain.command_model.email_set_event import EmailSetEvent
from demo.domain.command_model.kpi_event import KpiEvent
from demo.domain.command_model.save_user_command import SaveUserCommand
from demo.service_layer.command_handlers.save_user_command_handler import SaveUserCommandHandler
from demo.service_layer.event_handlers.email_set_event_handler import EmailSetEventHandler


class DemoBootstrapper(ddd.Bootstrapper):
    def __init__(self):
        super().__init__()
        self.user_repository = InMemoryUserRepository()
        self.pubsub_client = InMemoryPubSubClient()
        self.async_user_repository = AsyncInMemoryUserRepository()
        self.async_pubsub_client = AsyncInMemoryPubSubClient()
        self.register_command_handler_factory(SaveUserCommand().name, self.create_save_user_command_handler)
        self.register_event_handler_factory(EmailSetEvent().name, self.create_email_changed_event_handler)
        self.register_event_handler_factory(KpiEvent().name, self.create_kpi_event_handler)

    def create_save_user_command_handler(self) -> ddd.AbstractCommandHandler:
        """
        Made public for the framework's unit test.
        In realworld usage, this method should best be private.
        """
        return SaveUserCommandHandler(self.user_repository)
```

##### Handling the SaveUserCommand by the framework

Based on the above created bootstrapper instance, 
this is how the command should be propagated into the framework: 
```python
bootstrapper = DemoBootstrapper()

command = SaveUserCommand(user_id='1', email='eli.cohen@mossad.gov.il')

bootstrapper.handle_command(command)
```

### But wait, isn't this code over-engineered?

Basically, if this is all the code should do, then this code is arguably too complex.
Yet, what happens when the requirements grow, and you need to handle other tasks as a result of the above flow, such as:
1. Trigger a verification email to validate the provided email?
2. Notify a KPI Service about the changes - for further analysis
3. Handle other changes, as in a real world scenario the user entity should have much more properties - 
   where each property change might require triggering other actions (a.k.a. `Domain Events`)

The code might quickly look like this:
```python

    def handle(self, command: ddd.TCommand) -> ddd.THandleCommandResult:
        user = self._user_repository.get_by_id(command.user_id)
        user.set_email(command.email)
        # Side effect...
        if user.changed_email:
            self._pubsub_client.notify_email_changed(...)
            self._pubsub_client.notify_kpi_service(...)
        # Side effect...
        if user.phone_number_changed:
            self._pubsub_client.notify_phone_number_changed(...)
            self._pubsub_client.notify_kpi_service(...)
        return user.get_id()
```

The above code will contain lots side effects, and will defeat the SRP (Single Responsibility Principle) 
for which it was created - which is to save the new user details.
Even worse, it will sooner than later become spaghetti code - that will be a nightmare to maintain and unit test. 

### Event-Driven Architecture with EventHandlers to the Rescue
All the above side effects should best be extracted out of the above code, and handled within other handlers. 
These handlers will be handled in the same way as the command handler, 
i.e. within units of work of their own - and may trigger other events which will be handled by the framework.

However, please note that these events will be triggered by the framework - 
and **not** by calling the bootstrapper's `handle_command` method.

Here are 2 sample event handlers:

#### EmailSetEventHandler that will trigger a KPIEvent that will be handled by the KPIEventHandler
```python
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
```

##### KpiEventHandler
```python
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
```

### Advantages of applying the above-mentioned Domain-Driven Design Tactical Patterns

- A clear separation of concerns between the business rules (which reside solely inside the domain layer), 
  the application flows (which reside in the service layer) and the IO related operations - 
  such as communication with databases/web services/file system (which reside in the adapters layer)

- This separation of concerns make this kind of code very suitable for unit & integration tests - 
  the service & domain layers can be fully unit tested and the adapter layer can easily 
  be integration tested (without being concerned with any business logic leaking from the other layers - 
  so that the integration tests can remain simple)
  
- A common code base structure makes it much easier for other developers, 
  who are aware of this structure, to get into the code.
