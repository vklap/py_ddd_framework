import pytest

from demo.domain.model import User, ChangeEmailCommand
from demo.entrypoints.bootstrapper import DemoBootstrapper
import ddd
from ddd.error import BoundedContextError


class TestBootstrapper:
    OLD_EMAIL = 'kamel.amin@thaabet.sy'
    NEW_EMAIL = 'eli.cohen@mossad.gov.il'
    USER_ID = 'agent_566'
    A_NAME = 'a name'

    @pytest.fixture
    def bootstrapper(self) -> DemoBootstrapper:
        return DemoBootstrapper()

    def test_change_email(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        result = bootstrapper.handle_command(command)

        assert result == self.USER_ID
        user = bootstrapper.user_repository.users_by_id[self.USER_ID]
        assert user.email == self.NEW_EMAIL
        assert bootstrapper.user_repository.commit_called
        assert not bootstrapper.user_repository.rollback_called
        assert bootstrapper.pubsub_client.new_email == self.NEW_EMAIL
        assert bootstrapper.pubsub_client.old_email == self.OLD_EMAIL
        assert bootstrapper.pubsub_client.user_id == self.USER_ID
        assert bootstrapper.pubsub_client.sent_slack_message

    def test_invalid_command(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = ChangeEmailCommand(self.USER_ID, new_email='')

        with pytest.raises(BoundedContextError) as e:
            bootstrapper.handle_command(command)

        assert e.value.status_code == ddd.error.BAD_REQUEST
        assert 'missing' in str(e.value).lower()

    def test_user_does_not_exist(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = ChangeEmailCommand('not-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(BoundedContextError) as e:
            bootstrapper.handle_command(command)

        assert e.value.status_code == ddd.error.NOT_FOUND
        assert 'does not exist' in str(e.value).lower()
        assert bootstrapper.user_repository.rollback_called

    def test_command_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.user_repository.commit_should_raise = True
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert 'commit failed' in str(e.value).lower()
        assert bootstrapper.user_repository.commit_called
        assert not bootstrapper.user_repository.rollback_called

    def test_command_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.user_repository.rollback_should_raise = True
        command = ChangeEmailCommand('non-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert 'rollback failed' in str(e.value).lower()
        assert not bootstrapper.user_repository.commit_called
        assert bootstrapper.user_repository.rollback_called

    def test_event_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.pubsub_client.commit_should_raise = True
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert 'commit failed' in str(e.value).lower()
        assert bootstrapper.user_repository.commit_called
        assert bootstrapper.pubsub_client.commit_called
        assert not bootstrapper.pubsub_client.rollback_called

    def test_event_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.pubsub_client.notify_should_raise = True
        bootstrapper.pubsub_client.rollback_should_raise = True
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            bootstrapper.handle_command(command)

        assert 'rollback failed' in str(e.value).lower()
        assert bootstrapper.user_repository.commit_called
        assert not bootstrapper.pubsub_client.commit_called
        assert bootstrapper.pubsub_client.rollback_called

    @pytest.mark.asyncio
    async def test_async_change_email(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        result = await bootstrapper.async_handle_command(command)

        assert result == self.USER_ID
        user = bootstrapper.async_user_repository.users_by_id[self.USER_ID]
        assert user.email == self.NEW_EMAIL
        assert bootstrapper.async_user_repository.commit_called
        assert not bootstrapper.async_user_repository.rollback_called
        assert bootstrapper.async_pubsub_client.sent_email
        assert bootstrapper.async_pubsub_client.new_email == self.NEW_EMAIL
        assert bootstrapper.async_pubsub_client.old_email == self.OLD_EMAIL
        assert bootstrapper.async_pubsub_client.user_id == self.USER_ID
        assert bootstrapper.async_pubsub_client.sent_slack_message

    @pytest.mark.asyncio
    async def test_async_invalid_command(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = ChangeEmailCommand(self.USER_ID, new_email='')

        with pytest.raises(BoundedContextError) as e:
            await bootstrapper.async_handle_command(command)

        assert e.value.status_code == ddd.error.BAD_REQUEST
        assert 'missing' in str(e.value).lower()

    @pytest.mark.asyncio
    async def test_async_user_does_not_exist(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        command = ChangeEmailCommand('not-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(BoundedContextError) as e:
            await bootstrapper.async_handle_command(command)

        assert e.value.status_code == ddd.error.NOT_FOUND
        assert 'does not exist' in str(e.value).lower()
        assert bootstrapper.async_user_repository.rollback_called

    @pytest.mark.asyncio
    async def test_async_command_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_user_repository.commit_should_raise = True
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert 'commit failed' in str(e.value).lower()
        assert bootstrapper.async_user_repository.commit_called
        assert not bootstrapper.async_user_repository.rollback_called

    @pytest.mark.asyncio
    async def test_async_command_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_user_repository.rollback_should_raise = True
        command = ChangeEmailCommand('non-existing-user-id', self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert 'rollback failed' in str(e.value).lower()
        assert not bootstrapper.async_user_repository.commit_called
        assert bootstrapper.async_user_repository.rollback_called

    @pytest.mark.asyncio
    async def test_async_event_handler_commit_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_pubsub_client.commit_should_raise = True
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert 'commit failed' in str(e.value).lower()
        assert bootstrapper.async_user_repository.commit_called
        assert bootstrapper.async_pubsub_client.commit_called
        assert not bootstrapper.async_pubsub_client.rollback_called

    @pytest.mark.asyncio
    async def test_async_event_handler_rollback_raises(self, bootstrapper):
        self._fill_user_in_repo(bootstrapper)
        bootstrapper.async_pubsub_client.notify_should_raise = True
        bootstrapper.async_pubsub_client.rollback_should_raise = True
        command = ChangeEmailCommand(self.USER_ID, self.NEW_EMAIL)

        with pytest.raises(Exception) as e:
            await bootstrapper.async_handle_command(command)

        assert 'rollback failed' in str(e.value).lower()
        assert bootstrapper.async_user_repository.commit_called
        assert not bootstrapper.async_pubsub_client.commit_called
        assert bootstrapper.async_pubsub_client.rollback_called

    def test_register_async_command_handler_factory_with_non_async_callable(self, bootstrapper):
        with pytest.raises(ValueError):
            bootstrapper.register_async_command_handler_factory(
                self.A_NAME,
                bootstrapper.create_change_email_command_handler,  # type: ignore
            )

    def test_register_command_handler_factory_with_async_callable(self, bootstrapper):
        with pytest.raises(ValueError):
            bootstrapper.register_command_handler_factory(
                self.A_NAME,
                bootstrapper.create_async_change_email_command_handler,  # type: ignore
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

