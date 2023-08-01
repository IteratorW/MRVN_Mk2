import asyncio
import logging
import os
import sys

import coloredlogs as coloredlogs
import discord
from colored_traceback import colored_traceback
from tortoise import Tortoise

import impl
from api.extensions import extension_manager
from api.translation import translations, auto_translate
from impl import runtime, env

colored_traceback.add_hook(always=True)

coloredlogs.install(fmt="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s", datefmt="%H:%M:%S",
                    field_styles={"levelname": {"color": "magenta", "bright": True},
                                  'asctime': {'color': 'blue', "bright": True},
                                  "message": {"color": "white", "bright": True}})
logging.basicConfig(level=logging.INFO if not env.debug else logging.DEBUG)

if env.load_auto_translations:
    logging.info("Loading auto-translations...")

    translations.load_from_path(auto_translate.LANG_PATH)

logging.info("Loading extensions...")

# extension_manager.load_from_path("std_extension")
translations.load_from_path(f"{os.path.dirname(impl.__file__)}/lang")

for directory in env.extension_dirs:
    if not os.path.isdir(directory):
        os.mkdir(directory)

    extension_manager.scan_directory(directory)

if "auto_translate" in sys.argv:
    auto_translate.start_auto_translation()

logging.info("Running bot...")

loop = asyncio.new_event_loop()
runtime.bot.loop = loop

future = asyncio.ensure_future(runtime.bot.start(env.token), loop=loop)

try:
    loop.run_forever()
except KeyboardInterrupt:
    logging.info('Terminated.')
finally:
    loop.run_until_complete(Tortoise.close_connections())

    logging.info('Cleaning up after pycord.')
    discord.client._cleanup_loop(loop)
