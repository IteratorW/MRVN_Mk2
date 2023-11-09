import importlib.util
import logging
import os
from types import ModuleType

from api.translation import translations

extensions: dict[str, ModuleType] = {}
extensions_models: list[str] = []

logger = logging.getLogger("Extensions")


def load_from_path(path: str):
    name = path.split(".")[-1]

    module = __import__(path, fromlist=[''])

    feature_list = []

    if importlib.util.find_spec(model_path := f"{path}.models") is not None:
        extensions_models.append(model_path)

        feature_list.append("[M]")

    if os.path.isdir(lang_path := f"{os.path.dirname(module.__file__)}/lang"):
        translations.load_from_path(lang_path)

        feature_list.append("[T]")

    extensions[name] = module

    logger.info(f"Loaded extension {name} {' '.join(feature_list)}")


def scan_directory(path: str):
    for directory in [f for f in os.listdir(path) if os.path.isdir(f"{path}/{f}")]:
        if directory == "__pycache__":
            continue

        load_from_path(f"{path}.{directory}")
