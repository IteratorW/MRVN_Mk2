import logging
import time

from tortoise import Tortoise
from tortoise.exceptions import OperationalError

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.embed.style import Style
from api.translation.translatable import Translatable
from impl import runtime
from tabulate import tabulate


@runtime.bot.slash_command(description=Translatable("execute_command_sql_desc"), owners_only=True)
async def sql(ctx: MrvnCommandContext, request: ParseUntilEndsOption(str)):
    await ctx.defer()

    conn = Tortoise.get_connection("default")

    start_time = time.time_ns()

    try:
        result = await conn.execute_query(request)
    except OperationalError as ex:
        await ctx.respond_embed(Style.ERROR, ctx.format("execute_command_sql_operation_error", ex))
        return

    rows_affected = result[0]
    rows = result[1]

    if len(rows) > 0:
        columns = list(rows[0].keys())
        data = [[row[col] for col in columns] for row in rows[:15]]

    await ctx.respond(ctx.format("execute_command_sql_completed", rows_affected, (time.time_ns() - start_time) / 1_000_000) +
                      (f"\n```prolog\n{tabulate(data, headers=columns, tablefmt='rounded_outline')[:1900]}\n```"
                      if len(rows) > 0 else ""))