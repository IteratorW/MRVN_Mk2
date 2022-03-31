import io
import traceback
from contextlib import redirect_stdout

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


class MyGlobals(dict):
    # noinspection PyMissingConstructor
    def __init__(self, globs, locs):
        self.globals = globs
        self.locals = locs

    def __getitem__(self, name):
        try:
            return self.locals[name]
        except KeyError:
            return self.globals[name]

    def __setitem__(self, name, value):
        self.globals[name] = value

    def __delitem__(self, name):
        del self.globals[name]


async def async_exec(code: str, globs, locs):
    d = MyGlobals(globs, locs)

    exec(
        f'async def __ex(): ' +
        ''.join(f'\n {line}' for line in code.split('\n'))
        , d)

    return await d.globals.get("__ex")()


@runtime.bot.slash_command(description=Translatable("execute_command_execute_desc"), owners_only=True)
async def execute(ctx: MrvnCommandContext, code: ParseUntilEndsOption(str)):
    if ctx.interaction is None:
        if len((splitted := ctx.message.content.split("```"))) == 3:
            code = splitted[1].rstrip()
        else:
            await ctx.respond_embed(Style.ERROR, ctx.translate("execute_command_execute_invalid_format"))

            return

    await ctx.defer()

    with io.StringIO() as buf, redirect_stdout(buf):
        # noinspection PyBroadException
        try:
            await async_exec(code, globals(), locals())

            error = False
        except Exception:
            error = True

            buf.write(ctx.translate("execute_command_exception_occurred") + "\n")
            buf.write(f"```{traceback.format_exc(limit=3)}```")
        finally:
            output = buf.getvalue()

    await ctx.respond_embed(Style.ERROR if error else Style.OK, output, title=ctx.translate(f"execute_command_execute_{'error' if error else 'ok'}"))
