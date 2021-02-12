from pathlib import Path
import os

from arq.connections import RedisSettings
from dotenv import load_dotenv


load_dotenv()
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/sa-report"))
SITE_URL = os.getenv("SA_SITE_URL", "http://localhost")
MBGL_SERVER_URL = os.getenv("MBGL_SERVER_URL", "http://localhost:8002/render")
API_TOKEN = os.getenv("API_TOKEN")
API_SECRET = os.getenv("API_SECRET")
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENV")

REDIS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)
REDIS_QUEUE = "south_atlantic"

MAP_RENDER_THREADS = int(os.getenv("MAP_RENDER_THREADS", 2))
MAX_JOBS = int(os.getenv("MAX_JOBS", 2))
CUSTOM_REPORT_MAX_ACRES = int(os.getenv("CUSTOM_REPORT_MAX_ACRES", 3e6))

# retain files for 24 hours to aid troubleshooting
FILE_RETENTION = 86400

# time jobs out after 10 minutes
JOB_TIMEOUT = 600


if not TEMP_DIR.exists():
    os.makedirs(TEMP_DIR)
