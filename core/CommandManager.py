from typing import *
from core.command import CommandSpec, CommandExecutor
import logging

logger = logging.getLogger("CommandManager")
commands: List[CommandSpec] = []


def registerCommand(spec):
    if any(cmd.name == spec.name for cmd in commands): raise ValueError(
        f"Same name \"{spec.name}\" between two commands")
    logger.info(f"Registered command \"{spec.name}\" by module \"{spec.executor.__module__}\"")
    commands.append(spec)


def Command(name: str, register=True):
    def decorator(executor: Type[CommandExecutor]):
        spec = CommandSpec(name=name, executor=executor())
        if register:
            registerCommand(spec)
        return spec
    return decorator
