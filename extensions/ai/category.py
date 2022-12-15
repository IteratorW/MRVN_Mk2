from api.command import categories
from api.command.command_category import CommandCategory
from api.translation.translatable import Translatable

ai = categories.add_category(CommandCategory(Translatable("ai_category")))
