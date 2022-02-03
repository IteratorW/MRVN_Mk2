from typing import Union

from api.models import GlobalSetting, GuildSetting
from api.translation.translatable import Translatable


class SettingsCategory:
    def __init__(self, category_id: str, name: Union[str, Translatable]):
        self.category_id = category_id
        self.name = name

    def get_settings(self, guild: bool = False):
        cls = GuildSetting if guild else GlobalSetting

        return [x for x in cls.__subclasses__() if x.category == self]
