import logging

from api.event_handler.decorators import event_handler


@event_handler("startup")
async def on_ready():
    logging.info("Beu startup!")


@event_handler("ready")
async def on_ready():
    logging.info("Beu ready!")
