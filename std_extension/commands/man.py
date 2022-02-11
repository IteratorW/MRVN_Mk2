from discord import SlashCommand, SlashCommandGroup

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from impl import runtime


@runtime.bot.slash_command(category=categories.info)
async def man(ctx: MrvnCommandContext, cmd_name: ParseUntilEndsOption(str)):
    cmd_split = iter(cmd_name.split())

    name = next(cmd_split)

    for cmd in runtime.bot.application_commands:
        if isinstance(cmd, (
                SlashCommand, SlashCommandGroup)) and cmd.name == name and ctx.guild_id in cmd.guild_ids:
            command = cmd
            break
    else:
        await ctx.respond_embed(Style.ERROR, ctx.translate("std_command_help_command_not_found"))

        return

    root = command

    try:
        while isinstance(command, SlashCommandGroup):
            sub_cmd_name = next(cmd_split)

            command = next(filter(lambda it: it.name == sub_cmd_name, command.subcommands))
    except StopIteration:
        await ctx.respond_embed(Style.INFO, runtime.bot.get_command_desc(root, ctx, as_tree=True))

        return

    embed = ctx.get_embed(Style.INFO)

    embed.add_field(name=runtime.bot.get_command_desc(command, ctx), value=command.description)

    await ctx.respond(embed=embed)
