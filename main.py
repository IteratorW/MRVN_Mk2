import asyncio
import logging
import os

import coloredlogs as coloredlogs

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

        """
        if os.path.isfile(f"{directory}/{python_module}/models.py"):
        extension_handler.extensions_models.append(f"{path}.models")

        logging.info(f"Added models for extension {python_module}")
        """

        logging.info(f"Loaded extension {python_module}")


logging.info("Running async...")

runtime.bot.run(env.token)
