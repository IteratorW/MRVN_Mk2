import asyncio
from io import BytesIO

from aiohttp import ClientSession, ClientTimeout, ClientConnectionError
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from discord import File

from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime

TTS_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "access-control-allow-origin": "*",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://fifteen.ai",
    "referer": "https://fifteen.ai/app",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "python-requests 15.ai-Python-API(https://github.com/wafflecomposite/15.ai-Python-API)"
}
TTS_URL = "https://api.15.ai/app/getAudioFile5"
AUDIO_URL = "https://cdn.15.ai/audio/"


@runtime.bot.slash_command(description=Translatable("fun_stuff_command_glados_desc"))
async def glados(ctx: MrvnCommandContext, text: ParseUntilEndsOption(str)):
    await ctx.defer()

    data = {"text": text, "character": "GLaDOS", "emotion": "Contextual"}

    session = ClientSession(timeout=ClientTimeout(20))

    try:
        response = await session.post(TTS_URL, headers=TTS_HEADERS, json=data)
    except (asyncio.TimeoutError, ClientConnectionError):
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_glados_request_error"))

        return

    if response.status != 200:
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_glados_api_error"))

        return

    response_data = await response.json(content_type=None)
    response.close()

    result_url = AUDIO_URL + response_data["wavNames"][0]

    try:
        response = await session.get(result_url, headers=TTS_HEADERS)
    except (asyncio.TimeoutError, ClientConnectionError):
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_glados_download_error"))

        return

    buf = BytesIO(await response.read())

    await session.close()
    response.close()

    await ctx.respond(
        file=File(buf, filename=f"GLaDOS_{ctx.message.id if not ctx.interaction else ctx.interaction.id}.wav"))
