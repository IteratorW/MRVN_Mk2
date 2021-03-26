import logging
import sys

import core.runtime


def main():
    # А кто это блять тут обосрался? А это блять кодеры стдлибы не умеют использовать keyword аргументы, сука
    # только **kwargs и знают
    # И идея тоже блять туда же, handlers в коде описан. а в "документации" - нет
    # noinspection PyArgumentList
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("logs.txt")])
    core.runtime.start()


if __name__ == "__main__":
    main()
