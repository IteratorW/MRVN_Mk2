from abc import ABC
from typing import Any

from discord import Bot

from api.event_handler import handler_manager


class CustomBot(Bot, ABC):
    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event_name, *args, *kwargs)

        handler_manager.post(event_name, *args)
