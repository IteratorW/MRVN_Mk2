import discord

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics import autopost
from extensions.statistics.commands import stats


@stats.stats_group.command(description=Translatable("statistics_command_autopost_prompt_desc"))
async def gen_autopost_prompt(ctx: MrvnCommandContext):
    await autopost.send_plot_to_channel(ctx.guild.system_channel)
    #await ctx.respond(await autopost.get_ai_prompt(ctx.guild), allowed_mentions=discord.AllowedMentions(users=False))
