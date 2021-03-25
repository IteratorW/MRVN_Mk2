from typing import List

from core import CommandContext, language
from core.command.args.arguments import PreparedArguments
from core.command.args.parser import ParserElement
from core.exception import ArgumentParseException


class SequenceParserElement(ParserElement):
    def __init__(self, parsers: List[ParserElement]):
        super().__init__(None)
        self.parsers = parsers

    def parse(self, ctx: CommandContext, args: PreparedArguments):
        for parser in self.parsers:
            parser.parse(ctx, args)

    def parse_value(self, ctx: CommandContext, args: PreparedArguments) -> any:
        return None

    def get_usage(self) -> str:
        return " ".join(parser.get_usage() for parser in self.parsers)


def seq(parsers: List[ParserElement]) -> ParserElement:
    """
    Парсер последовательности парсеров. Каждый переданный парсер парсит по порядку.
    :param parsers: последовательность парсеров
    :return: ParserElement
    """
    return SequenceParserElement(parsers)


class SingleStringParserElement(ParserElement):
    def parse_value(self, ctx: CommandContext, args: PreparedArguments) -> any:
        return args.next()

    def get_usage(self) -> str:
        return self.key


def singleString(key: str) -> ParserElement:
    """
    Просто кусочек строки
    :param key: ключ аргумента
    :return: ParserElement
    """
    return SingleStringParserElement(key)


class ParseUntilEndsParserElement(ParserElement):
    def __init__(self, element: ParserElement, min_count: int = -1):
        super().__init__(None)
        self.element = element
        self.min_count = min_count

    def parse(self, ctx: CommandContext, args: PreparedArguments):
        i = 0
        while args.has_next():
            try:
                value = self.element.parse_value(ctx, args)
            except IndexError:
                break
            if self.element.key is not None and value is not None:
                ctx.put_argument(self.element.key, value)
            i = i + 1
        if i < self.min_count:
            raise ArgumentParseException.with_pointer(
                language.INSUFFICIENT_ARGUMENT_COUNT % (self.element.key, i, self.min_count), args)

    def parse_value(self, ctx: CommandContext, args: PreparedArguments) -> any:
        return None

    def get_usage(self) -> str:
        return f"{self.element.get_usage()}..."


def untilEnds(element: ParserElement, min_count: int = -1) -> ParserElement:
    """
    Парсинг до конца аргументов.
    SequenceParserElement не поддерживается.
    :param min_count: минимальное количество итераций
    :param element: элемент, который будет парсить
    :return: ParserElement
    """
    return ParseUntilEndsParserElement(element, min_count)
