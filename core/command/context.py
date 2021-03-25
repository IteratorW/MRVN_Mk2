from collections import defaultdict
from typing import Dict, List


class CommandContext:
    args: Dict[str, List[any]]
    def __init__(self):
        self.args = defaultdict(list) # aka multidict

    def put_argument(self, key, value):
        self.args[key].append(value)

    def get_one(self, key):
        return self.args[key][0]

    def get_all(self, key):
        return self.args[key]
