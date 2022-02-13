import asyncio
import math
from typing import Union

from aiohttp import ClientSession, ClientTimeout, ClientConnectionError
from discord import Embed

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed import styled_embed_generator
from api.embed.style import Style
from api.view.mrvn_paginator import MrvnPaginator
from extensions.search import env
from extensions.search.cse.search_item import SearchItem
from extensions.search.cse.search_type import SearchType
from extensions.search.models import SettingEnableSafeSearch

GOOGLE_PAGE_SIZE = 2
ITEMS_NUM = 10


class CSEPaginator(MrvnPaginator):
    def __init__(self, query: str, results: list[SearchItem], search_type: SearchType, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query = query
        self.results = results
        self.search_type = search_type

    async def get_page_contents(self) -> Union[str, Embed]:
        if self.search_type == SearchType.YOUTUBE:
            video_url = self.results[self.page_index].url

            return f"{self.tr.format('search_command_yt_title', self.query)}\n{video_url}"
        else:
            if self.search_type == SearchType.GOOGLE:
                page_results = self.results[(self.page_index * GOOGLE_PAGE_SIZE):][:GOOGLE_PAGE_SIZE]

                embed = styled_embed_generator.get_embed(Style.INFO, title=self.tr.format("search_command_google_title",
                                                                                          self.query),
                                                         author=self.original_author)

                for result in page_results:
                    embed.add_field(name=result.title, value=f"[{result.snippet}]({result.url})", inline=False)
            else:
                image = self.results[self.page_index]

                embed = styled_embed_generator.get_embed(Style.INFO,
                                                         title=self.tr.format("search_command_img_title", self.query),
                                                         author=self.original_author)
                embed.set_image(url=image.url)
                embed.set_author(name=image.title, url=image.context_url)

            return embed


async def search(ctx: MrvnCommandContext, q: str, search_type: SearchType):
    if not env.cse_cx or not env.cse_api_key:
        await ctx.respond_embed(Style.ERROR, ctx.translate("search_command_img_api_data_missing"))

        return

    await ctx.defer()

    safe = "active" if ctx.guild_id and (await SettingEnableSafeSearch.get_or_create(guild_id=ctx.guild_id))[
        0].value else "off"

    session = ClientSession(timeout=ClientTimeout(20))

    params = {"q": q, "num": ITEMS_NUM, "start": 1,
              "key": env.cse_api_key,
              "cx": env.cse_cx,
              "safe": safe}

    params.update(search_type.value)

    try:
        response = await session.get("https://www.googleapis.com/customsearch/v1",
                                     params=params)
    except (asyncio.TimeoutError, ClientConnectionError):
        await ctx.respond_embed(Style.ERROR, ctx.translate("search_connection_error"))

        return

    data = await response.json()

    await session.close()
    response.close()

    if response.status != 200:
        if data["error"]["status"] == "RESOURCE_EXHAUSTED":
            await ctx.respond_embed(Style.ERROR, ctx.translate("search_command_resource_exhausted"))
        else:
            await ctx.respond_embed(Style.ERROR, ctx.format("search_command_api_error", data["error"]["status"]))

        return

    if data["searchInformation"]["totalResults"] == "0":
        await ctx.respond_embed(Style.ERROR, ctx.format("search_command_not_found", q))

        return

    items = [
        SearchItem(x["title"], x["link"], x["image"]["contextLink"] if search_type == SearchType.IMAGES else x["link"],
                   x["snippet"]) for x in data["items"]]

    count = len(items)

    if search_type == SearchType.GOOGLE:
        num_pages = math.ceil(count / GOOGLE_PAGE_SIZE) if count > GOOGLE_PAGE_SIZE else 1
    else:
        num_pages = count

    paginator = CSEPaginator(q, items, search_type, tr=ctx, author=ctx.author,
                             original_author=None if ctx.interaction else ctx.author, timeout=30,
                             num_pages=num_pages)

    await paginator.respond_ctx(ctx)
