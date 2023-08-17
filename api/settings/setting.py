from typing import TYPE_CHECKING

from tortoise import Model, fields
from tortoise.fields import Field

from api.translation.translatable import Translatable

if TYPE_CHECKING:
    from api.settings.settings_category import SettingsCategory


class Setting(Model):
    key: str = None
    description: Translatable = None
    category: "SettingsCategory" = None

    value_field: Field = None

    @property
    def value(self) -> any:
        return self.value_field

    @value.setter
    def value(self, new_value: any):
        self.value_field = new_value


class GuildSetting(Setting):
    guild_id = fields.BigIntField()


class GlobalSetting(Setting):
    pass
