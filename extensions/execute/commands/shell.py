import platform
import subprocess

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime


@runtime.bot.slash_command(description=Translatable("execute_command_shell_desc"), owners_only=True)
async def shell(ctx: MrvnCommandContext, command: ParseUntilEndsOption(str)):
    if "shutdown" in command.lower() or "restart" in command.lower():
        await ctx.respond_embed(Style.ERROR, ctx.translate("execute_command_shell_prohibited_word"))

        return

    await ctx.defer()

    encoding = "cp866" if platform.system() == "Windows" else "utf-8"

    try:
        result = subprocess.check_output(command, shell=True, timeout=5, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired:
        await ctx.respond_embed(Style.WARN, ctx.translate("execute_command_shell_executed_timeout"))
    except subprocess.CalledProcessError as ex:
        await ctx.respond_embed(Style.ERROR, ex.output.decode(encoding), ctx.translate("execute_command_shell_error"))
    else:
        await ctx.respond_embed(Style.OK, result.decode(encoding), ctx.translate("execute_command_shell_ok"))
