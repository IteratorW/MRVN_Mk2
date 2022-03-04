import asyncio
from typing import Union

from aiohttp import ClientSession, ClientTimeout, ClientConnectionError
from discord import Embed, Interaction
from discord.ui import Item
from markdownify import markdownify

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed import styled_embed_generator
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.view.mrvn_paginator import MrvnPaginator
from extensions.search.commands.category import search_category
from impl import runtime


class WikiPaginator(MrvnPaginator):
    def __init__(self, wiki_lang: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, item: Item, interaction: Interaction):
        await interaction.response.defer()

        await super().callback(item, interaction)

    async def get_page_contents(self) -> Union[str, Embed]:
        title = self.pages[self.page_index]

        session = ClientSession(timeout=ClientTimeout(20))

        params = {"action": "query",
                  "prop": "extracts",
                  "titles": title,
                  "format": "json",
                  "exintro": "true",
                  "explainttext": "true"}

        try:
            response = await session.get("https://ru.wikipedia.org/w/api.php",
                                         params=params)
        except (asyncio.TimeoutError, ClientConnectionError):
            return styled_embed_generator.get_embed(Style.ERROR, self.tr.translate("search_connection_error"))

        data = await response.json()

        await session.close()
        response.close()

        pages = data["query"]["pages"]
        text = data["query"]["pages"][next(iter(pages))]["extract"]
        text = markdownify(text, strip=["img"])

        embed = styled_embed_generator.get_embed(Style.INFO, text, title=title, author=self.original_author,
                                                 guild=self.guild)

        return embed


@runtime.bot.slash_command(category=search_category, description=Translatable("search_command_wiki_desc"))
async def wiki(ctx: MrvnCommandContext, query: ParseUntilEndsOption(str)):
    await ctx.defer()

    session = ClientSession(timeout=ClientTimeout(20))

    params = {"action": "query",
              "format": "json",
              "list": "search",
              "srsearch": query}

    try:
        response = await session.get("https://ru.wikipedia.org/w/api.php",
                                     params=params)
    except (asyncio.TimeoutError, ClientConnectionError):
        await ctx.respond_embed(Style.ERROR, ctx.translate("search_connection_error"))

        return

    data = await response.json()

    await session.close()
    response.close()

    items = [x["title"] for x in data["query"]["search"]]

    if not len(items):
        await ctx.respond_embed(Style.ERROR, ctx.format("search_command_not_found", query))

        return

    paginator = WikiPaginator("ru", tr=ctx, author=ctx.author, original_author=ctx.author, timeout=30, pages=items,
                              guild=ctx.guild)

    await paginator.respond_ctx(ctx)
