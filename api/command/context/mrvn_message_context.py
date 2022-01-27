from typing import Optional, Union, Callable

from discord import Message, Bot, ApplicationCommand, Guild, Member, InteractionResponse, Interaction, WebhookMessage
from discord.abc import Messageable, User

from api.command.context.mrvn_command_context import MrvnCommandContext


class MrvnMessageContext(MrvnCommandContext):
    # noinspection PyMissingConstructor
    def __init__(self, bot: Bot, message: Message):
        self.bot = bot
        self.interaction = None
        self._message = message

        self.args = {}

    def put_argument(self, key, value):
        self.args[key] = value

    def get_one(self, key):
        return self.args[key]

    async def _get_channel(self) -> Messageable:
        return self.message.channel

    async def invoke(self, command: ApplicationCommand, /, *args, **kwargs):
        return await command(self, *args, **kwargs)

    @property
    def channel(self):
        return self.message.channel

    @property
    def channel_id(self) -> Optional[int]:
        return self.channel.id

    @property
    def guild(self) -> Optional[Guild]:
        return self.message.guild

    @property
    def guild_id(self) -> Optional[int]:
        return self.guild.id

    @property
    def locale(self) -> Optional[str]:
        return None

    @property
    def guild_locale(self) -> Optional[str]:
        return None  # TODO Reimplement for Message

    @property
    def me(self) -> Union[Member, User]:
        return self.guild.me if self.guild is not None else self.bot.user

    @property
    def message(self) -> Optional[Message]:
        return self._message

    @property
    def user(self) -> Optional[Union[Member, User]]:
        return self.message.author

    @property
    def author(self) -> Optional[Union[Member, User]]:
        return self.user

    @property
    def voice_client(self):
        if self.guild is None:
            return None

        return self.guild.voice_client

    @property
    def response(self) -> Union[InteractionResponse, None]:
        return None

    @property
    def respond(self) -> Callable[..., Union[Interaction, WebhookMessage]]:
        return self.message.channel.send

    @property
    def send_response(self):
        return self.respond

    @property
    def send_followup(self):
        return self.respond

    @property
    def defer(self):
        return None  # TODO maybe simulate a deferred message

    @property
    def followup(self):
        return None

    async def delete(self):
        return None  # TODO reimplement

    @property
    def edit(self):
        return self.message.edit
