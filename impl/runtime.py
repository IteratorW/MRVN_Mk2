import logging
import time

from discord import Intents
from tortoise import Tortoise

from api.command.context.mrvn_command_context import MrvnCommandContext
from api.event_handler import handler_manager
from api.extension import extension_manager
from api.translation import translations
from impl import env
from impl.mrvn_bot import MrvnBot

bot = MrvnBot(debug_guilds=env.debug_guilds, intents=Intents.all())
startup_done = False
start_time = 0


async def run_tortoise():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': extension_manager.extensions_models + ["api.models"]}
    )
    await Tortoise.generate_schemas()


@bot.event
async def on_ready():
    global startup_done
    global start_time

    if not startup_done:
        await run_tortoise()

        handler_manager.post("startup")

        startup_done = True

    start_time = time.time()

    logging.info("==================")
    logging.info(
        f"Bot loaded with: "
        f"[{len(extension_manager.extensions)} EXT] "
        f"[{len(bot.unique_app_commands)} CMD] "
        f"[L: {', '.join(translations.translations.keys())}] "
        f"[{len(translations.translations[translations.FALLBACK_LANGUAGE])} TR]")
    logging.info("==================")


@bot.event
async def on_application_command_completion(ctx: MrvnCommandContext):
    message = f"Executed Command /{ctx.command.qualified_name} [{'Slash' if ctx.interaction else 'Message'}] "

    if ctx.guild:
        message += f"[Guild {ctx.guild.name}] [Author {ctx.author.id} {ctx.author.name}#{ctx.author.discriminator}]"
    else:
        message += f"[DM {ctx.author.id} {ctx.author.name}#{ctx.author.discriminator}]"

    logging.info(message)
