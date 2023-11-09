from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from extensions.statistics.commands.stats_group import stats_group
from extensions.statistics.plots import smooth_plot


@stats_group.command(description=Translatable("statistics_command_smooth_desc"), name="smooth")
async def smooth(ctx: MrvnCommandContext, period_days: float = 1, max_channels: int = 5):
    await ctx.defer()

    result = await smooth_plot.get_smooth_stats(ctx.guild, period_days, max_channels)

    await ctx.respond(file=File(result, filename="smooth_chart.png"))
