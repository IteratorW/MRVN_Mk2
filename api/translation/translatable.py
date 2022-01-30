class Translatable(str):
    def __init__(self, key: str):
        self.key = key

    def __str__(self):
        return self.key
