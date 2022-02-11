from api.translation.translatable import Translatable


class CommandCategory:
    def __init__(self, name: Translatable):
        self.name = name
