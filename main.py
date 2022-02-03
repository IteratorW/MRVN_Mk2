import asyncio
import importlib
import logging
import os
import signal

import coloredlogs as coloredlogs
import discord
from tortoise import Tortoise

import impl
from api.translation import translations
from impl import runtime, env

coloredlogs.install(fmt="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s", datefmt="%H:%M:%S",
                    field_styles={"levelname": {"color": "yellow", "bright": True},
                                  'asctime': {'color': 'blue', "bright": True},
                                  "message": {"color": "white", "bright": True}})
logging.basicConfig(level=logging.INFO if not env.debug else logging.DEBUG)

logging.info("Loading extensions...")

for directory in env.extension_dirs:
    if not os.path.isdir(directory):
        os.mkdir(directory)

    for python_module in os.listdir(directory):
        path = f"{directory}.{python_module}"

        extension = getattr(__import__(path, globals(), locals()), python_module)

        if os.path.isfile(f"{directory}/{python_module}/models.py"):
            runtime.extensions_models.append(f"{path}.models")

            logging.info(f"Added models for extension {python_module}")

        try:
            lang_module = importlib.import_module(f"{path}.lang")

            translations.load_from_package(lang_module)

            logging.info(f"Loaded translations for {python_module}")
        except ImportError:
            logging.info(f"Extension {python_module} doesn't have translations.")

        runtime.extensions[python_module] = extension

        logging.info(f"Loaded extension {python_module}")

translations.load_from_package(impl.lang)

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
