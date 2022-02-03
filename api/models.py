from abc import ABC, abstractmethod, ABCMeta
from typing import Union, TYPE_CHECKING

from tortoise import Model, fields

from api.translation.translatable import Translatable

if TYPE_CHECKING:
    from api.settings.settings_category import SettingsCategory


class Setting(Model):
    title: Union[str, Translatable] = None
    description: Union[str, Translatable] = None
    category: "SettingsCategory" = None

    @property
    def value(self) -> any:
        pass

    @value.setter
    def value(self, new_value: any):
        pass


class GuildSetting(Setting):
    guild_id = fields.IntField()


class GlobalSetting(Setting):
    pass

