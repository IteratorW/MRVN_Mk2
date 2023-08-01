import logging
import openai

from . import commands, env
from . import reply_listener

if env.openai_key is None:
    logging.getLogger("OpenAI").error("OpenAI key is not provided.")
else:
    openai.api_key = env.openai_key

if base := env.openai_base is not None:
    openai.api_base = base

