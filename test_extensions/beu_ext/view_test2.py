from discord import ButtonStyle, Interaction
from discord.ui import Button, Item

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translator import Translator
from api.view.mrvn_view import MrvnView
from impl import runtime


class KeyboardView(MrvnView):
    def __init__(self, ctx: MrvnCommandContext, **kwargs):
        super().__init__(ctx, **kwargs)

        self.ctx = ctx
        self.message = None

        for i in range(1, 10):
            if 3 < i <= 6:
                row = 1
            elif i > 6:
                row = 2
            else:
                row = 0

            self.add_item(Button(label=str(i), style=ButtonStyle.gray, row=row))

        self.add_item(Button(emoji="❌", row=3, style=ButtonStyle.red))
        self.add_item(Button(label="0", style=ButtonStyle.gray, row=3))
        self.add_item(Button(emoji="✅", row=3, style=ButtonStyle.green))

        self.code = ""

    async def callback(self, item: Item, interaction: Interaction):
        number = str(self.children.index(item) + 1)

        if number == "10":
            self.code = ""
        elif number == "12":
            if self.code in ["8665788965", "0451"]:
                self.code = "[Code valid! +50 social credits!!!!]"
            else:
                self.code = "[Code invalid! -50000 social credits!!!!! Execution date: yesterday....]"
        else:
            if number == "11":
                number = "0"

            self.code += number

        await self.message.edit(self.code if len(self.code) else f"[Start entering code ({interaction.user.mention})]", view=self)

        if number == "12":
            self.stop()

    async def respond(self):
        msg = await self.ctx.respond("[Start entering code]", view=self)

        if isinstance(msg, Interaction):
            msg = await msg.original_message()

        self.message = msg


@runtime.bot.slash_command()
async def keyboard(ctx: MrvnCommandContext):
    view = KeyboardView(ctx)

    await view.respond()
