from typing import List, Dict, Any

from discord import User, Interaction
from discord.ui import View, Item, Button, Select

from api.embed import styled_embed_generator
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.translation.translator import Translator


class MrvnView(View):
    def __init__(self, tr: Translator, author: User = None, *items: Item, **kwargs):
        super().__init__(*items, **kwargs)

        self.author = author
        self.tr = tr  # This potentially clogs up memory if Context being passed here.
        # A possible fix is to pass lang string or a new instance of Translator

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user == self.author:
            return True

        embed = styled_embed_generator.get_embed(Style.ERROR, self.tr.translate("mrvn_core_views_not_an_author"),
                                                 translator=self.tr)

        await interaction.response.send_message(embed=embed, ephemeral=True)

        return False
    
    def add_item(self, item: Item) -> None:
        if isinstance(item, Button) and isinstance(item.label, Translatable):
            item.label = self.tr.translate(item.label)
        elif isinstance(item, Select):
            if isinstance(item.placeholder, Translatable):
                item.placeholder = self.tr.translate(item.placeholder)

            for option in item.options:
                if isinstance(option.label, Translatable):
                    option.label = self.tr.translate(option.label)
                if isinstance(option.description, Translatable):
                    option.description = self.tr.translate(option.description)

        super().add_item(item)
