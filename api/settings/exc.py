from api.translation.translatable import Translatable


class SettingsValueWriteError(Exception):
    def __init__(self, message: Translatable):
        self.message = message
