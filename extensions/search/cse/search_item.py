class SearchItem:
    def __init__(self, title: str, url: str, context_url: str, snippet: str = None):
        self.title = title
        self.url = url
        self.context_url = context_url
        self.snippet = snippet
