import logging

import discord
from discord import User, Role, Option, OptionChoice
from discord.abc import Mentionable, GuildChannel
from discord.enums import SlashCommandOptionType

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.ParseUntilEndsOption import ParseUntilEndsOption
from api.embed.style import Style
from api.event_handler.decorators import event_handler
from impl import runtime


@event_handler()
async def on_startup():
    logging.info("Beu startup!")


@runtime.bot.slash_command()
async def test(ctx: MrvnCommandContext, arg_1: str, arg_2: str):
    """Test command"""

    await ctx.respond_embed(Style.INFO, desc=f"arg_1: {arg_1}\narg_2: {arg_2}")


@runtime.bot.slash_command()
async def test_int(ctx: MrvnCommandContext, test_arg: int):
    """Test command with int arg"""

    await ctx.respond_embed(Style.INFO, str(test_arg))


@runtime.bot.slash_command()
async def multi_arg(ctx: MrvnCommandContext, string: str, integer: int, boolean: bool, user: User, channel: GuildChannel, role: Role, mentionable: Mentionable, number: float):
    await ctx.respond_embed(Style.INFO, f"""
String: `{string}`
Integer: `{integer}`
Boolean: `{boolean}`
User: `{user}`
Channel: `{channel}`
Role: `{role}`
Mentionable: `{mentionable}`
Number: `{number}`
""")


@runtime.bot.slash_command()
async def optional_arg(ctx, optional: int = 0):
    await ctx.respond_embed(Style.INFO, str(optional))


group = runtime.bot.create_group("group", "A group")
sub_group = group.create_subgroup("subgroup", "A subgroup")


@group.command()
async def group_command(ctx):
    await ctx.respond_embed(Style.INFO, "Group test")


@sub_group.command()
async def sub_group_command(ctx):
    await ctx.respond_embed(Style.INFO, "Subgroup test!")


@sub_group.command()
async def sub_group_command2(ctx, test_arg: int):
    await ctx.respond_embed(Style.INFO, f"Argument: {test_arg}")


@runtime.bot.slash_command()
async def until_ends(ctx, query: ParseUntilEndsOption(str)):
    await ctx.respond_embed(Style.INFO, f"Query: `{query}`")


@runtime.bot.slash_command()
async def choices(ctx, choice_str: Option(str, choices=[OptionChoice("Choice 1", "Anus"),
                                                        OptionChoice("Choice 2", "Amogus"),
                                                        OptionChoice("Choice 3", "Test")])):
    await ctx.respond_embed(Style.INFO, f"{choice_str}")


@runtime.bot.slash_command()
async def attach(ctx, attachment: Option(SlashCommandOptionType.attachment)):
    await ctx.respond_embed(Style.OK, attachment.url)
