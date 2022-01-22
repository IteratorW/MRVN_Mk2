import logging

from api.event_handler.decorators import event_handler
from impl import bot


@event_handler("startup")
async def on_startup():
    logging.info("Bultin startup!")


@event_handler("ready")
async def on_ready():
    logging.info("Builtin ready!")
