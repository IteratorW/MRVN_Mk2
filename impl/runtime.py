from discord import Intents

from api.event_handler import handler_manager
from impl import env
from impl.mrvn_bot import MrvnBot

bot = MrvnBot(description="Test", debug_guilds=env.debug_guilds, intents=Intents.all())
startup_done = False


@bot.event
async def on_ready():
    global startup_done

    if not startup_done:
        handler_manager.post("startup")

        startup_done = True
