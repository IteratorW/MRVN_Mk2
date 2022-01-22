import asyncio
from collections import defaultdict
from typing import Callable

handlers: dict[str, list[Callable]] = defaultdict(list)


def add_handler(event_name: str, func: Callable):
    handlers[event_name].append(func)


def post(event_name: str, *args):
    for handler in handlers[event_name]:
        asyncio.create_task(handler(*args), name=f'mrvn event: {event_name}')
