from typing import Union

from discord import ApplicationContext, Interaction


class MrvnCommandContext(ApplicationContext):
    def __init__(self, bot, interaction: Union[Interaction, None]):
        super().__init__(bot, interaction)

