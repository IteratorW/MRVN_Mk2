from api.command.context.mrvn_message_context import MrvnMessageContext
from api.event_handler.decorators import event_handler
from discord import Message

from api.embed.style import Style
from api.translation import translations
from extensions.openai.commands import ai
from impl import runtime


@event_handler()
async def on_message(message: Message):
    if message.author.bot or not message.reference:
        return

    source_id = message.guild.id if message.guild else message.author.id

    last_ai_message_id = ai.last_message_ids.get(source_id, None)

    if not last_ai_message_id or last_ai_message_id != message.reference.message_id:
        return

    # We're basically running !ai command here

    ctx = MrvnMessageContext(runtime.bot, message)

    if message.guild:
        await ctx.set_from_guild(message.guild.id)
    else:
        ctx.set_lang(translations.FALLBACK_LANGUAGE)

    # noinspection PyBroadException
    try:
        await ai.ai(ctx, message.content)
    except Exception:
        await ctx.respond_embed(Style.ERROR, ctx.translate("openai_reply_command_error"), reference=message)
