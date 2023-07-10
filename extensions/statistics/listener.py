from discord import Message

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.event_handler.decorators import event_handler
from extensions.statistics.models import StatsCommandEntry, StatsUserCommandsEntry, StatsDailyGuildChannelMessages, \
    StatsChannelMessageTimestamp


@event_handler()
async def on_application_command_completion(ctx: MrvnCommandContext):
    if not ctx.guild_id:
        return

    command_entry = \
        (await StatsCommandEntry.get_or_create(guild_id=ctx.guild_id, command_name=ctx.command.qualified_name))[0]
    user_entry = (await StatsUserCommandsEntry.get_or_create(guild_id=ctx.guild_id, user_id=ctx.author.id))[0]

    command_entry.increment()
    user_entry.increment()

    await command_entry.save()
    await user_entry.save()


@event_handler()
async def on_message(message: Message):
    if not message.guild:
        return

    await StatsChannelMessageTimestamp.create(guild_id=message.guild.id, channel_id=message.channel.id,
                                              timestamp=message.created_at)

    entry = await StatsDailyGuildChannelMessages.get_for_now(message.guild.id, message.channel.id)

    entry.increment()

    await entry.save()
