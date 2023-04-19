from api.command.mrvn_context import MrvnContext
from impl import runtime


@runtime.bot.mrvn_command()
async def test_exception(ctx: MrvnContext):
    test = 5 / 0
