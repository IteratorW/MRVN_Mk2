import datetime
import json
import re
from collections import defaultdict
from typing import Optional

import openai
from discord import Embed

from api.command import categories
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed import styled_embed_generator
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.openai import env
from extensions.openai.ai_commands import parse_and_run_gpt_commands
from extensions.openai.models import SettingSystemMessage, SettingMaxRequestsPerMinute, SettingTemperature, \
    SettingPromptCharLimit, SettingOpenAiMaxHistoryLen, SettingEnableAiCommands
from impl import runtime

last_request_minute = 0
last_minute_request_count = 0

conversation_history: defaultdict[int, list[tuple[str, str]]] = defaultdict(list)
last_message_ids: dict[int, int] = {}


def get_current_minute():
    now = datetime.datetime.now()

    return now.minute


@runtime.bot.slash_command(description=Translatable("openai_command_ai_desc"), category=categories.utility)
async def ai(ctx: MrvnCommandContext, prompt: ParseUntilEndsOption(str)):
    global last_request_minute
    global last_minute_request_count

    max_chars = (await SettingPromptCharLimit.get_or_create())[0].value

    prompt = f"{ctx.author.id}: {prompt}"

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
    history_max_len = (await SettingOpenAiMaxHistoryLen.get_or_create())[0].value
    enable_commands = (await SettingEnableAiCommands.get_or_create())[0].value

    source_id = ctx.guild_id if ctx.guild_id else ctx.author.id

    history = conversation_history[source_id]

    messages = [
        {"role": "system", "content": system_message}
    ]

    for user, assistant in history:
        messages.extend([{"role": "user", "content": user}, {"role": "assistant", "content": assistant}])

    messages.append({"role": "user", "content": prompt})

    await ctx.defer(ephemeral=False)

    try:
        response_text = (await openai.ChatCompletion.acreate(
            model=env.openai_model,
            messages=messages,
            temperature=temperature
        ))["choices"][0]["message"]["content"]
    except openai.error.OpenAIError as ex:
        text = ctx.translate("openai_command_ai_rate_limited") if isinstance(ex, openai.error.RateLimitError) else \
            ctx.format("openai_command_ai_api_error", type(ex).__name__)

        await ctx.respond_embed(Style.ERROR, text)

        return

    last_minute_request_count += 1

    history.append((prompt, response_text))

    if len(history) > history_max_len:
        history.pop(0)

    commands_result = None if not enable_commands else await parse_and_run_gpt_commands(ctx, response_text)

    if commands_result:
        response_text = commands_result[0]

    bot_response = await ctx.respond(
        response_text
        if isinstance(ctx, MrvnMessageContext) else
        ctx.format("openai_command_ai_text_slash", prompt, response_text),
        embed=
        styled_embed_generator.get_embed(Style.INFO, commands_result[1], ctx.translate("openai_ai_commands_title"))
        if commands_result is not None else
        None,
        **({"reference": ctx.message} if isinstance(ctx, MrvnMessageContext) else {})
    )

    last_message_ids[source_id] = bot_response.id


@runtime.bot.slash_command(description=Translatable("openai_command_ai_clear_desc"), category=categories.utility)
async def ai_clear_history(ctx: MrvnCommandContext):
    source_id = ctx.guild_id if ctx.guild_id else ctx.author.id

    if source_id in conversation_history:
        conversation_history[source_id].clear()

    await ctx.respond_embed(Style.INFO, ctx.translate("openai_command_ai_clear_ok"))


@runtime.bot.slash_command(description=Translatable("openai_command_ai_sys_message_desc"), category=categories.utility)
async def ai_system_message(ctx: MrvnCommandContext, new_message: ParseUntilEndsOption(str, default="")):
    setting = (await SettingSystemMessage.get_or_create())[0]

    if not new_message:
        await ctx.respond_embed(Style.INFO, ctx.format("openai_command_ai_sys_message_current",
                                                       setting.value))
    else:
        max_chars = (await SettingPromptCharLimit.get_or_create())[0].value
        
        if len(new_message) > max_chars:
            await ctx.respond_embed(Style.ERROR, ctx.format("openai_command_ai_sys_message_too_long", str(max_chars)))

            return

        setting.value = new_message
        await setting.save()

        source_id = ctx.guild_id if ctx.guild_id else ctx.author.id

        if source_id in conversation_history:
            conversation_history[source_id].clear()

        await ctx.respond_embed(Style.OK,
                                ctx.translate("openai_command_ai_sys_message_success")
                                if isinstance(ctx, MrvnMessageContext) else
                                ctx.format("openai_command_ai_sys_message_success_slash", new_message)
                                )


@runtime.bot.slash_command(description=Translatable("openai_command_ai_history_desc"), category=categories.utility)
async def ai_view_history(ctx: MrvnCommandContext):
    source_id = ctx.guild_id if ctx.guild_id else ctx.author.id

    history = conversation_history[source_id]

    if not len(history):
        await ctx.respond_embed(Style.INFO, ctx.translate("openai_command_history_is_empty"))

        return

    ai_name = ctx.translate("openai_command_history_ai_name")
    user_name = ctx.translate("openai_command_history_user_name")

    history_text = \
        "\n**---**\n".join([f"**{user_name}**: {user}\n**{ai_name}**: {assistant}" for user, assistant in history])

    await ctx.respond_embed(Style.INFO, history_text, ctx.translate("openai_command_history_title"))
