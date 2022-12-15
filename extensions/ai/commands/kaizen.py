import logging
import os.path
import random
from typing import Optional

from discord import ButtonStyle, Interaction
from discord.ui import Button, Item

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from api.view.mrvn_view import MrvnView
from extensions.ai import category
from extensions.ai.models import AiTextModel
from impl import runtime

AI_FOLDER = "ai"
AI_FILES = [f"./{AI_FOLDER}/pytorch_model.bin", f"./{AI_FOLDER}/config.json", f"./{AI_FOLDER}/aitextgen.tokenizer.json"]

logger = logging.getLogger("Kaizen AI")

for file in AI_FILES:
    if not os.path.isfile(file):
        logger.error(f"AI file {file} doesn't exist - the model is not loaded.")

        ai = None
        break
else:
    from aitextgen import aitextgen

    ai = aitextgen(model_folder=AI_FOLDER, tokenizer_file=f"./{AI_FOLDER}/aitextgen.tokenizer.json")


async def generate_text(prompt: str) -> Optional[AiTextModel]:
    if ai is None:
        return None

    seed = random.getrandbits(32)
    temp = random.uniform(0, 2)

    # aitextgen is shit bruh. It does return a string as stated in the docstring.
    # noinspection PyNoneFunctionAssignment,PyTypeChecker
    text: str = ai.generate_one(temperature=temp, seed=seed, prompt=prompt)
    text = text.lstrip().rstrip()

    return await AiTextModel.create(seed=seed, text=text, temperature=temp)


class AiMessageView(MrvnView):
    def __init__(self, ctx: MrvnCommandContext, text_model: AiTextModel, **kwargs):
        super().__init__(ctx, timeout=None, **kwargs)
        self.text_model = text_model

        self.message = None

        self.add_item(Button(emoji="👎", label=" 0", custom_id=f"{self.text_model.seed}_0"))
        self.add_item(Button(emoji="👍", label=" 0", custom_id=f"{self.text_model.seed}_1"))

    async def respond(self, ctx: MrvnCommandContext):
        embed = ctx.get_embed(Style.INFO, desc=self.text_model.text, title=ctx.translate("ai_command_title"))
        embed.colour = 0x0ABAB5
        embed.set_footer(text=f"Seed: {self.text_model.seed} | Temp: {self.text_model.temperature}")

        self.message = await ctx.respond(embed=embed, view=self)

    async def callback(self, item: Item, interaction: Interaction):
        custom_id = interaction.custom_id.split("_")
        seed = custom_id[0]
        like = custom_id[1] == "1"

        text_model = await AiTextModel.get_or_none(seed=seed)

        if not text_model:
            return

        reacted = text_model.react(interaction.user.id, like)

        if reacted:
            self.children[0].label = str(len(text_model.dislikes))
            self.children[1].label = str(len(text_model.likes))

            await text_model.save()

        await self.message.edit(view=self)


@runtime.bot.slash_command(description=Translatable("ai_command_kaizen_desc"), category=category.ai)
async def kz(ctx: MrvnCommandContext, prompt: ParseUntilEndsOption(str, default="")):
    text_model = await generate_text(prompt)

    if not text_model:
        await ctx.respond_embed(Style.ERROR, ctx.translate("ai_command_model_not_loaded"))

        return

    view = AiMessageView(ctx, text_model)

    await view.respond(ctx)

