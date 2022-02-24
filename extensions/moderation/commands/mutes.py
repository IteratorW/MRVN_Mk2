import datetime

from discord import Option, OptionChoice, User, Member, Forbidden

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.permission.decorators import mrvn_discord_permissions
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime

TIME_DICT = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "w": 604800,
        "mo": 18144000,
        "y": 217728000
}


@runtime.bot.slash_command(category=categories.moderation, description=Translatable("moderation_command_mute_desc"))
@mrvn_discord_permissions("moderate_members")
async def mute(ctx: MrvnCommandContext, member: Member, time: int, unit: Option(str, choices=[
    OptionChoice("Seconds", "s"),
    OptionChoice("Minutes", "m"),
    OptionChoice("Hours", "h"),
    OptionChoice("Days", "d"),
    OptionChoice("Weeks", "w"),
    OptionChoice("Months", "mo"),
        OptionChoice("Years", "y")])):
    if member == runtime.bot.user:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_cant_do_this_to_bot"))

        return
    elif member == ctx.author:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_cant_do_this_to_self"))

        return
    elif member.guild_permissions.administrator:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_command_mute_cant_mute_administrator"))

        return
    elif ctx.author.top_role.position < member.top_role.position or ctx.author.guild_permissions < member.guild_permissions:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_cant_do_this_to_this_user"))

        return

    timestamp = datetime.datetime.utcnow() + datetime.timedelta(0, time * TIME_DICT[unit])

    try:
        await member.edit(communication_disabled_until=timestamp)
    except Forbidden:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_bot_insufficient_perms"))
    else:
        await ctx.respond_embed(Style.OK, ctx.format("moderation_command_mute_successful", member.mention))


@runtime.bot.slash_command(category=categories.moderation, description=Translatable("moderation_command_unmute_desc"))
@mrvn_discord_permissions("moderate_members")
async def unmute(ctx: MrvnCommandContext, member: Member):
    try:
        await member.edit(communication_disabled_until=None)
    except Forbidden:
        await ctx.respond_embed(Style.ERROR, ctx.translate("moderation_bot_insufficient_perms"))
    else:
        await ctx.respond_embed(Style.OK, ctx.format("moderation_command_unmute_successful", member.mention))
