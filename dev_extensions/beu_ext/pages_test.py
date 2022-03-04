from typing import Union

from discord import Embed
from discord.commands import permissions

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.view.mrvn_paginator import MrvnPaginator
from impl import runtime


class CustomPaginator(MrvnPaginator):
    async def get_page_contents(self) -> Union[str, Embed]:
        return f"Beu page {self.page_index}"


@runtime.bot.command(category=categories.debug)
@permissions.is_owner()
async def pages_test(ctx: MrvnCommandContext):
    await ctx.respond("Test")

    paginator = CustomPaginator(ctx, num_pages=10, timeout=10, guild=ctx.guild)
    await paginator.respond_ctx(ctx)
