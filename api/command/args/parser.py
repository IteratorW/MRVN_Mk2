import abc

from typing import Optional

from api.command.args.arguments import PreparedArguments
from api.command.mrvn_message_context import MrvnMessageContext


class ParserElement(abc.ABC):
    option = None

    @classmethod
    def parse(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:

        try:
            value = cls.parse_value(ctx, args)
        except IndexError:
            raise RuntimeError("Parser out of rng")

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
