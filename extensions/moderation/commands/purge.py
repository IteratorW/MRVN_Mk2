from api.command.context.mrvn_command_context import MrvnCommandContext
from discord import Option, Member, Forbidden

from api.command import categories
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


# Note: it seems that purge in Pycord is broken and this command cannot be executed more than once for some reason.


@runtime.bot.slash_command(category=categories.moderation, description=Translatable("moderation_command_purge_desc"),
                           discord_permissions=["manage_messages"])
async def purge(ctx: MrvnCommandContext, number: Option(int, min_value=1, max_value=200), member: Member = None):
    try:
        deleted = await ctx.channel.purge(limit=number, check=lambda msg: member is None or msg.author == member,
                                          bulk=True)
    except Forbidden:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_bot_insufficient_perms"))
    else:
        await ctx.respond_embed(Style.OK,
                                ctx.format("moderation_command_purge_messages_removed", ctx.author.mention, deleted))
