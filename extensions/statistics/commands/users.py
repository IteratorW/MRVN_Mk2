from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.statistics.commands import stats


@stats.stats_group.command(description=Translatable("statistics_command_users_desc"), name="users")
async def users_command(ctx: MrvnCommandContext):
    await ctx.defer()

    await ctx.respond_embed(Style.WARN, "!")
