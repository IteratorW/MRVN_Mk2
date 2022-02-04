from discord import SelectOption, Interaction
from discord.ui import Select

from api.command import categories
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.view.mrvn_view import MrvnView
from impl import runtime


class Dropdown(Select):
    def __init__(self):
        # Set the options that will be presented inside the dropdown
        options = [
            SelectOption(
                label=Translatable("beu_ext_sex_anal_name"), description=Translatable("beu_ext_sex_anal_desc"),
                emoji="🍑"
            ),
            SelectOption(
                label=Translatable("beu_ext_sex_vaginal_name"), description=Translatable("beu_ext_sex_vaginal_desc"),
                emoji="🐱"
            ),
            SelectOption(
                label=Translatable("beu_ext_sex_oral_name"), description=Translatable("beu_ext_sex_oral_desc"),
                emoji="😱"
            ),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(
            placeholder=Translatable("beu_ext_sex_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        # Use the interaction object to send a response message containing
        # The user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        await interaction.response.send_message(
            f"{self.values[0]}"
        )


class DropdownView(MrvnView):
    def __init__(self, test_str: str, **kwargs):
        super().__init__(timeout=10, **kwargs)
        self.test_str = test_str
        # Adds the dropdown to our view object.
        self.add_item(Dropdown())


@runtime.bot.slash_command(category=categories.debug)
async def dropdown(ctx, anus: str):
    view = DropdownView(tr=ctx, author=ctx.user, test_str=anus)

    await ctx.respond_embed(Style.INFO, ctx.translate("beu_ext_sex_message"), ctx.translate("beu_ext_sex_title"),
                            view=view)
