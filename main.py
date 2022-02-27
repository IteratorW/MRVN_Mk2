import asyncio
import logging
import os
import signal
import sys

import coloredlogs as coloredlogs
import discord
from colored_traceback import colored_traceback
from tortoise import Tortoise

import impl
from api.extension import extension_manager
from api.translation import translations, auto_translate
from impl import runtime, env

colored_traceback.add_hook(always=True)

coloredlogs.install(fmt="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s", datefmt="%H:%M:%S",
                    field_styles={"levelname": {"color": "yellow", "bright": True},
                                  'asctime': {'color': 'blue', "bright": True},
                                  "message": {"color": "white", "bright": True}})
logging.basicConfig(level=logging.INFO if not env.debug else logging.DEBUG)

logging.info("Loading extensions...")

extension_manager.load_from_path("std_extension")
translations.load_from_path(f"{os.path.dirname(impl.__file__)}/lang")

for directory in env.extension_dirs:
    if not os.path.isdir(directory):
        os.mkdir(directory)

    extension_manager.scan_directory(directory)

if "auto_translate" in sys.argv:
    auto_translate.start_auto_translation()

if env.load_auto_translations:
    logging.info("Loading auto-translations...")

    translations.load_from_path(auto_translate.LANG_PATH)

logging.info("Running bot...")

# All the code exists here because simply making our own loop and calling discord.Client.start() makes the client
# disconnect after some time for some reason. That's a bug on their side and all this mess will be cleaned up when
# they'll fix that.

loop = asyncio.new_event_loop()
runtime.bot.loop = loop

try:
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    loop.add_signal_handler(signal.SIGTERM, loop.stop)
except (NotImplementedError, RuntimeError):
    pass


async def runner():
    try:
        await runtime.bot.start(env.token)
    finally:
        if not runtime.bot.is_closed():
            await runtime.bot.close()


def stop_loop_on_completion(f):
    loop.stop()


future = asyncio.ensure_future(runner(), loop=loop)
future.add_done_callback(stop_loop_on_completion)
try:
    loop.run_forever()
except KeyboardInterrupt:
    logging.info('Received signal to terminate bot and event loop.')
finally:
    loop.run_until_complete(Tortoise.close_connections())

    future.remove_done_callback(stop_loop_on_completion)
    logging.info('Cleaning up tasks.')
    discord.client._cleanup_loop(loop)

if not future.cancelled():
    try:
        future.result()
    except KeyboardInterrupt:
        pass
