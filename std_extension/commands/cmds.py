import math
from typing import Union

from discord import ButtonStyle, Interaction, Embed, SlashCommandGroup
from discord.ui import Button, Item

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translator import Translator
from api.view.mrvn_paginator import MrvnPaginator
from api.view.mrvn_view import MrvnView
from impl import runtime

PAGE_SIZE = 5


class CategoryView(MrvnView):
    def __init__(self, tr: Translator, items: list[Item], **kwargs):
        super().__init__(tr, *items, **kwargs)

        self.category_len = None

    async def callback(self, item: Item, interaction: Interaction):
        self.category_len = self.children.index(item)

        self.stop()


class CmdsPaginator(MrvnPaginator):
    def __init__(self, ctx: MrvnCommandContext, commands: list, category_name: str, **kwargs):
        super().__init__(ctx, **kwargs)

        self.commands = commands
        self.category_name = category_name

    async def get_page_contents(self) -> Union[str, Embed]:
        embed = self.ctx.get_embed(Style.INFO,
                                   title=self.ctx.format("builtin_command_help_embed_title", self.category_name))
        page_commands = self.commands[(self.page_index * PAGE_SIZE):][:PAGE_SIZE]

        for command in page_commands:
            embed.add_field(name=runtime.bot.get_command_desc(command, self.ctx), value=command.description, inline=False)

        return embed


@runtime.bot.slash_command(category=categories.info)
async def cmds(ctx: MrvnCommandContext):
    sorted_categories = sorted(categories.categories, key=lambda it: len(it.items), reverse=True)

    items = [Button(label=f"{ctx.translate(x.name)} ({len(x.items)})", disabled=not len(x.items),
                    style=ButtonStyle.blurple if len(x.items) else ButtonStyle.gray) for x in
             sorted_categories]

    view = CategoryView(ctx, items, author=ctx.author, timeout=10)

    message = await ctx.respond(ctx.translate("builtin_command_help_choose_category"), view=view)

    await view.wait()

    if view.category_len is None:
        return

    category = sorted_categories[view.category_len]
    count = len(category.items)

    num_pages = math.ceil(count / PAGE_SIZE) if count > PAGE_SIZE else 1

    paginator = CmdsPaginator(ctx, category.get_all_commands(), ctx.translate(category.name), num_pages=num_pages, timeout=30)

    await paginator.attach(message)
