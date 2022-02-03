from typing import Union

from discord import SlashCommand, SlashCommandGroup

from api.translation.translatable import Translatable


class CommandCategory:
    def __init__(self, name: Translatable, category_id: str):
        self.name = name
        self.category_id = category_id

        self.items = []

    def add_command(self, command: Union[SlashCommand, SlashCommandGroup]):
        self.items.append(command)
