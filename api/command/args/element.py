from typing import List

from discord.enums import SlashCommandOptionType

from api.command.args.arguments import PreparedArguments
from api.command.args.parser import ParserElement
from api.command.mrvn_message_context import MrvnMessageContext


class SingleStringParserElement(ParserElement):
    option = SlashCommandOptionType.string

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        return args.next().value


class IntegerParserElement(ParserElement):
    option = SlashCommandOptionType.integer

    @classmethod
    def parse_value(cls, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        to_parse = args.next().value

        if not to_parse.isdigit():
            raise RuntimeError("Enter an integer")

        return int(to_parse)


parsers = {elem.option: elem for elem in [SingleStringParserElement,
                                          IntegerParserElement] if elem.option}
