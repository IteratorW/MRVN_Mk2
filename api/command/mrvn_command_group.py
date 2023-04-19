from discord.ext.bridge import BridgeCommandGroup, BridgeExtGroup, BridgeSlashGroup
from discord.ext.commands import Context

from api.command.mrvn_command import MrvnCommand
from api.command.mrvn_context import MrvnContext, MrvnPrefixContext
from api.embed.style import Style


class MrvnCommandGroup(BridgeCommandGroup):
    # noinspection PyMissingConstructor
    def __init__(self, *args, **kwargs):
        self.ext_variant: MrvnPrefixGroup = (ext_var := MrvnPrefixGroup(self.custom_callback, *args, **kwargs))
        self.slash_variant: MrvnSlashGroup = MrvnSlashGroup(self.custom_callback, kwargs.pop("name", ext_var.name), *args, **kwargs)
        self.parent = kwargs.pop("parent", None)

        self.subcommands: list[MrvnCommand] = []

    # Override default behaviour: send unknown subcommand message if no valid subcommand is provided.
    async def custom_callback(self, ctx: MrvnContext):
        await ctx.respond_embed(Style.ERROR, "Unknown subcommand!")


class MrvnPrefixGroup(BridgeExtGroup):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self.invoke_without_command = True


class MrvnSlashGroup(BridgeSlashGroup):
    pass
