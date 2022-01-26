import logging

import discord

from api.command.mrvn_command_context import MrvnCommandContext
from api.event_handler.decorators import event_handler
from impl import bot


@event_handler()
async def on_startup():
    logging.info("Beu startup!")


@bot.bot.slash_command()
async def test(ctx: MrvnCommandContext, arg_1: str, arg_2: str):
    """Test message-only command"""

    embed = discord.Embed(title="Error", color=0xff0033, description=f"arg_1: {arg_1}\narg_2: {arg_2}")

    await ctx.respond(embed=embed)


@bot.bot.slash_command()
async def test_int(ctx: MrvnCommandContext, test_arg: int):
    """Test command with int arg"""

    await ctx.respond(str(test_arg))
