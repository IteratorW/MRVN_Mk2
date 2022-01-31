import asyncio
import importlib
import logging
import os

import coloredlogs as coloredlogs
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

        logging.info(f"Loaded extension {python_module}")

translations.load_from_package(impl.lang)

logging.info("Running bot...")

loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(runtime.bot.start(env.token))
except KeyboardInterrupt:
    loop.run_until_complete(runtime.bot.close())
    # cancel all tasks lingering
finally:
    loop.run_until_complete(Tortoise.close_connections())

    # It seems that Tortoise closes the loop by itself... Well, nobody asked.
    # loop.close()
