from abc import ABC, abstractmethod, ABCMeta
from typing import Union, TYPE_CHECKING

from tortoise import Model, fields
from tortoise.fields import Field

from api.command.const import PREFIX_LIST
from api.list_field import ListField
from api.settings import settings
from api.settings.exc import SettingsValueWriteError
from api.settings.setting import GuildSetting, GlobalSetting
from api.translation import translations
from api.translation.translatable import Translatable

from api.settings.settings_category import SettingsCategory

mrvn_category = settings.add_category(SettingsCategory("mrvn", Translatable("mrvn_api_settings_category_name")))


class MrvnUser(Model):
    user_id = fields.IntField(pk=True)
    is_owner = fields.BooleanField(default=False)


class CommandOverride(Model):
    command_name = fields.CharField(max_length=32)
    guild_id = fields.IntField()

    disabled = fields.BooleanField(default=False)
    discord_permissions = ListField[str](default=[])
    whitelist_channel_ids = ListField[int](default=[])
    prefix = fields.CharField(max_length=1, default="")

    class Meta:
        unique_together = (("command_name", "guild_id"), )


# Settings ======================

class SettingGuildLanguage(GuildSetting):
    key = "guild_lang"
    description = Translatable("mrvn_api_setting_guild_language_desc")
    category = mrvn_category

    value_field = fields.TextField(default="en")

    @property
    def value(self) -> any:
        return self.value_field

    @value.setter
    def value(self, new_value: any):
        if new_value not in translations.translations.keys():
            raise SettingsValueWriteError(Translatable("mrvn_api_setting_guild_language_error"))

        self.value_field = new_value


class SettingEnableMessageCommands(GuildSetting):
    key = "message_commands"
    description = Translatable("mrvn_api_setting_enable_message_commands_desc")
    category = mrvn_category

    value_field = fields.BooleanField(default=False)


class SettingMessageCmdPrefix(GuildSetting):
    key = "command_prefix"
    description = Translatable("mrvn_api_setting_message_cmd_prefix_desc")
    category = mrvn_category

    value_field = fields.CharField(default="!", max_length=1)

    @property
    def value(self) -> any:
        return self.value_field

    @value.setter
    def value(self, new_value: any):
        if new_value not in PREFIX_LIST:
            raise SettingsValueWriteError(Translatable("mrvn_api_setting_prefix_invalid"))

        self.value_field = new_value


class SettingAllowCommandsInDMs(GlobalSetting):
    key = "dm_commands"
    description = Translatable("mrvn_api_setting_allow_dm_commands")
    category = mrvn_category

    value_field = fields.BooleanField(default=False)

