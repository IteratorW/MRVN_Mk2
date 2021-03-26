__all__ = [
    "CommandContext",
    "PermissionContext"
]

import abc
import discord

from collections import defaultdict
from typing import Dict, List, Union, Type


class CommandContext:
    args: Dict[str, List[any]]

    def __init__(self):
        self.args = defaultdict(list)  # aka multidict

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
    def should_be_found(self, ctx: CommandContext) -> bool:
        """
        Должна ли команда быть найденной (влияет на help и на поиск команд после ввода пользователем)
        :param ctx: Контекст
        :return: bool
        """


class Default(PermissionContext):
    def should_be_executed(self, ctx: CommandContext) -> bool:
        return True

    def requirements(self, ctx: CommandContext) -> Union[List[discord.Permissions], str]:
        return ""

    def should_be_found(self, ctx: CommandContext) -> bool:
        return True


PermissionContext.Default = Default
