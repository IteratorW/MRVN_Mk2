from api.command.command_category import CommandCategory
from api.translation.translatable import Translatable

categories: list[CommandCategory] = []


def add_category(category: CommandCategory):
    categories.append(category)

    return category


uncategorized = add_category(CommandCategory(Translatable("mrvn_api_command_category_uncategorized"), "uncategorized"))
utility = add_category(CommandCategory(Translatable("mrvn_api_command_category_utility"), "utility"))
moderation = add_category(CommandCategory(Translatable("mrvn_api_command_category_moderation"), "moderation"))
info = add_category(CommandCategory(Translatable("mrvn_api_command_category_info"), "info"))
bot_management = add_category(CommandCategory(Translatable("mrvn_api_command_category_bot_management"), "bot_management"))
debug = add_category(CommandCategory(Translatable("mrvn_api_command_category_debug"), "debug"))
owners_only = add_category(CommandCategory(Translatable("mrvn_api_command_category_owners_only"), "owners_only"))

