from discord import ui, InputTextStyle, Interaction, ButtonStyle

from api.command.mrvn_context import MrvnContext
from api.embed import styled_embed_generator
from api.embed.style import Style
from impl import runtime


class TestModal(ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            ui.InputText(
                label="Short Input",
                placeholder="Placeholder Test",
            ),
            ui.InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=InputTextStyle.long,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: Interaction):
        embed = styled_embed_generator.get_embed(Style.INFO, f"First: {self.children[0].value}\nSecond: {self.children[1].value}")
        await interaction.response.send_message(embed=embed)


@runtime.bot.mrvn_command()
async def test_modal(ctx: MrvnContext):
    class TestView(ui.View):
        @ui.button(label="Modal Test", style=ButtonStyle.primary)
        async def button_callback(
                self, button: ui.Button, interaction: Interaction
        ):
            modal = TestModal(title="Prolapse")
            await interaction.response.send_modal(modal)

    await ctx.respond("Beu", view=TestView())
