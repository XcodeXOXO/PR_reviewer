# app/config.py

import os

from dotenv import load_dotenv
load_dotenv()  # loads .env
def get_env(name: str, default: str | None = None):
    return os.getenv(name, default)
