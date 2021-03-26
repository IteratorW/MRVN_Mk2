__all__ = [
    "seq",
    "singleString",
    "untilEnds",
    "NONE"
]

import os
import logging
import core.language as language

from typing import List

from core.command.context import CommandContext
from core.command.args.arguments import PreparedArguments
from core.command.args.parser import ParserElement
from core.exception import ArgumentParseException

logger = logging.getLogger("Arguments")
debug = bool(os.environ.get("DEBUG") or "true")

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

NONE = seq([])

class SingleStringParserElement(ParserElement):
    def parse_value(self, ctx: CommandContext, args: PreparedArguments) -> any:
        return args.next().value

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
    Поддерживаются только парсеры одиночного аргумента.
    :param min_count: минимальное количество итераций
    :param element: элемент, который будет парсить
    :return: ParserElement
    """
    if debug:
        # Дебаг для долбаёба, который не смотрел в докстринг, когда писал код
        import dis
        instructions = dis.get_instructions(element.parse_value)
        step = 0
        for instruction in instructions:
            if step == 0:
                if instruction.opname == "LOAD_FAST" and instruction.argval == "args":
                    step = 1
            elif step == 1:
                if instruction.opname == "LOAD_METHOD" and instruction.argval == "next":
                    step = 2
                else:
                    step = 0
            elif step == 2:
                if instruction.opname == "CALL_METHOD":
                    break
                else:
                    step = 0
        if step == 0:
            import traceback
            logger.warning("ParseUntilEndsParserElement used with ParserElement without args.next() in parse_value")
            logger.warning("Stacktrace: ")
            for line in traceback.extract_stack().format():
                logger.warning(line)


    # if dis.Bytecode(element.parse_value).codeobj.co_code == b'd\x00S\x00':
    #     # Дизассемблированный код
    #     # 28           0 LOAD_CONST               0 (None)
    #     #              2 RETURN_VALUE
    #     # Или просто
    #     # def parse_value(self, ctx: CommandContext, args: PreparedArguments) -> any:
    #     #     pass
    #     raise RuntimeError("В докстринге блять написано - поддерживаются только парсеры одиночного аргумента, еблан ты тупой")

    return ParseUntilEndsParserElement(element, min_count)
