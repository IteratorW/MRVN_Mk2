import g4f

MODEL = "gpt-3.5-turbo"
PROVIDER = g4f.Provider.FreeGpt


class ChatGPTError(BaseException):
    def __init__(self, message: str):
        self.message = message


async def request(history: list[tuple[str | None, str | None]], system_message: str | None = None,
                  temperature: float | None = None):
    """
    Make a request to ChatGPT.
    :param system_message: The system message (Optional)
    :param history: The conversation history - a list with tuples, where the first tuple element is the user's message,
    the second element is AI response. Either of these could be None.
    :param temperature: Temperature to be used (Optional, default is None)
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
        return await g4f.ChatCompletion.create_async(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            provider=PROVIDER
        )
    except Exception as ex:  # TODO find a proper exception lmao
        raise ChatGPTError(str(ex))
