import datetime

from discord import File

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.statistics import utils
from extensions.statistics.commands.date_validator import validate_date
from extensions.statistics.commands.stats_group import stats_group
from extensions.statistics.plots.daily import daily_stats
from extensions.statistics.utils import NotEnoughInformationError


@stats_group.command(description=Translatable("statistics_command_daily_desc"), name="daily")
async def daily_command(ctx: MrvnCommandContext, date: str = None):
    if date:
        date = await validate_date(ctx, date)

        if date is None:
            return
    else:
        date = datetime.date.today()

    await ctx.defer()

    try:
        result = await daily_stats.get_daily_chart_for_date(ctx.guild, date)
    except NotEnoughInformationError:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_not_enough_information_for_this_date"))
        return

    await ctx.respond(file=File(result, filename="daily_chart.png"))
