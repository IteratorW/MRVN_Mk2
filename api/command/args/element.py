import logging
import os
from typing import List

from discord.enums import SlashCommandOptionType

from api.command.args.arguments import PreparedArguments
from api.command.args.parser import ParserElement
from api.command.mrvn_message_context import MrvnMessageContext

logger = logging.getLogger("Arguments")
debug = bool(os.environ.get("mrvn_debug") or "true")


class SequenceParserElement(ParserElement):
    def __init__(self, parsers: List[ParserElement]):
        super().__init__(None)
        self.parsers = parsers

    def parse(self, ctx: MrvnMessageContext, args: PreparedArguments):
        for parser in self.parsers:
            parser.parse(ctx, args)

    def parse_value(self, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        return None

    def get_display_usage(self) -> str:
        return " ".join(parser.get_display_usage() for parser in self.parsers)

    def get_usage(self) -> str:
        return ""


def seq(parsers: List[ParserElement]) -> ParserElement:
    """
    Парсер последовательности парсеров. Каждый переданный парсер парсит по порядку.
    :param parsers: последовательность парсеров
    :return: ParserElement
    """
    return SequenceParserElement(parsers)


NONE = seq([])


class SingleStringParserElement(ParserElement):
    option = SlashCommandOptionType.string

    def parse_value(self, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        return args.next().value

    def get_usage(self) -> str:
        return self.key


class IntegerParserElement(ParserElement):
    def get_usage(self) -> str:
        return self.key

    option = SlashCommandOptionType.integer

    def parse_value(self, ctx: MrvnMessageContext, args: PreparedArguments) -> any:
        to_parse = args.next().value

        if not to_parse.isdigit():
            raise RuntimeError("Enter an integer")

        return int(to_parse)


parsers = {elem.option: elem for elem in [SingleStringParserElement,
                                          IntegerParserElement] if elem.option}
