from tortoise import fields

from api.settings import settings
from api.settings.setting import GuildSetting
from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable

search_category = settings.add_category(SettingsCategory("search", Translatable("search_category_name")))


class SettingEnableSafeSearch(GuildSetting):
    key = "safe_search"
    description = Translatable("search_setting_safe_search")
    category = search_category

    value_field = fields.BooleanField(default=False)
