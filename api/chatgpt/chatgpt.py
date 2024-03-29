import os

import g4f
import openai
from openai import AsyncOpenAI

MODEL = "gpt-3.5-turbo"
PROVIDER = g4f.Provider.AItianhuSpace

use_g4f = int(os.environ.get("mrvn_use_g4f", 1))

openai_client = None

if not use_g4f:
    openai_client = AsyncOpenAI(
        api_key=os.environ.get("mrvn_openai_api_key", None),
        base_url=os.environ.get("mrvn_openai_base_url", None)
    )


class ChatGPTError(BaseException):
    def __init__(self, message: str):
        self.message = message


async def request(history: list[tuple[str | None, str | None]], system_message: str | None = None,
                  temperature: int = 0.5):
    """
    Make a request to ChatGPT.
    :param system_message: The system message (Optional)
    :param history: The conversation history - a list with tuples, where the first tuple element is the user's message,
    the second element is AI response. Either of these could be None.
    :param temperature: Temperature to be used (Optional, default is 0.5)
    :return:
    """

    messages = []

    if system_message is not None:
        messages.append({"role": "system", "content": system_message})

    for entry in history:
        for i, msg in enumerate(entry):
            if msg is None:
                continue

            messages.append({"role": "user" if i == 0 else "assistant", "content": msg})

    try:
        if use_g4f:
            return await g4f.ChatCompletion.create_async(
                model=MODEL,
                messages=messages,
                temperature=temperature
            )
        else:
            return (await openai_client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
            )).choices[0].message.content
    except Exception as ex:  # TODO find a proper exception lmao
        raise ChatGPTError(str(ex))
