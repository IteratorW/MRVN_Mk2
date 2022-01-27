from typing import Any

from discord import Option


class ParseUntilEndsOption(Option):
    def __init__(self, input_type: Any, /, **kwargs):
        if "default" in kwargs or "choices" in kwargs or "required" in kwargs and not kwargs["required"]:
            raise ValueError("ParseUntilEndsOption can not be optional or have choices.")

        super().__init__(input_type, **kwargs)
