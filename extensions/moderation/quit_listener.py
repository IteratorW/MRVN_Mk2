import discord

from api.embed import styled_embed_generator
from api.embed.style import Style
from api.event_handler.decorators import event_handler
from api.models import SettingGuildLanguage
from api.translation.translator import Translator
from extensions.moderation.models import SettingEnableMemberQuitMsg


@event_handler()
async def on_member_remove(member: discord.Member):
    if not (await SettingEnableMemberQuitMsg.get_or_create(guild_id=member.guild.id))[
            0].value:
        return

    tr = Translator((await SettingGuildLanguage.get_or_create(guild_id=member.guild.id))[0].value)

    embed = styled_embed_generator.get_embed(Style.ERROR, tr.format("moderation_member_has_left",
                                                                    f"{member.mention} ({member.display_name})"))

    embed.title = None

    try:
        await member.guild.system_channel.send(embed=embed)
    except discord.Forbidden:
        pass
