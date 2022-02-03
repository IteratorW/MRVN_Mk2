import importlib.util
import logging
import os
from types import ModuleType

extensions: dict[str, ModuleType] = {}

logger = logging.getLogger("Extensions")


def load_from_path(path: str):
    print(path)

    name = os.path.basename(path)
    print(name)
    spec = importlib.util.spec_from_file_location(name, f"{path}/__init__.py")
    module = importlib.util.module_from_spec(spec)

    extensions[name] = module

    spec.loader.exec_module(module)

    logger.info(f"Loaded extension {name}")


def scan_directory(path: str):
    for directory in [f for f in os.listdir(path) if os.path.isdir(f"{path}/{f}")]:
        load_from_path(f"{path}/{directory}")
