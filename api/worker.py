from pathlib import Path
from time import time

from arq import cron

from api.custom_report import create_custom_report
from api.settings import TEMP_DIR

# run cleanup every 60 minutes
CLEANUP_FREQUENCY = 3600

# retain files for 4 hours
RETENTION = 14400


async def cleanup_files(ctx):
    for path in TEMP_DIR.rglob("*"):
        if path.stat().st_mtime < time() - RETENTION:
            path.unlink()


class WorkerSettings:
    job_timeout = 600  # 10 minutes
    functions = [create_custom_report]
    cron_jobs = [cron(cleanup_files, second=CLEANUP_FREQUENCY)]
