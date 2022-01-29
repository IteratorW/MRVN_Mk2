import discord

from api.embed.style import Style
from impl import runtime


class Dropdown(discord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(
                label="Анальный", description="Ты любишь долбиться в очко", emoji="🍑"
            ),
            discord.SelectOption(
                label="Вагинальный", description="Ты любишь долбиться в пизду", emoji="🐱"
            ),
            discord.SelectOption(
                label="Оральный", description="Ты любишь ебаться в рот", emoji="😱"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder="Секс:",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # The user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(
            f"{self.values[0]} секс"
        )


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


@runtime.bot.slash_command()
async def dropdown(ctx):
    view = DropdownView()

    await ctx.respond_embed(Style.INFO, "Выбери свой любимый вид секса:", "Тест", view=view)
