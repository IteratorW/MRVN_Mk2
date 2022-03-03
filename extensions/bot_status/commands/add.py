from discord import Option, OptionChoice

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from extensions.bot_status import status_update
from extensions.bot_status.commands.bot_status import bot_status_group
from extensions.bot_status.models import BotStatusEntry

ENTRIES_LIMIT = 5


@bot_status_group.command(description=Translatable("bot_status_command_add_desc"))
async def add(ctx: MrvnCommandContext,
              status: Option(str, choices=[
                  OptionChoice("Online", "online"),
                  OptionChoice("Invisible", "invisible"),
                  OptionChoice("Idle", "idle"),
                  OptionChoice("Do Not Disturb", "dnd")
              ]),
              activity: Option(str, choices=[
                  OptionChoice("Playing", "playing"),
                  OptionChoice("Streaming", "streaming"),
                  OptionChoice("Listening", "listening"),
                  OptionChoice("Watching", "watching"),
                  OptionChoice("Competing", "competing")
              ]),
              text: ParseUntilEndsOption(str)):
    if len(await BotStatusEntry.filter()) == ENTRIES_LIMIT:
        await ctx.respond_embed(Style.ERROR, ctx.translate("bot_status_command_add_limit_reached"))

        return
    elif len(text) > 50:
        await ctx.respond_embed(Style.ERROR, ctx.translate("bot_status_command_add_text_too_long"))

        return

    await BotStatusEntry.create(status=status, activity=activity.lower(), text=text)

    status_update.start_task()

    await ctx.respond_embed(Style.OK, ctx.translate("bot_status_command_add_status_added"))
