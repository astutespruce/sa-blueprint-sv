import logging
from time import time

import arq
from arq import cron
import sentry_sdk

from api.custom_report import create_custom_report
from api.summary_unit_report import create_summary_unit_report
from api.settings import (
    TEMP_DIR,
    JOB_TIMEOUT,
    FILE_RETENTION,
    SENTRY_DSN,
    SENTRY_ENV,
    LOGGING_LEVEL,
    REDIS,
    REDIS_QUEUE,
    MAX_JOBS,
)


log = logging.getLogger(__name__)
log.setLevel(LOGGING_LEVEL)


if SENTRY_DSN:
    log.info("setting up sentry in background worker")
    sentry_sdk.init(dsn=SENTRY_DSN, environment=SENTRY_ENV)


"""Cleanup user-uploaded files and generated PDFs in a background task.

Parameters
----------
ctx : arq ctx (unused)
"""


async def cleanup_files(ctx):
    for path in TEMP_DIR.rglob("*"):
        if path.stat().st_mtime < time() - FILE_RETENTION:
            path.unlink()


async def startup(ctx):
    ctx["redis"] = await arq.create_pool(REDIS)


async def shutdown(ctx):
    await ctx["redis"].close()


class WorkerSettings:
    redis_settings = REDIS
    job_timeout = JOB_TIMEOUT
    max_jobs = MAX_JOBS
    queue_name = REDIS_QUEUE
    # run cleanup every 60 minutes
    cron_jobs = [cron(cleanup_files, run_at_startup=True, minute=0, second=0)]
    functions = [create_custom_report, create_summary_unit_report]

    on_startup = startup
    on_shutdown = shutdown
