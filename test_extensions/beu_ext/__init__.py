import logging

import discord
from discord import User, Role
from discord.abc import Mentionable, GuildChannel

from api.command.mrvn_command_context import MrvnCommandContext
from api.event_handler.decorators import event_handler
from impl import runtime


@event_handler()
async def on_startup():
    logging.info("Beu startup!")


@runtime.bot.slash_command()
async def test(ctx: MrvnCommandContext, arg_1: str, arg_2: str):
    """Test message-only command"""

    embed = discord.Embed(title="Error", color=0xff0033, description=f"arg_1: {arg_1}\narg_2: {arg_2}")

    await ctx.respond(embed=embed)


@runtime.bot.slash_command()
async def test_int(ctx: MrvnCommandContext, test_arg: int):
    """Test command with int arg"""

    await ctx.respond(str(test_arg))


@runtime.bot.slash_command()
async def multi_arg(ctx: MrvnCommandContext, string: str, integer: int, boolean: bool, user: User, channel: GuildChannel, role: Role, mentionable: Mentionable, number: float):
    await ctx.respond(f"""
String: {string}
Integer: {integer}
Boolean: {boolean}
User: {user}
Channel: {channel}
Role: {role}
Mentionable: {mentionable}
Number: {number}
""")
