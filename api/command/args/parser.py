import abc

from api.command.args.arguments import PreparedArguments
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.exc import ArgumentParseException


class ParserElement(abc.ABC):
    option = None

    @classmethod
    def parse(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:

        try:
            value = cls.parse_value(ctx, args)
        except IndexError:
            raise ArgumentParseException.with_pointer("Parser out of range.", args)

        return value

    @classmethod
    @abc.abstractmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        pass

    @classmethod
    def get_display_usage(cls, key: str) -> str:
        return f"<{cls.get_usage(key)}>"

    @classmethod
    def get_usage(cls, key: str) -> str:
        return key
