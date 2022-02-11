from tortoise import fields

from api.settings import settings
from api.settings.setting import GuildSetting, GlobalSetting
from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable

category = settings.add_category(SettingsCategory("beu_ext", Translatable("beu_ext_settings_category_name")))


class GuildSettingTest(GuildSetting):
    key = "guild_setting_test"
    description = Translatable("beu_ext_setting_test_desc")
    category = category

    value_field = fields.IntField(default=12345)


class GlobalSettingTest(GlobalSetting):
    key = "global_setting_test"
    description = Translatable("beu_ext_setting_test_global_desc")
    category = category

    value_field = fields.TextField(default="Global setting default val")
