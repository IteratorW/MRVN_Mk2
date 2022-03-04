from typing import Union

from discord import ButtonStyle, Interaction, Embed, Message, Guild
from discord.abc import Messageable, User
from discord.ui import Button, Item

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from api.view.mrvn_view import MrvnView


class MrvnPaginator(MrvnView):
    def __init__(self, *args, pages: list[Union[str, Embed]] = None, num_pages=None, original_author: User = None,
                 guild: Guild, **kwargs):
        super().__init__(*args, **kwargs)

        self.children: list[Button] = []

        self.pages = pages
        self.num_pages = len(pages) if pages is not None else num_pages
        self.original_author = original_author
        self.guild = guild

        self.page_index = 0

        self.add_item(Button(style=ButtonStyle.blurple, label=Translatable("mrvn_api_views_paginator_button_first")))
        self.add_item(Button(style=ButtonStyle.gray, label=Translatable("mrvn_api_views_paginator_button_prev")))
        self.add_item(Button(style=ButtonStyle.gray, label="N/A", disabled=True))
        self.add_item(Button(style=ButtonStyle.gray, label=Translatable("mrvn_api_views_paginator_button_next")))
        self.add_item(Button(style=ButtonStyle.blurple, label=Translatable("mrvn_api_views_paginator_button_last")))

        self.message = None

    async def get_page_contents(self) -> Union[str, Embed]:
        return self.pages[self.page_index]

    async def update(self):
        page = await self.get_page_contents()
        is_embed = isinstance(page, Embed)

        await self.message.edit(view=self, content=page if not is_embed else None, embed=page if is_embed else None)

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True

        self.children[2].label = self.tr.translate("mrvn_api_views_paginator_button_timeout")

        await self.message.edit(view=self)

    async def callback(self, item: Item, interaction: Interaction):
        if item == self.children[0]:
            self.page_index = 0
        elif item == self.children[1]:
            self.page_index -= 1
        elif item == self.children[3]:
            self.page_index += 1
        elif item == self.children[4]:
            self.page_index = self.num_pages - 1

        self.update_buttons()

        await self.update()

    def update_buttons(self):
        self.children[0].disabled = self.page_index == 0
        self.children[1].disabled = self.page_index == 0

        self.children[2].label = f"{self.page_index + 1}/{self.num_pages}"

        self.children[3].disabled = self.page_index == self.num_pages - 1
        self.children[4].disabled = self.page_index == self.num_pages - 1

    async def attach(self, message: Message):
        self.message = message

        self.update_buttons()

        await self.update()

    async def _send(self, func) -> Message:
        self.update_buttons()

        page = await self.get_page_contents()
        is_embed = isinstance(page, Embed)

        msg = await func(view=self, content=page if not is_embed else None,
                         embed=page if is_embed else None)

        self.message = await msg.original_message() if isinstance(msg, Interaction) else msg

        return self.message

    async def send(self, messageable: Messageable) -> Message:
        return await self._send(messageable.send)

    async def respond_ctx(self, ctx: MrvnCommandContext) -> Message:
        return await self._send(ctx.respond)

    async def respond_interaction(self, interaction: Interaction) -> Message:
        func = interaction.response.send_message if not interaction.response.is_done() else interaction.followup.send

        return await self._send(func)
