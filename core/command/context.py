__all__ = [
    "CommandContext",
    "PermissionContext"
]

import abc
import discord

from collections import defaultdict
from typing import Dict, List, Union, Type, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.command.specification import CommandSpec

class CommandContext:
    args: Dict[str, List[any]]
    message: discord.Message
    _specification: Optional["CommandSpec"]
    def __init__(self, message: discord.Message):
        self.args = defaultdict(list)  # aka multidict
        self.message = message
        self._specification = None

    @property
    def specification(self):
        if not self._specification:
            raise RuntimeError("Lateinit property \"specification\" has not been initialized")
        return self._specification

    @specification.setter
    def specification(self, value: "CommandSpec"):
        if self._specification:
            raise RuntimeError("Lateinit property \"specification\" has already been initialized")
        self._specification = value

    def put_argument(self, key, value):
        self.args[key].append(value)

    def get_one(self, key):
        return self.args[key][0]

    def get_all(self, key):
        return self.args[key]


class PermissionContext(abc.ABC):
    Default: Type["PermissionContext"]

    def __init__(self):
        pass

    @abc.abstractmethod
    def should_be_executed(self, ctx: CommandContext) -> bool:
        """
        Исполняется постфактум как команда найдена после ввода юзером. Определяет, выполнять команду или выкинуть ошибку прав
        :param ctx: Контекст
        :return: bool
        """

    @abc.abstractmethod
    def requirements(self, ctx: CommandContext) -> Union[List[discord.Permissions], str]:
        """
        Требования для запуска
        :param ctx: Контекст
        :return: Список прав Discord
        :return: Сообщение с требованиями
        """

    @abc.abstractmethod
    def should_be_found(self, ctx: CommandContext, spec: "CommandSpec") -> bool:
        """
        Должна ли команда быть найденной (влияет на help и на поиск команд после ввода пользователем)
        Имейте в виду, что ctx.specification недоступен в момент выполнения метода
        :param ctx: Контекст
        :param spec: Спецификация команды
        :return: bool
        """


class Default(PermissionContext):
    def should_be_executed(self, ctx: CommandContext) -> bool:
        return True

    def requirements(self, ctx: CommandContext) -> Union[List[discord.Permissions], str]:
        return ""

    def should_be_found(self, ctx: CommandContext, spec: CommandSpec) -> bool:
        return True


PermissionContext.Default = Default
