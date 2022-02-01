from typing import Union

from api.translation.translatable import Translatable


class SettingsCategory:
    def __init__(self, category_id: str, name: Union[str, Translatable]):
        self.category_id = category_id
        self.name = name
