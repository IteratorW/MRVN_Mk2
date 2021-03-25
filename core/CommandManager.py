from typing import *

from core.command import CommandSpec, CommandExecutor

commands: List[CommandSpec] = []


def registerCommand(spec):
    if any(cmd.name == spec.name for cmd in commands): raise ValueError(
        f"Same name \"{spec.name}\" between two commands")
    commands.append(spec)


def Command(name: str, register=True):
    def decorator(executor: Type[CommandExecutor]):
        spec = CommandSpec(name=name, executor=executor())
        if register:
            registerCommand(spec)
        return spec
    return decorator
