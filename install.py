import os.path
import subprocess
import sys

from impl import env

"""
This script auto-installs requirements for all extensions with requirements.txt. 
Also installs requirements.txt from the project root.
"""


def install(path: str):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", path])
    except subprocess.CalledProcessError:
        print(f"Error installing requirements {path}")

        sys.exit()


print("Installing main requirements")

install("./requirements.txt")

for directory in env.extension_dirs:
    if not os.path.isdir(directory):
        continue

    for ext in os.listdir(directory):
        req_path = f"{directory}/{ext}/requirements.txt"

        if os.path.isfile(req_path):
            print(f"Installing requirements for extension {ext}")

            install(req_path)

print("Done")
