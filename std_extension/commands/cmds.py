import math
from typing import Union

from discord import ButtonStyle, Interaction, Embed
from discord.ui import Button, Item

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translator import Translator
from api.view.mrvn_paginator import MrvnPaginator
from api.view.mrvn_view import MrvnView
from impl import runtime

PAGE_SIZE = 10


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
                                   title=self.ctx.format("std_command_help_embed_title", self.category_name))
        page_commands = self.commands[(self.page_index * PAGE_SIZE):][:PAGE_SIZE]

        for command in page_commands:
            embed.add_field(name=runtime.bot.get_command_desc(command, self.ctx), value=command.description, inline=False)

        return embed


@runtime.bot.slash_command(category=categories.info)
async def cmds(ctx: MrvnCommandContext):
    cat_commands = {}

    for cat in categories.categories:
        cat_commands[cat] = runtime.bot.get_category_commands(cat, ctx.guild_id)

    cat_commands = {k: v for k, v in sorted(cat_commands.items(), key=lambda item: len(item[1]), reverse=True)}

    items = [Button(label=f"{ctx.translate(cat.name)} ({len(items)})", disabled=not len(items),
                    style=ButtonStyle.blurple if len(items) else ButtonStyle.gray) for cat, items in
             cat_commands.items()]

    view = CategoryView(ctx, items, author=ctx.author, timeout=10)

    message = await ctx.respond(ctx.translate("std_command_help_choose_category"), view=view)

    await view.wait()

    if view.category_len is None:
        return

    category, items = list(cat_commands.items())[view.category_len]
    count = len(items)

    num_pages = math.ceil(count / PAGE_SIZE) if count > PAGE_SIZE else 1

    paginator = CmdsPaginator(ctx, items, ctx.translate(category.name), num_pages=num_pages, timeout=30)

    await paginator.attach(message)
