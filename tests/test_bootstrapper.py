import pytest

import ddd
from demo.domain.command_model.save_user_command import SaveUserCommand
from demo.domain.command_model.user import User
from demo.entrypoints.bootstrapper import DemoBootstrapper


class TestBootstrapper:
    A_NAME = 'a name'
    COMMIT_FAILED = 'commit failed'
    ROLLBACK_FAILED = 'rollback failed'
    NEW_EMAIL = 'eli.cohen@mossad.gov.il'
    OLD_EMAIL = 'kamel.amin@thaabet.sy'
    USER_ID = 'agent_566'

    @pytest.fixture
    def bootstrapper(self) -> DemoBootstrapper:
        return DemoBootstrapper()

    def test_change_email(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        result = bootstrapper.handle_command(command)

        assert result == self.USER_ID
        user = bootstrapper.user_repository.users_by_id[self.USER_ID]
        assert user.email == self.NEW_EMAIL
        assert bootstrapper.user_repository.commit_called
        assert not bootstrapper.user_repository.rollback_called
        assert bootstrapper.pubsub_client.notify_email_set_new_email == self.NEW_EMAIL
        assert bootstrapper.pubsub_client.notify_email_set_old_email == self.OLD_EMAIL
        assert bootstrapper.pubsub_client.notify_email_set_user_id == self.USER_ID
        assert bootstrapper.pubsub_client.kpi_event_sent

    def test_invalid_command(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = SaveUserCommand(self.USER_ID, email='')

        with pytest.raises(ddd.BoundedContextError) as e:
            bootstrapper.handle_command(command)

        assert e.value.status_code == ddd.error.BAD_REQUEST
        assert 'missing' in str(e.value).lower()

    def test_user_does_not_exist(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = SaveUserCommand('not-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(ddd.BoundedContextError) as e:
            bootstrapper.handle_command(command)

        assert e.value.status_code == ddd.error.NOT_FOUND
        assert 'does not exist' in str(e.value).lower()
        assert bootstrapper.user_repository.rollback_called

    def test_command_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.user_repository.commit_should_fail = True
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert self.COMMIT_FAILED in str(e.value).lower()
        assert bootstrapper.user_repository.commit_called
        assert not bootstrapper.user_repository.rollback_called

    def test_command_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.user_repository.rollback_should_fail = True
        command = SaveUserCommand('non-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert self.ROLLBACK_FAILED in str(e.value).lower()
        assert not bootstrapper.user_repository.commit_called
        assert bootstrapper.user_repository.rollback_called

    def test_event_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.pubsub_client.commit_should_fail = True
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert self.COMMIT_FAILED in str(e.value).lower()
        assert bootstrapper.user_repository.commit_called
        assert bootstrapper.pubsub_client.commit_called
        assert not bootstrapper.pubsub_client.rollback_called

    def test_event_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.pubsub_client.notify_email_set_should_fail = True
        bootstrapper.pubsub_client.rollback_should_fail = True
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert self.ROLLBACK_FAILED in str(e.value).lower()
        assert bootstrapper.user_repository.commit_called
        assert not bootstrapper.pubsub_client.commit_called
        assert bootstrapper.pubsub_client.rollback_called

    @pytest.mark.asyncio
    async def test_async_change_email(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        result = await bootstrapper.async_handle_command(command)

        assert result == self.USER_ID
        user = bootstrapper.async_user_repository.users_by_id[self.USER_ID]
        assert user.email == self.NEW_EMAIL
        assert bootstrapper.async_user_repository.commit_called
        assert not bootstrapper.async_user_repository.rollback_called
        assert bootstrapper.async_pubsub_client.email_sent
        assert bootstrapper.async_pubsub_client.notify_email_set_new_email == self.NEW_EMAIL
        assert bootstrapper.async_pubsub_client.notify_email_set_old_email == self.OLD_EMAIL
        assert bootstrapper.async_pubsub_client.notify_email_set_user_id == self.USER_ID
        assert bootstrapper.async_pubsub_client.kpi_event_sent

    @pytest.mark.asyncio
    async def test_async_invalid_command(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = SaveUserCommand(self.USER_ID, email='')

        with pytest.raises(ddd.BoundedContextError) as e:
            await bootstrapper.async_handle_command(command)

        assert e.value.status_code == ddd.error.BAD_REQUEST
        assert 'missing' in str(e.value).lower()

    @pytest.mark.asyncio
    async def test_async_user_does_not_exist(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = SaveUserCommand('not-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(ddd.BoundedContextError) as e:
            await bootstrapper.async_handle_command(command)

        assert e.value.status_code == ddd.error.NOT_FOUND
        assert 'does not exist' in str(e.value).lower()
        assert bootstrapper.async_user_repository.rollback_called

    @pytest.mark.asyncio
    async def test_async_command_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_user_repository.commit_should_fail = True
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert self.COMMIT_FAILED in str(e.value).lower()
        assert bootstrapper.async_user_repository.commit_called
        assert not bootstrapper.async_user_repository.rollback_called

    @pytest.mark.asyncio
    async def test_async_command_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_user_repository.rollback_should_fail = True
        command = SaveUserCommand('non-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert self.ROLLBACK_FAILED in str(e.value).lower()
        assert not bootstrapper.async_user_repository.commit_called
        assert bootstrapper.async_user_repository.rollback_called

    @pytest.mark.asyncio
    async def test_async_event_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_pubsub_client.commit_should_fail = True
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert self.COMMIT_FAILED in str(e.value).lower()
        assert bootstrapper.async_user_repository.commit_called
        assert bootstrapper.async_pubsub_client.commit_called
        assert not bootstrapper.async_pubsub_client.rollback_called

    @pytest.mark.asyncio
    async def test_async_event_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_pubsub_client.notify_email_set_should_fail = True
        bootstrapper.async_pubsub_client.rollback_should_fail = True
        command = SaveUserCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert self.ROLLBACK_FAILED in str(e.value).lower()
        assert bootstrapper.async_user_repository.commit_called
        assert not bootstrapper.async_pubsub_client.commit_called
        assert bootstrapper.async_pubsub_client.rollback_called

    def test_register_async_command_handler_factory_with_non_async_callable(self, bootstrapper):
        with pytest.raises(ValueError):
            bootstrapper.register_async_command_handler_factory(
                self.A_NAME,
                bootstrapper.create_save_user_command_handler,  # type: ignore
            )

    def test_register_command_handler_factory_with_async_callable(self, bootstrapper):
        with pytest.raises(ValueError):
            bootstrapper.register_command_handler_factory(
                self.A_NAME,
                bootstrapper.create_async_save_user_command_handler,  # type: ignore
            )

    def test_register_async_event_handler_factory_with_non_async_callable(self, bootstrapper):
        with pytest.raises(ValueError):
            bootstrapper.register_async_event_handler_factory(
                self.A_NAME,
                bootstrapper.create_email_changed_event_handler,  # type: ignore
            )

    def test_register_event_handler_factory_with_async_callable(self, bootstrapper):
        with pytest.raises(ValueError):
            bootstrapper.register_event_handler_factory(
                self.A_NAME,
                bootstrapper.create_async_email_changed_event_handler,  # type: ignore
            )

    @classmethod
    def _fill_user_in_repo(cls, bs: DemoBootstrapper) -> None:
        bs.user_repository.users_by_id[cls.USER_ID] = User(email=cls.OLD_EMAIL, id_=cls.USER_ID)
        bs.async_user_repository.users_by_id[cls.USER_ID] = User(email=cls.OLD_EMAIL, id_=cls.USER_ID)

