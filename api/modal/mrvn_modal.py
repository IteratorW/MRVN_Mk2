from discord.ui import Modal

from api.translation.translator import Translator


class MrvnModal(Modal):
    def __init__(self, tr: Translator, title: str, **kwargs):
        super().__init__(title, **kwargs)
        self.tr = tr
