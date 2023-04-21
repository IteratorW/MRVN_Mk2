import asyncio
import datetime
import json
import re
import traceback
from typing import Optional

from aiohttp import ClientConnectionError, ClientSession, ClientTimeout
from discord import Embed

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.extensions import extension_manager


async def parse_and_run_gpt_commands(ctx: MrvnCommandContext, response_text: str) -> Optional[tuple[str, str]]:
    commands = re.findall(r"##GPT (.+?)##", response_text)

    if not len(commands):
        return

    command_desc_list = []

    for command in commands:
        response_text = response_text.replace(f"##GPT {command}##", "")

        try:
            args = command.split()

            if len(args) < 2:
                continue

            name = args.pop(0)

            if name == "MUTE":
                if not ctx.guild_id:
                    continue

                user_id = int(args.pop(0))
                member = ctx.guild.get_member(user_id)
                reason = " ".join(args)

                until = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

                await member.timeout(until=until, reason=reason)

                command_desc_list.append(ctx.format("openai_command_ai_command_mute", member.mention, "15", reason))
            elif name == "CH":
                name = " ".join(args)

                channel = await ctx.channel.category.create_text_channel(name)

                command_desc_list.append(ctx.format("openai_command_ai_command_channel", channel.mention))
            elif name == "NAME":
                if not ctx.guild_id:
                    continue

                new_name = " ".join(args)

                await ctx.guild.edit(name=new_name)

                command_desc_list.append(ctx.format("openai_command_ai_command_server_name", new_name))
            elif name == "MSG":
                await ctx.respond(" ".join(args))

                command_desc_list.append(ctx.translate("openai_command_ai_command_msg"))
            elif name == "EMB":
                await ctx.respond(embed=Embed.from_dict(json.loads(" ".join(args))))

                command_desc_list.append(ctx.translate("openai_command_ai_command_emb"))
            elif name == "IMG":
                query = " ".join(args)

                result_url = await picture_search(query)

                if not result_url:
                    command_desc_list.append(ctx.translate("openai_command_ai_command_image_failed"))

                    continue

                await ctx.respond(result_url)

                command_desc_list.append(ctx.format("openai_command_ai_command_image", query))
            elif name == "NICK":
                user_id = int(args.pop(0))
                nick = " ".join(args)

                await ctx.guild.get_member(user_id).edit(nick=nick)

                command_desc_list.append(ctx.format("openai_command_ai_command_nick", nick))
            else:
                command_desc_list.append(ctx.format("openai_command_ai_command_unknown", command))
        except Exception as e:
            print(traceback.format_exc())
            command_desc_list.append(ctx.format("openai_command_ai_command_error", type(e).__name__))

    return (response_text, "\n".join(command_desc_list)) if len(command_desc_list) else None


async def picture_search(query: str) -> Optional[str]:
    if "search" not in extension_manager.extensions:
        return None

    import extensions.search.env as senv

    if not (senv.cse_cx is not None and senv.cse_api_key is not None):
        return None

    session = ClientSession(timeout=ClientTimeout(20))

    params = {"q": query, "num": 1, "start": 1,
              "key": senv.cse_api_key,
              "cx": senv.cse_cx,
              "safe": "off",
              "searchType": "image"}

    try:
        response = await session.get("https://www.googleapis.com/customsearch/v1",
                                     params=params)
    except (asyncio.TimeoutError, ClientConnectionError):
        return None

    data = await response.json()

    await session.close()
    response.close()

    if response.status != 200:
        return None

    if data["searchInformation"]["totalResults"] == "0":
        return None

    return data["items"][0]["link"]
