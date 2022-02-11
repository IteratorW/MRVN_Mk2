from api.settings.setting import GuildSetting, GlobalSetting
from api.translation.translatable import Translatable


class SettingsCategory:
    def __init__(self, category_id: str, name: Translatable):
        self.category_id = category_id
        self.name = name

    def get_settings(self, is_global: bool = True):
        cls = GlobalSetting if is_global else GuildSetting

        return [x for x in cls.__subclasses__() if x.category == self]
