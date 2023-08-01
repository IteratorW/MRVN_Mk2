import asyncio
import functools
from io import BytesIO

import discord
from api.command.context.mrvn_command_context import MrvnCommandContext
from discord import Option, Attachment

from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.fun_stuff import sussifier
from impl import runtime


@runtime.bot.slash_command(description=Translatable("fun_stuff_command_sus_desc"))
async def sus(ctx: MrvnCommandContext, image: Option(Attachment)):
    if not image.content_type.startswith("image"):
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_sus_invalid_content_type"))

        return

    await ctx.defer()

    image_bytes = BytesIO()
    await image.save(image_bytes)

    this_id = ctx.message.id if not ctx.interaction else ctx.interaction.id

    result = await asyncio.get_event_loop().run_in_executor(None, functools.partial(sussifier.sussify, image_bytes,
                                                                                    str(this_id)))

    if not result:
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_sus_fail"))

        return

    file = discord.File(BytesIO(result), filename=f"{this_id}_sussified.gif")
    embed = ctx.get_embed(Style.INFO, title=ctx.translate("fun_stuff_command_sus_title"))
    embed.set_image(url=f"attachment://{file.filename}")

    await ctx.respond(embed=embed, file=file)
