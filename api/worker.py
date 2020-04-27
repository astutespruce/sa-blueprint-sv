import logging
from pathlib import Path
from time import time

from arq import cron
import sentry_sdk

from api.custom_report import create_custom_report
from api.settings import (
    TEMP_DIR,
    JOB_TIMEOUT,
    FILE_RETENTION,
    SENTRY_DSN,
    LOGGING_LEVEL,
)


log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


if SENTRY_DSN:
    log.info("setting up sentry in background worker")
    sentry_sdk.init(dsn=SENTRY_DSN)


"""Cleanup user-uploaded files and generated PDFs in a background task.

Parameters
----------
ctx : arq ctx (unused)
"""


async def cleanup_files(ctx):
    for path in TEMP_DIR.rglob("*"):
        if path.stat().st_mtime < time() - FILE_RETENTION:
            path.unlink()


class WorkerSettings:
    job_timeout = JOB_TIMEOUT
    # run cleanup every 60 minutes
    cron_jobs = [cron(cleanup_files, run_at_startup=True, minute=0, second=0)]
    functions = [create_custom_report]
