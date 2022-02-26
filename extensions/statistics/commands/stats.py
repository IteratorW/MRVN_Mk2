from api.command import categories
from api.command.command_category import CommandCategory
from api.command.context.mrvn_command_context import MrvnCommandContext
from api.translation.translatable import Translatable
from impl import runtime


stats_category = categories.add_category(CommandCategory(Translatable("statistics_stats_category_name")))
stats_group = runtime.bot.create_group(name="stats", description=Translatable("statistics_command_stats_desc"), category=stats_category)
