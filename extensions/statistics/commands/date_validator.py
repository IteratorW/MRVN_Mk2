import datetime

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style


async def validate_date(ctx: MrvnCommandContext, date_input: str) -> datetime.date | None:
    try:
        datetime_parsed = datetime.datetime.strptime(date_input, "%d.%m.%Y")
    except ValueError:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_date_validation_invalid"))
        return None

    if datetime.datetime.fromtimestamp(datetime_parsed.timestamp(), tz=datetime.timezone.utc) < ctx.guild.created_at:
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_date_validation_guild_did_not_exist"))
        return None

    date = datetime_parsed.date()

    if date > datetime.date.today():
        await ctx.respond_embed(Style.ERROR, ctx.translate("statistics_date_validation_this_is_from_the_future"))
        return None

    return date
