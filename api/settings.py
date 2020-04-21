from pathlib import Path
import os

from arq.connections import RedisSettings
from dotenv import load_dotenv


load_dotenv()
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp"))
MBGL_SERVER_URL = os.getenv("MBGL_SERVER_URL", "http://localhost:8001/render")
API_TOKEN = os.getenv("API_TOKEN")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)


REDIS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)


if not TEMP_DIR.exists():
    os.makedirs(TEMP_DIR)
