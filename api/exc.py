from api.command.args.arguments import PreparedArguments


class ArgumentParseException(Exception):
    def __init__(self, message: str):
        self.message = message

    @staticmethod
    def with_pointer(message: str, args: PreparedArguments):
        result_message = "%s\n```\n%s\n%s%s```" % (
            message,
            args.source.replace("`", "\\`"),
            " "*args.current().start,
            "^"*(args.current().end-args.current().start)
        )
        return ArgumentParseException(result_message)
