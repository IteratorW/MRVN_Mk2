from typing import Any

from discord import Option


class ParseUntilEndsOption(Option):
    def __init__(self, input_type: Any, /, **kwargs):
        super().__init__(input_type, **kwargs)
