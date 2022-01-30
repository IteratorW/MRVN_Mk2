import logging

from api.event_handler.decorators import event_handler


@event_handler()
async def on_startup():
    logging.info("Bultin startup!")


@event_handler()
async def ready():
    logging.info("Builtin ready!")
