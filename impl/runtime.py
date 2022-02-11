import logging

from discord import Intents
from tortoise import Tortoise

from api.event_handler import handler_manager
from api.extension import extension_manager
from api.translation import translations
from impl import env
from impl.mrvn_bot import MrvnBot

bot = MrvnBot(debug_guilds=env.debug_guilds, intents=Intents.all())
startup_done = False


async def run_tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': extension_manager.extensions_models + ["api.models"]}
    )
    await Tortoise.generate_schemas()


@bot.event
async def on_ready():
    global startup_done

    if not startup_done:
        handler_manager.post("startup")

        await run_tortoise()

        startup_done = True

    logging.info("==================")
    logging.info(
        f"Bot loaded with: "
        f"[{len(extension_manager.extensions)} EXT] "
        f"[{len(bot.unique_app_commands)} CMD] "
        f"[L: {', '.join(translations.translations.keys())}] "
        f"[{len(translations.translations[translations.FALLBACK_LANGUAGE])} TR]")
    logging.info("==================")
