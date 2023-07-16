import asyncio
import tempfile
from io import BytesIO

from discord import Option, Attachment, File
from PIL import Image
from braillert import generator, colors
from braillert.main import _resize_portrait

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime

@runtime.bot.slash_command(description=Translatable("fun_stuff_command_ita_desc"))
async def ita(ctx: MrvnCommandContext, image: Option(Attachment), palette: Option(str, choices=[i for i in colors.AvailableColors]) = colors.AvailableColors.GRAYSCALE, width: Option(int) = 100):
    if not image.content_type.startswith("image"):
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_ita_invalid_content_type"))

        return

    await ctx.defer()

    image_bytes = BytesIO()
    await image.save(image_bytes)

    image_bytes.seek(0)
    image_object = _resize_portrait(Image.open(image_bytes), width)

    art_generator = generator.Generator(image_object, colors.AvailableColors(palette))

    result = await asyncio.get_event_loop().run_in_executor(None, art_generator.generate_art)

    if not result:
        await ctx.respond_embed(Style.ERROR, ctx.translate("fun_stuff_command_ita_fail"))

        return

    with tempfile.TemporaryFile() as fp:
        fp.write(result.encode("utf-8"))
        fp.seek(0)
        await ctx.respond(file=File(fp, "message.ansi"))
    
