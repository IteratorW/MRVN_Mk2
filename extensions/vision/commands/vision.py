import asyncio
from urllib import parse

import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
from discord import Option, Attachment

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime

SERVICE_URL = "https://visionbot.ru/index.php"


@runtime.bot.slash_command(description=Translatable("vision_command_vision_desc"), category=categories.utility)
async def vision(ctx: MrvnCommandContext, image: Option(Attachment)):
    if not image.content_type.startswith("image"):
        await ctx.respond_embed(Style.ERROR, ctx.translate("vision_command_vision_invalid_content_type"))

        return

    await ctx.defer()

    session = aiohttp.ClientSession(timeout=ClientTimeout(20))

    try:
        response = await session.post(SERVICE_URL, data="userlink=%s" % parse.quote(image.url, safe=''),
                                      headers={"Cookie": "textonly=true; imageonly=true; qronly=false",
                                               "Content-Type": "application/x-www-form-urlencoded"})
    except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
        await ctx.respond_embed(Style.ERROR, ctx.translate("vision_command_vision_connection_error"))

        return
    finally:
        await session.close()

    text = await response.text()

    response.close()

    soup = BeautifulSoup(text, "html.parser")
    results = soup.find_all("div", {"class": "success description"})

    if not len(results):
        await ctx.respond_embed(Style.ERROR, ctx.translate("vision_command_vision_fail"))
        return

    embed = ctx.get_embed(Style.INFO, results[0].text, ctx.translate("vision_command_vision_title"))
    embed.set_image(url=image.url)

    await ctx.respond(embed=embed)
