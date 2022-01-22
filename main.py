import asyncio
import logging
import os
import sys

import coloredlogs as coloredlogs

from impl import bot, env

coloredlogs.install(fmt="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s", datefmt="%H:%M:%S",
                    field_styles={"levelname": {"color": "blue"}, "message": {"color": "white", "bright": True}})
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

loop = asyncio.new_event_loop()
asyncio.ensure_future(bot.run(), loop=loop)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    logging.info("Shitdown")
