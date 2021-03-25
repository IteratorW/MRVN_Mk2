import abc


class CommandContext:
    def __init__(self):
        pass

class CommandExecutor(abc.ABC):
    @abc.abstractmethod
    def execute(self, ctx: CommandContext):
        pass

    def __call__(self, ctx: CommandContext):
        return self.execute(ctx)

class CommandSpec:
    name: str
    executor: CommandExecutor

    def __init__(self, name, executor):
        self.name = name
        self.executor = executor

    class Builder:
        def __init__(self):
            self._executor = None
            self._name = None

        def name(self, name: str):
            self._name = name
            return self

        def executor(self, executor: CommandExecutor):
            self._executor = executor
            return self

        def build(self):
            return CommandSpec(self._name, self._executor)



class Message:
    content: str
    def __init__(self, content: str):
        self.content = content

