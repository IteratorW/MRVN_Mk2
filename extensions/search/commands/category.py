from api.command import categories
from api.command.command_category import CommandCategory
from api.translation.translatable import Translatable

search_category = categories.add_category(CommandCategory(Translatable("search_command_category_name")))
