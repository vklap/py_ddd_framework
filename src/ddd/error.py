from __future__ import annotations

NOT_FOUND = 'not_found'
BAD_REQUEST = 'bad_request'
SERVER_ERROR = 'server_error'


class BoundedContextError(Exception):
    def __init__(self, status_code: str = None, *args):
        super().__init__(*args)
        self._status_code = status_code

    @property
    def error(self) -> str:
        return str(self)

    @property
    def status_code(self) -> str | None:
        return self._status_code

