import openai
from discord import SelectOption, Interaction
from discord.ui import Select

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.view.mrvn_view import MrvnView
from extensions.openai.models import SettingAiModel
from impl import runtime


class Dropdown(Select):
    def __init__(self, models: list[str]):
        options = [SelectOption(label=x, emoji="📃") for x in models]

        super().__init__(
            placeholder=Translatable("openai_command_ai_change_model_select_placeholder"),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction):
        await SettingAiModel.all().update(value_field=self.values[0])

        await interaction.message.edit(content=self.view.tr.format("openai_command_ai_change_model_select_done",
                                                                   self.values[0]), view=None)


class DropdownView(MrvnView):
    def __init__(self, models: list[str], **kwargs):
        super().__init__(timeout=10, **kwargs)
        self.add_item(Dropdown(models))


@runtime.bot.slash_command(description=Translatable("openai_command_ai_change_model_desc"), categories=categories.utility)
async def ai_change_model(ctx: MrvnCommandContext):
    try:
        models = [x["id"] for x in (await openai.Model.alist())["data"] if "/api/v1/chat/completions" in x["endpoints"]]
    except openai.OpenAIError as ex:
        await ctx.respond_embed(Style.ERROR, ctx.format("openai_command_ai_api_error", str(ex)))
        return

    if not len(models):
        await ctx.respond_embed(Style.ERROR, ctx.translate("openai_command_ai_change_model_no_models_available"))
        return

    await ctx.respond(ctx.translate("openai_command_ai_change_model_choose_the_model"
                                    ""), view=DropdownView(models, tr=ctx))
