from api.command.context.mrvn_command_context import MrvnCommandContext
from discord import Member, Forbidden

from api.command import categories
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


@runtime.bot.slash_command(category=categories.moderation, description=Translatable("moderation_command_ban_desc"),
                           discord_permissions=["ban_members"])
async def ban(ctx: MrvnCommandContext, member: Member):
    if member == runtime.bot.user:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_cant_do_this_to_bot"))

        return
    elif member == ctx.author:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_cant_do_this_to_self"))

        return
    elif ctx.author.top_role.position < member.top_role.position or ctx.author.guild_permissions < member.guild_permissions:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_cant_do_this_to_this_user"))

        return

    try:
        await member.ban(delete_message_days=0)
    except Forbidden:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_bot_insufficient_perms"))
    else:
        await ctx.respond_embed(Style.OK, ctx.format("moderation_command_ban_success", member.mention))


@runtime.bot.slash_command(category=categories.moderation, description=Translatable("moderation_command_unban_desc"),
                           discord_permissions=["ban_members"])
async def unban(ctx: MrvnCommandContext, member: Member):
    try:
        await member.unban()
    except Forbidden:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_bot_insufficient_perms"))
    else:
        await ctx.respond_embed(Style.OK, ctx.format("moderation_command_unban_successful", member.mention))
