import discord
from discord import Message

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.event_handler.decorators import event_handler
from extensions.statistics.models import StatsCommandEntry, StatsUserCommandsEntry, \
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

    # PyCharm thinks `message.clean_content` is a function. It's a property tho.
    # noinspection PyTypeChecker
    await StatsChannelMessageTimestamp.create(guild_id=message.guild.id, channel_id=message.channel.id,
                                              timestamp=message.created_at, user_id=message.author.id,
                                              text=discord.utils.remove_markdown(message.clean_content),
                                              embeds=[x.to_dict() for x in message.embeds])
