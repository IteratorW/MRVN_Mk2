from io import BytesIO
from typing import Union

import aiohttp
import openai
from discord import Embed, File

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed import styled_embed_generator
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.view.mrvn_paginator import MrvnPaginator
from impl import runtime


class ImGenPaginator(MrvnPaginator):
    def __init__(self, urls: list[str], *args, **kwargs):
        self.urls = urls

        super().__init__(num_pages=len(urls), *args, **kwargs)

    async def get_page_contents(self) -> Union[str, Embed]:
        embed = styled_embed_generator.get_embed(Style.INFO, title=self.tr.translate("openai_command_imgen_title"),
                                                 author=self.original_author, guild=self.guild)
        embed.set_image(url=self.urls[self.page_index])

        return embed

    async def on_timeout(self) -> None:
        await super().on_timeout()

        async with aiohttp.ClientSession() as session:
            async with session.get(self.urls[self.page_index]) as resp:
                image = BytesIO(await resp.read())

        file = File(image, "imgen_final_image.png")

        embed = self.message.embeds[0]

        embed.set_image(url="attachment://imgen_final_image.png")

        await self.message.edit(embed=embed, file=file)


@runtime.bot.slash_command(description=Translatable("openai_command_imgen_desc"), categories=categories.utility)
async def imgen(ctx: MrvnCommandContext, prompt: ParseUntilEndsOption(str)):
    await ctx.defer()

    try:
        urls = [x["url"] for x in (await openai.Image.acreate(prompt=prompt, n=10, size="1024x1024"))["data"]]
    except openai.OpenAIError as ex:
        await ctx.respond_embed(Style.ERROR, ctx.format("openai_command_ai_api_error", str(ex)))
        return

    paginator = ImGenPaginator(urls, guild=ctx.guild, original_author=ctx.author, tr=ctx, timeout=30)

    await paginator.respond_ctx(ctx)
