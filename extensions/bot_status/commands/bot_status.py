from api.command import categories
from impl import runtime

bot_status_group = runtime.bot.create_group("bot_status", owners_only=True, category=categories.owners_only)
