from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics.commands.stats_group import stats_group
from extensions.statistics.plots import msg_counts_plot


@stats_group.command(description=Translatable("statistics_command_messages_desc"), name="messages")
async def messages_command(ctx: MrvnCommandContext):
    await ctx.defer()

    result = await msg_counts_plot.get_messages_stats(ctx.guild)

    await ctx.respond(file=File(result, filename="messages_chart.png"))
