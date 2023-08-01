import os

openai_key = os.environ.get("mrvn_openai_key", None)
openai_model = os.environ.get("mrvn_openai_model", "gpt-3.5-turbo")
openai_base = os.environ.get("mrvn_openai_base", None)
