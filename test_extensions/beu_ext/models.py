from api.models import GuildSetting, GlobalSetting
from tortoise import fields

from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable


category = SettingsCategory("beu_ext", Translatable("beu_ext_settings_category_name"))


class GuildSettingTest(GuildSetting):
    title = Translatable("beu_ext_setting_test_title")
    description = Translatable("beu_ext_setting_test_desc")
    category = category

    _value = fields.TextField(default="Anus")

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, new_value: any):
        self._value = new_value


class GlobalSettingTest(GlobalSetting):
    title = Translatable("beu_ext_setting_test_global_title")
    description = Translatable("beu_ext_setting_test_global_desc")
    category = category

    _value = fields.TextField(default="Global setting default val")

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, new_value: any):
        self._value = new_value
