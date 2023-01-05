import asyncio

from demo.domain.command_model.save_user_command import SaveUserCommand
from demo.domain.command_model.user import User
from demo.entrypoints.bootstrapper import DemoBootstrapper


def main():
    # Setup demo bootstrap with fake in memory data
    bootstrapper = DemoBootstrapper()
    bootstrapper.async_user_repository.users_by_id['1'] = User(email='kamel.amin@thaabet.sy', id_='1')

    # Imagine you just received a ChangeEmail message from pubsub
    command = SaveUserCommand(user_id='1', email='eli.cohen@mossad.gov.il')

    asyncio.run(bootstrapper.async_handle_command(command))


if __name__ == '__main__':
    main()
