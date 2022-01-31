from typing import Union

from discord import Embed
from discord.commands import permissions
from discord.ext.pages import Paginator

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.view.mrvn_paginator import MrvnPaginator
from impl import runtime


class CustomPaginator(MrvnPaginator):
    async def get_page_contents(self) -> Union[str, Embed]:
        return f"Beu page {self.page_index}"


@runtime.bot.command()
@permissions.is_owner()
async def pages_test(ctx: MrvnCommandContext):
    await ctx.respond("Test")

    paginator = CustomPaginator(ctx, num_pages=10, timeout=10)
    await paginator.respond()
