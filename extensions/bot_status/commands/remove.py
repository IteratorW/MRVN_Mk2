from discord import Interaction, ButtonStyle
from discord.ui import Item, Button

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.translation.translator import Translator
from api.view.mrvn_view import MrvnView
from extensions.bot_status import status_update
from extensions.bot_status.commands.bot_status import bot_status_group
from extensions.bot_status.models import BotStatusEntry


class EntriesView(MrvnView):
    def __init__(self, tr: Translator, entries: list[BotStatusEntry], **kwargs):
        items = [Button(style=ButtonStyle.danger, label=x.text) for x in entries]

        super().__init__(tr, *items, **kwargs)

        self.entries = entries
        self.message = None

    async def callback(self, item: Item, interaction: Interaction):
        if not isinstance(item, Button):
            return

        item_len = self.children.index(item)

        await self.entries[item_len].delete()

        status_update.start_task()

        item.style = ButtonStyle.gray
        item.disabled = True

        await self.message.edit(view=self)

    async def respond(self, ctx: MrvnCommandContext):
        self.message = await ctx.respond_embed(Style.INFO,
                                               title=ctx.translate("bot_status_command_remove_choose_status"),
                                               view=self)


@bot_status_group.command(description=Translatable("bot_status_command_remove_desc"))
async def remove(ctx: MrvnCommandContext):
    entries = await BotStatusEntry.filter()

    if not len(entries):
        await ctx.respond_embed(Style.ERROR, ctx.translate("bot_status_command_remove_no_entries"))

        return

    view = EntriesView(ctx, await BotStatusEntry.filter(), timeout=40)

    await view.respond(ctx)
