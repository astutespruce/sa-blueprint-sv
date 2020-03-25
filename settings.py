import os

from dotenv import load_dotenv

load_dotenv()
MBGL_SERVER_URL = os.getenv("MBGL_SERVER_URL", "http://localhost:8001/render")
