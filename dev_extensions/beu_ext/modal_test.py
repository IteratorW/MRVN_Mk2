from discord import InputTextStyle, Interaction, Embed, Color, ui, ButtonStyle
from discord.ui import InputText, View

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.modal.mrvn_modal import MrvnModal
from impl import runtime


class MyModal(MrvnModal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Short Input", placeholder="Placeholder Test"))

        self.add_item(
            InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=InputTextStyle.long,
            )
        )

    async def callback(self, interaction: Interaction):
        embed = Embed(title="Your Modal Results", color=Color.random())
        embed.add_field(name="First Input", value=self.children[0].value, inline=False)
        embed.add_field(name="Second Input", value=self.children[1].value, inline=False)
        await interaction.response.send_message(embeds=[embed])


@runtime.bot.slash_command()
async def modal(ctx: MrvnCommandContext):
    class MyView(View):
        @ui.button(label="Modal Test", style=ButtonStyle.primary)
        async def button_callback(self, button, interaction):
            modal = MyModal(title="Test modal")
            await interaction.response.send_modal(modal)

    view = MyView()
    await ctx.respond_embed(Style.INFO, "Click to test modal", view=view)
