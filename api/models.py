from abc import ABC, abstractmethod, ABCMeta
from typing import Union

from tortoise import Model, fields

from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable


class Setting(Model):
    title: Union[str, Translatable] = None
    description: Union[str, Translatable] = None
    category: SettingsCategory = None

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

