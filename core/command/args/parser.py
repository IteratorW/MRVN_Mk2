import abc

from typing import Optional

import core.language as language
from core.command.args.arguments import PreparedArguments
from core.command.context import CommandContext
from core.exception import ArgumentParseException


class ParserElement(abc.ABC):
    key: str

    def __init__(self, key: Optional[str]):
        """
        :param key: Ключ аргумента
        """
        self.key = key

    def parse(self, ctx: CommandContext, args: PreparedArguments):
        """
        Низкоуровневый парсинг аргументов без обработки ошибок
        :param ctx: контекст
        :param args: аргументы
        :return: None
        """
        try:
            value = self.parse_value(ctx, args)
        except IndexError:
            raise ArgumentParseException.with_pointer(language.PARSER_OUT_OF_RANGE, args)
        if self.key is not None and value is not None:
            ctx.put_argument(self.key, value)

    @abc.abstractmethod
    def parse_value(self, ctx: CommandContext, args: PreparedArguments) -> any:
        """
        Парсинг аргументов с обработкой ошибок, в том числе недостатка аргументов
        :param ctx: контекст
        :param args: аргументы
        :return: значение для установки в аргумент
        """
        pass

    def get_display_usage(self) -> str:
        return f"<{self.get_usage()}>"

    @abc.abstractmethod
    def get_usage(self) -> str:
        """
        Строка использования.
        :return: str
        """
        pass
