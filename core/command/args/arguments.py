import re
from typing import List, Dict, Optional

PATTERN = re.compile(r"\"([^\"]*)\"|--(\S+)=\"([^\"]*)\"|--(\S+)=(\S+)|--(\S+)|-(\S+)|(\S+\n?)")


class SingleArgument:
    value: str
    start: int
    end: int

    def __init__(self, value: str, start: int, end: int):
        self.value = value
        self.start = start
        self.end = end


class PreparedArguments:
    source: str
    args: List[SingleArgument]
    keys: Dict[str, "PreparedArguments"]

    def __init__(self, source: str, parse_keys: bool = True):
        self.source = source
        self.args = []
        self.keys = {}
        self._pos = -1
        for match in PATTERN.finditer(source):
            if match.group(1):
                self.append_single_arg(match, 1)
            elif match.group(2) and match.group(3) and parse_keys:
                self.process_key(match.group(2), match.group(3))
            elif match.group(4) and match.group(5) and parse_keys:
                self.process_key(match.group(4), match.group(5))
            elif match.group(6) and parse_keys:
                self.process_key(match.group(6), None)
            elif match.group(7):
                for char in match.group(7):
                    self.process_key(char, None)
            elif match.group(8):
                self.append_single_arg(match, 8)
            else:
                self.append_single_arg(match, 0)

    def append_single_arg(self, match: "re.Match", group: int):
        self.args.append(SingleArgument(match.group(group), match.start(), match.end()))

    # Здесь нужен RawArguments, что бы элемент, который будет в KeyParserElement, смог парсить переданную в ключ строку
    def process_key(self, key: str, value: Optional[str]):
        if value is None:
            self.keys.setdefault(key, PreparedArguments("true", False))
        else:
            self.keys.setdefault(key, PreparedArguments(value, False))

    def has_next(self) -> bool:
        return len(self.args) - 1 > self._pos

    def next(self) -> SingleArgument:
        if not self.has_next(): raise IndexError
        self._pos += 1
        return self.args[self._pos]

    def peek(self) -> SingleArgument:
        if not self.has_next(): raise IndexError
        return self.args[self._pos + 1]

    def current(self):
        if self._pos == -1: raise IndexError
        return self.args[self._pos]