from tortoise import fields

from api.settings import settings
from api.settings.setting import GuildSetting
from api.settings.settings_category import SettingsCategory
from api.translation.translatable import Translatable

mod_category = settings.add_category(SettingsCategory("moderation", Translatable("moderation_category_name")))


class SettingEnableMemberQuitMsg(GuildSetting):
    key = "member_quit_message"
    description = Translatable("moderation_setting_member_quit_message")
    category = mod_category

    value_field = fields.BooleanField(default=True)
