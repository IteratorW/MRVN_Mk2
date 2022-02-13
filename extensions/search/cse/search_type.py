from enum import Enum


class SearchType(Enum):
    YOUTUBE = {"siteSearch": "youtube.com/watch"}
    GOOGLE = {}
    IMAGES = {"searchType": "image"}
