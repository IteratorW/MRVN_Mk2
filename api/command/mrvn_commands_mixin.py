from abc import ABC
from typing import Union, List

from discord import Member, SlashCommand, SlashCommandGroup, Bot, ApplicationCommand
from discord.abc import User

from api.command.permission.mrvn_permission import MrvnPermission
from api.models import CommandOverride, MrvnUser
from api.translation.translator import Translator


class MrvnCommandsMixin(Bot, ABC):
    def is_guild_only(self, command: Union[SlashCommand, SlashCommandGroup]):
        return getattr(command, "__mrvn_guild_only__", False)

    def get_translatable_desc(self, command: Union[SlashCommand, SlashCommandGroup], tr: Translator):
        desc = getattr(command, "__mrvn_translatable_desc__", None)

        if not desc:
            return tr.translate("mrvn_api_command_no_desc")

        return tr.translate(desc)

    def get_sub_commands(self, group: SlashCommandGroup):
        commands = []

        for sub_cmd in group.subcommands:
            if isinstance(sub_cmd, SlashCommandGroup):
                commands.extend(self.get_sub_commands(sub_cmd))
            else:
                commands.append(sub_cmd)

        return commands

    async def is_owner(self, user: User) -> bool:
        mrvn_user = await MrvnUser.get_or_none(user_id=user.id)

        if not mrvn_user:
            return False

        return mrvn_user.is_owner

    async def has_permission(self, member: Member, command: Union[SlashCommand, SlashCommandGroup],
                             override: CommandOverride = None):
        mrvn_perm: MrvnPermission = getattr(command, "__mrvn_perm__", None)

        if mrvn_perm and mrvn_perm.owners_only:
            test = await self.is_owner(member)
            return test
        elif override and len(override.discord_permissions):
            perms = override.discord_permissions
        elif mrvn_perm:
            perms = mrvn_perm.discord_permissions
        else:
            return True

        for k, v in iter(member.guild_permissions):
            if k in perms and not v:
                return False

        return True
