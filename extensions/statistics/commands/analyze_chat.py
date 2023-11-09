import datetime

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.statistics import ai_chat_analyzer, utils
from extensions.statistics.commands.date_validator import validate_date
from extensions.statistics.commands.stats_group import stats_group
from extensions.statistics.utils import NotEnoughInformationError


@stats_group.command(description=Translatable("statistics_command_analyze_chat_desc"), name="analyze_chat")
async def analyze_chat_command(ctx: MrvnCommandContext, date: str = None):
    if date:
        date = await validate_date(ctx, date)

        if date is None:
            return
    else:
        date = datetime.date.today()

    await ctx.defer()

    try:
        result = await ai_chat_analyzer.analyze_chat(ctx.guild, date)
    except NotEnoughInformationError:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_not_enough_information_for_this_date"))
        return

    if not result:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_command_analyze_chat_error"))
        return

    await ctx.respond_embed(Style.INFO, result, ctx.format("statistics_command_analyze_chat_title",
                                                           date.strftime("%d.%m.%Y")))
