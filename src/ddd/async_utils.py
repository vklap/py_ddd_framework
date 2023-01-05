import asyncio
from collections.abc import Callable
from typing import Any


def to_thread(func: Callable, *args: Any) -> Any:
    """
    Starting from python 3.9, please use asyncio.to_thread - which also supports kwargs
    """
    loop = asyncio.get_running_loop()
    result = loop.run_in_executor(None, func, *args)
    return result
