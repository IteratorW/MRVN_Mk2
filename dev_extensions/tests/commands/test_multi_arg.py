from typing import Union

from discord import User, Role, Attachment
from discord.abc import GuildChannel, Mentionable

from api.command.mrvn_context import MrvnContext
from api.embed.style import Style
from impl import runtime


@runtime.bot.mrvn_command()
async def test_multi_arg(ctx: MrvnContext, string: str, integer: int, boolean: bool, user: User,
                         channel: GuildChannel, role: Role, mentionable: Union[User, Role], number: float,
                         attachment: Attachment):
    await ctx.respond_embed(Style.INFO, f"""Multi-argument test:
String: `{string}`
Integer: `{integer}`
Boolean: `{boolean}`
User: {user.mention}
Channel: {channel.mention}
Role: {role.mention}
Mentionable: `{mentionable}`
Number: `{number}`
Attachment: {attachment.url}
""")
