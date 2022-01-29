import abc

from api.command.args.arguments import PreparedArguments
from api.command.context.mrvn_message_context import MrvnMessageContext
from api.exc import ArgumentParseException
from api.translation.translator import Translator


class ParserElement(abc.ABC):
    option = None

    @classmethod
    def parse(cls, ctx: MrvnMessageContext, args: PreparedArguments,
              translator: Translator = Translator()) -> any:

        try:
            value = cls.parse_value(ctx, args, translator)
        except IndexError:
            raise ArgumentParseException.with_pointer(translator.translate("mrvn_api_command_parse_out_of_range"), args)

        return value

    @classmethod
    @abc.abstractmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments,
                    translator: Translator = Translator()) -> any:
        pass

    @classmethod
    def get_display_usage(cls, key: str) -> str:
        return f"<{cls.get_usage(key)}>"

    @classmethod
    def get_usage(cls, key: str) -> str:
        return key
