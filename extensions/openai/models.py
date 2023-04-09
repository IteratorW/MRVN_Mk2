from tortoise import fields

from api.settings import settings
from api.settings.exc import SettingsValueWriteError
from api.settings.setting import GuildSetting, GlobalSetting
from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable

DEFAULT_SYS_MESSAGE = "You are a Discord bot called MRVN Mk2. Your replies are extremely sarcastic."

openai_category = settings.add_category(SettingsCategory("openai", Translatable("openai_settings_category_name")))


class SettingPromptCharLimit(GlobalSetting):
    key = "prompt_char_limit"
    description = Translatable("openai_setting_prompt_char_limit_desc")
    category = openai_category

    value_field = fields.IntField(default=128)


class SettingMaxRequestsPerMinute(GlobalSetting):
    key = "max_requests_per_minute"
    description = Translatable("openai_setting_max_requests_per_minute_desc")
    category = openai_category

    value_field = fields.IntField(default=15)


class SettingSystemMessage(GlobalSetting):
    key = "system_message"
    description = Translatable("openai_setting_system_message")
    category = openai_category

    value_field = fields.TextField(default=DEFAULT_SYS_MESSAGE)


class SettingTemperature(GlobalSetting):
    key = "openai_temperature"
    description = Translatable("openai_setting_temperature")
    category = openai_category

    value_field = fields.FloatField(default=0.7)

    @property
    def value(self) -> any:
        return self.value_field

    @value.setter
    def value(self, new_value: any):
        try:
            new_value = float(new_value)
        except ValueError:
            new_value = None

        if new_value is None or not 0 <= new_value <= 1:
            raise SettingsValueWriteError(Translatable("openai_setting_temperature_invalid"))

        self.value_field = new_value


class SettingOpenAiMaxHistoryLen(GlobalSetting):
    key = "openai_max_history_len"
    description = Translatable("openai_setting_max_history_len")
    category = openai_category

    value_field = fields.IntField(default=10)


class SettingEnableAiCommands(GlobalSetting):
    key = "openai_enable_ai_commands"
    description = Translatable("openai_enable_ai_commands")
    category = openai_category

    value_field = fields.BooleanField(default=True)
