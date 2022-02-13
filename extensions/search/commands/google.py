from api.command.context.mrvn_command_context import MrvnCommandContext
from api.command.option.parse_until_ends import ParseUntilEndsOption
from api.translation.translatable import Translatable
from extensions.search.commands.category import search_category
from extensions.search.cse import cse
from extensions.search.cse.search_type import SearchType
from impl import runtime


@runtime.bot.slash_command(category=search_category, description=Translatable("search_command_google_desc"))
async def google(ctx: MrvnCommandContext, query: ParseUntilEndsOption(str)):
    await cse.search(ctx, query, SearchType.GOOGLE)
