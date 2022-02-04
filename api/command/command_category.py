from typing import Union

from discord import SlashCommand, SlashCommandGroup

from api.translation.translatable import Translatable


def get_sub_commands(group: SlashCommandGroup):
    commands = []

    for sub_cmd in group.subcommands:
        if isinstance(sub_cmd, SlashCommandGroup):
            commands.extend(get_sub_commands(sub_cmd))
        else:
            commands.append(sub_cmd)

    return commands


class CommandCategory:
    def __init__(self, name: Translatable, category_id: str):
        self.name = name
        self.category_id = category_id

        self.items = []

    def add_command(self, command: Union[SlashCommand, SlashCommandGroup]):
        self.items.append(command)

    def get_all_commands(self):
        commands = []

        for command in self.items:
            if isinstance(command, SlashCommandGroup):
                commands.extend(get_sub_commands(command))
            else:
                commands.append(command)

        return commands

