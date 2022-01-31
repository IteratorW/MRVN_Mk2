from discord import Intents
from tortoise import Tortoise

from api.event_handler import handler_manager
from impl import env
from impl.mrvn_bot import MrvnBot

bot = MrvnBot(description="Test", debug_guilds=env.debug_guilds, intents=Intents.all())
startup_done = False

extensions_models = []


async def run_tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': extensions_models + ["api.models"]}
    )
    await Tortoise.generate_schemas()


@bot.event
async def on_ready():
    global startup_done

    if not startup_done:
        handler_manager.post("startup")

        await run_tortoise()

        startup_done = True


