import datetime

import openai

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.openai.models import SettingSystemMessage, SettingMaxRequestsPerMinute, SettingTemperature, \
    SettingPromptCharLimit
from impl import runtime

last_request_minute = 0
last_minute_request_count = 0


def get_current_minute():
    now = datetime.datetime.now()

    return now.minute


@runtime.bot.slash_command(description=Translatable("openai_command_ai_desc"), category=categories.utility)
async def ai(ctx: MrvnCommandContext, prompt: ParseUntilEndsOption(str)):
    global last_request_minute
    global last_minute_request_count

    max_chars = (await SettingPromptCharLimit.get_or_create())[0].value

    if len(prompt) > max_chars:
        await ctx.respond_embed(Style.ERROR, ctx.format("openai_command_ai_char_limit", str(max_chars)))

        return

    max_requests = (await SettingMaxRequestsPerMinute.get_or_create())[0].value

    if last_minute_request_count >= max_requests and last_request_minute == get_current_minute():
        await ctx.respond_embed(Style.ERROR, ctx.format("openai_command_ai_max_requests_reached", str(max_requests)))

        return
    elif last_request_minute != get_current_minute():
        last_request_minute = get_current_minute()
        last_minute_request_count = 0

    system_message = (await SettingSystemMessage.get_or_create())[0].value
    temperature = (await SettingTemperature.get_or_create())[0].value

    await ctx.defer(ephemeral=False)

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
    except openai.error.OpenAIError as ex:
        text = ctx.translate("openai_command_ai_rate_limited") if isinstance(ex, openai.error.RateLimitError) else \
            ctx.format("openai_command_ai_api_error", ex.__name__)

        await ctx.respond_embed(Style.ERROR, text)

        return

    last_minute_request_count += 1

    await ctx.respond_embed(Style.INFO, response["choices"][0]["message"]["content"],
                            ctx.translate("openai_command_ai_success"))
