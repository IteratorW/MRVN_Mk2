from typing import List

from discord.enums import SlashCommandOptionType

from api.command.args.arguments import PreparedArguments
from api.command.args.parser import ParserElement
from api.command.mrvn_message_context import MrvnMessageContext
from api.exc import ArgumentParseException


class SingleStringParserElement(ParserElement):
    option = SlashCommandOptionType.string

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        return args.next().value


class IntegerParserElement(ParserElement):
    option = SlashCommandOptionType.integer

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        try:
            return int(args.next().value)
        except ValueError:
            raise ArgumentParseException.with_pointer(
                "This is not an integer.", args)


parsers = {elem.option: elem for elem in [SingleStringParserElement,
                                          IntegerParserElement] if elem.option}
