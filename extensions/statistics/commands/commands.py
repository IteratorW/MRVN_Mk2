from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.statistics.commands import stats
from extensions.statistics.models import StatsCommandEntry, StatsUserCommandsEntry
from impl import runtime


def get_user_mention(user_id: int):
    user = runtime.bot.get_user(user_id)

    return user.mention if user else "N/A"


@stats.stats_group.command(description=Translatable("statistics_command_commands_desc"))
async def commands(ctx: MrvnCommandContext):
    await ctx.defer()

    command_entries = sorted(await StatsCommandEntry.filter(guild_id=ctx.guild_id), key=lambda k: k.count,
                             reverse=True)[:10]
    command_stats = "\n".join([f"**{x.command_name}** - `{x.count}`" for x in command_entries])

    user_entries = sorted(await StatsUserCommandsEntry.filter(guild_id=ctx.guild_id), key=lambda k: k.count,
                          reverse=True)[:10]
    user_stats = "\n".join([f"{get_user_mention(x.user_id)} - `{x.count}`" for x in user_entries])

    embed = ctx.get_embed(Style.INFO, title=ctx.translate("statistics_command_commands_title"))
    embed.description = f"""
{ctx.translate("statistics_command_commands_command_top")}
{command_stats}
{ctx.translate("statistics_command_commands_user_top")}
{user_stats}
"""

    await ctx.respond(embed=embed)
