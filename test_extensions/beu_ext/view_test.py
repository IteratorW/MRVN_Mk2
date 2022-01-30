import discord

from api.embed.style import Style
from api.view.mrvn_view import MrvnView
from impl import runtime


class DropdownView(MrvnView):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


@runtime.bot.slash_command()
async def dropdown(ctx):
    view = DropdownView()

    await ctx.respond_embed(Style.INFO, "Выбери свой любимый вид секса:", "Тест", view=view)